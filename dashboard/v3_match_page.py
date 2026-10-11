"""Premium IPL Match Replay & Rivalry Studio, 2008-2026."""
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from dashboard.analytics import TEAMS
from dashboard.design import hero,kpi,section
from dashboard.chart_ui import render_chart
from dashboard.v3_match_engine import (match_index,match_deliveries,innings_summary,over_summary,wicket_events,
    runs_between_wickets,descriptive_turning_points,rivalry_table,rivalry_metrics)

@st.cache_data(show_spinner=False)
def _all_matches():return match_index()

@st.cache_data(show_spinner=False,max_entries=24)
def _match(mid,super_over):return match_deliveries(mid,super_over)

def _style(fig,height=380):
    fig.update_layout(template='plotly_dark',paper_bgcolor='rgba(0,0,0,0)',plot_bgcolor='rgba(0,0,0,0)',height=height,
       font=dict(color='#E5EFFD'),margin=dict(l=35,r=15,t=60,b=35),hovermode='x unified')
    return fig

def _match_selector(matches):
    c1,c2,c3=st.columns([1,1,2])
    years=sorted(matches.season_year.dropna().astype(int).unique().tolist(),reverse=True)
    year=c1.selectbox('IPL season',years,key='v3_replay_season')
    team=c2.selectbox('Franchise', ['ALL']+[x for x in TEAMS],key='v3_replay_team')
    s=matches[matches.season_year==year]
    if team!='ALL':s=s[(s.team1_code==team)|(s.team2_code==team)]
    if s.empty:return None
    mids=s.match_id.astype(int).tolist()
    opts={int(r.match_id):f"{str(r.match_date)[:10]} · {r.team1_code} vs {r.team2_code} · {r.venue_group if pd.notna(r.venue_group) else r.venue} · #{int(r.match_id)}" for r in s.itertuples()}
    mid=c3.selectbox('Historical match',mids,format_func=lambda x:opts[x],key='v3_replay_match')
    return s[s.match_id==mid].iloc[0]

def match_replay():
    allmatches=_all_matches()
    m=_match_selector(allmatches)
    if m is None:st.info('No matches found for this team and season.');return
    include_super=st.toggle('Include Super Over deliveries in the event tables (kept separate from regulation statistics)',False,key='v3_super')
    d=_match(int(m.match_id),bool(include_super))
    regulation=d[~d.super_over.fillna(False).astype(bool)].copy()
    summary=innings_summary(regulation)
    st.markdown(f'### {m.team1_code} vs {m.team2_code} — {str(m.match_date)[:10]}')
    st.caption(f'Ground: {m.venue} · Stage: {m.match_type} · Recorded winner: {m.winner_final_code if pd.notna(m.winner_final_code) else "Not resolved"} · Match ID: {int(m.match_id)}')
    if m.is_dls:st.warning('DLS-affected match: target/overs and comparisons may follow revised innings conditions.')
    if len(d)==0:st.warning('No delivery records found.');return
    mx=len(regulation)
    consumed=st.slider('Replay: deliveries revealed from the recorded match',min_value=0,max_value=mx,value=mx,step=1,key='v3_replay_slider')
    upto=regulation.iloc[:consumed]
    partial=innings_summary(upto)
    summap={int(r.inning):r for r in partial.itertuples()}
    cols=st.columns(4)
    for i,(label,val,note) in enumerate([
        ('Match Deliveries Revealed',f'{consumed:,} / {mx:,}','Includes legal balls and extras'),
        ('First Innings',f"{summap[1].runs}/{summap[1].wickets}" if 1 in summap else '0/0','Runs / wickets'),
        ('Second Innings',f"{summap[2].runs}/{summap[2].wickets}" if 2 in summap else '0/0','Runs / wickets'),
        ('Recorded Match Winner',str(m.winner_final_code) if pd.notna(m.winner_final_code) else 'Unresolved','Known retrospective match result')]):
        with cols[i]:kpi(label,val,note)
    tabs=st.tabs(['📈 Score Replay','🎯 Over-by-Over Analysis','🔥 Wickets & Scoring Bursts','⚔️ Innings Comparison','📜 Delivery Evidence'])
    with tabs[0]:
        if upto.empty:st.info('Move the slider to reveal the score progression.')
        else:
            fig=go.Figure()
            for inning,g in upto.groupby('inning'):
                name=f"Innings {inning} · {g.batting_team_code.iloc[0]}"
                fig.add_trace(go.Scatter(x=g.over_elapsed,y=g.cumulative_runs,mode='lines',name=name,line=dict(width=3),
                    hovertemplate='%{x:.2f} overs · %{y} runs<extra>'+name+'</extra>'))
                w=g[g.wickets_at_ball>0]
                if not w.empty:
                    fig.add_trace(go.Scatter(x=w.over_elapsed,y=w.cumulative_runs,mode='markers',name=f'Innings {inning}: Wickets',marker=dict(size=9,symbol='x'),
                      hovertemplate='Wicket at %{x:.2f} overs · Score %{y}<extra></extra>'))
            fig.update_layout(title='Innings Score Progression by Legal Overs Completed',xaxis_title='Overs completed',yaxis_title='Cumulative runs')
            render_chart(_style(fig,420),key='v3_score_progression',title='Innings Score Progression by Legal Overs Completed',context='Wides and no-balls add runs but not legal balls. Wicket markers indicate recorded dismissal events.')
    with tabs[1]:
        overs=over_summary(upto)
        if len(overs):
            fig=px.bar(overs,x='over_number',y='runs',color='batting_team_code',barmode='group',title='Runs Scored in Each Over by Innings',
                labels={'over_number':'Over number','runs':'Runs scored','batting_team_code':'Batting team'})
            render_chart(_style(fig),key='v3_over_runs',title='Runs Scored in Each Over by Innings')
            fig2=px.line(overs,x='over_number',y='runs',color='batting_team_code',markers=True,title='Runs Scored in Each Over: Innings Comparison',
                labels={'over_number':'Over number','runs':'Runs per over','batting_team_code':'Team'})
            render_chart(_style(fig2),key='v3_over_rr',title='Runs Scored in Each Over: Innings Comparison',context='Values show runs in each recorded over, not a projected run rate. The current over may be incomplete if the replay slider is partway through it.')
    with tabs[2]:
        wk=wicket_events(upto)
        if not wk.empty:
            st.dataframe(wk.rename(columns={'over_elapsed':'Overs completed','cumulative_runs':'Team runs','bowler':'Bowler','wickets_at_ball':'Wickets on delivery'}),hide_index=True,use_container_width=True)
            w_overs=over_summary(upto)
            fig=px.bar(w_overs,x='over_number',y='wickets',color='batting_team_code',barmode='group',title='Wickets Lost by Over and Batting Team')
            render_chart(_style(fig),key='v3_wickets_over',title='Wickets Lost by Over and Batting Team')
        seg=runs_between_wickets(upto)
        if not seg.empty:
            fig=px.bar(seg,x='segment',y='runs_between_wickets',color='inning',barmode='group',title='Runs Between Consecutive Wickets',
              labels={'runs_between_wickets':'Runs since previous wicket','segment':'Wicket-to-wicket segment'})
            render_chart(_style(fig),key='v3_segments',title='Runs Between Consecutive Wickets')
            st.caption('These are wicket-to-wicket run segments, not verified two-batter partnerships.')
    with tabs[3]:
        if len(summary):
            st.dataframe(summary.rename(columns={'runs':'Total Runs','wickets':'Wickets Lost','legal_balls':'Legal Balls Bowled','fours':'Fours','sixes':'Sixes'}),hide_index=True,use_container_width=True)
            fig=px.bar(summary,x='batting_team_code',y='runs',title='Runs Scored by Each Batting Team',labels={'runs':'Total runs scored','batting_team_code':'Batting team'})
            render_chart(_style(fig),key='v3_innings_runs',title='Runs Scored by Each Batting Team')
            fig=px.bar(summary,x='batting_team_code',y='wickets',title='Wickets Lost by Each Batting Team',labels={'wickets':'Wickets lost','batting_team_code':'Batting team'})
            render_chart(_style(fig),key='v3_innings_wickets',title='Wickets Lost by Each Batting Team')
        st.markdown('#### Observed high-impact overs (descriptive)')
        for note in descriptive_turning_points(upto):st.markdown('- '+note)
        st.caption('“High impact” here means high runs or wickets within an over, not a causal or ML-derived change in winning probability.')
    with tabs[4]:
        preview=upto[['inning','batting_team_code','over_index','ball_in_over','batter','bowler','batsman_runs','extra_runs','total_runs','wickets_count','cumulative_runs','cumulative_wickets']]
        st.dataframe(preview.tail(300),hide_index=True,use_container_width=True)
        st.download_button('Download revealed deliveries as CSV',data=preview.to_csv(index=False),file_name=f'ipl_match_{int(m.match_id)}_replay.csv',mime='text/csv',key='v3_delivery_export')
        if include_super and d.super_over.fillna(False).astype(bool).any():
            st.markdown('### Separate Super Over events')
            sd=d[d.super_over.fillna(False).astype(bool)]
            st.dataframe(sd[['inning','batting_team_code','over_index','ball_in_over','total_runs','wickets_count']],hide_index=True,use_container_width=True)


def rivalry_studio():
    section('Historical Head-to-Head Intelligence','Compare two franchises across the same IPL seasons; no simulated results.')
    c1,c2,c3=st.columns(3)
    team_a=c1.selectbox('Franchise A',list(TEAMS),index=0,key='v3_riv_a')
    team_b=c2.selectbox('Franchise B',[x for x in TEAMS if x!=team_a],index=0,key='v3_riv_b')
    period=c3.slider('Seasons',2008,2026,(2008,2026),key='v3_riv_years')
    d=rivalry_table(team_a,team_b,period)
    met=rivalry_metrics(d,team_a,team_b)
    cols=st.columns(4)
    for c,(label,val,note) in zip(cols,[('Total Head-to-Head Games',met['matches'],'Selected seasons'),(f'{team_a} Wins',met['wins_a'],'Decided results'),(f'{team_b} Wins',met['wins_b'],'Decided results'),('Undecided Matches',met['unresolved'],'No confirmed winning side')]):
        with c:kpi(label,val,note)
    if not len(d):st.info('No head-to-head matches in this selection.');return
    st.caption('Historical franchise aliases are mapped into present-day identities where appropriate; discontinued franchises do not transfer to successor brands.')
    winners=d[d.winner_final_code.isin([team_a,team_b])].copy()
    if len(winners):
        r=winners.groupby(['season_year','winner_final_code']).size().reset_index(name='wins')
        fig=px.bar(r,x='season_year',y='wins',color='winner_final_code',barmode='group',title=f'{team_a} vs {team_b}: Match Wins by IPL Season',
           labels={'season_year':'IPL season','wins':'Match wins','winner_final_code':'Winner'})
        render_chart(_style(fig),key='v3_rivalry_wins',title=f'{team_a} vs {team_b}: Match Wins by IPL Season')
    venues=d.groupby('venue_group',dropna=False).agg(matches=('match_id','count'),wins_a=('winner_final_code',lambda x:int((x==team_a).sum())),wins_b=('winner_final_code',lambda x:int((x==team_b).sum()))).reset_index()
    venues=venues[venues.matches>=1].sort_values('matches',ascending=False).head(15)
    if len(venues):
        venue_long=venues.rename(columns={'wins_a':team_a,'wins_b':team_b}).melt(id_vars=['venue_group','matches'],value_vars=[team_a,team_b],var_name='Winner',value_name='Wins')
        f=px.bar(venue_long,x='venue_group',y='Wins',color='Winner',barmode='group',title=f'{team_a} vs {team_b}: Head-to-Head Wins by Ground',
          labels={'venue_group':'Ground','Wins':'Match wins'})
        render_chart(_style(f,430),key='v3_rivalry_venues',title=f'{team_a} vs {team_b}: Head-to-Head Wins by Ground')
    st.dataframe(d[['match_date','season_year','match_type','venue','winner_final_code','match_id']].rename(columns={'match_date':'Match date','season_year':'Season','match_type':'Stage','venue':'Venue','winner_final_code':'Winner','match_id':'Cricsheet match ID'}),hide_index=True,use_container_width=True)
    st.download_button('Download head-to-head match records',data=d.to_csv(index=False),file_name=f'IPL_{team_a}_vs_{team_b}_H2H.csv',mime='text/csv',key='v3_h2h_download')
    st.caption('Match counts and venue splits are descriptive. Differences may reflect changing squads, ground conditions and era effects.')


def render():
    hero('Match Replay & Rivalry Intelligence','Relive documented IPL matches ball by ball, inspect wicket and scoring bursts, and compare real head-to-head history.','V3 / MATCH EXPLORER','2008–2026')
    tabs=st.tabs(['🏟️ Historical Match Replay','⚔️ Rivalry & Venue Analysis','📚 Interpretation & Sources'])
    with tabs[0]:match_replay()
    with tabs[1]:rivalry_studio()
    with tabs[2]:
        st.markdown('**Primary source:** Cricsheet IPL JSON records, preserved in `data/source/ipl_json.zip`. Score progression and over analysis derive from the project’s own `data/raw/deliveries.csv.gz`.')
        st.markdown('**The replay is retrospective.** The score slider reveals only already recorded events. Turning-point descriptions identify run bursts and wicket overs, not learned win-probability effects.')
        st.markdown('**Super Overs:** excluded from regulation innings analysis; optionally shown as separate events. **DLS:** revised targets may not correspond to ordinary 20-over comparisons. **Match IDs:** stable Cricsheet IDs.')
        st.markdown('**Franchise eras:** Deccan Chargers and Sunrisers Hyderabad remain separate historical identities.')
