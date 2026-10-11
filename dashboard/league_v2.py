"""Slicer-synchronized IPL League Overview — V2 B.
All visual and numeric datasets are scoped through the same match_id selection.
"""
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from dashboard.analytics import ALL_TEAMS,TEAMS,PHASE_ORDER
from dashboard.filter_engine import (LeagueSelection,select_matches,scoped,season_evolution,
    phase_evolution,player_leaders,league_kpis,evidence_notes)
from dashboard.design import hero,kpi,section,analyst
from dashboard.data import load
from dashboard.chart_ui import render_chart

C='#EFC26E';B='#72B5F2';G='#4ADEB1';P='#B6A3ED';

def chart(fig,height=355):
    fig.update_layout(template='plotly_dark',height=height,paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',font=dict(family='Arial, sans-serif',color='#CBDAE9',size=12),
        title_font=dict(size=16,color='#EDF4FD'),margin=dict(l=10,r=12,t=57,b=20),
        xaxis=dict(showgrid=False,zeroline=False),yaxis=dict(gridcolor='rgba(155,190,230,.10)',zeroline=False),
        legend=dict(orientation='h',y=1.08,x=0,title_text=''))
    render_chart(fig,key='league_'+str(fig.layout.title.text or 'untitled').lower().replace(' ','_'))

def empty(text='No records for this filter combination.'):
    st.info(text)

def fmt(v,suffix='',decimals=1):return f'{v:,.{decimals}f}{suffix}' if pd.notna(v) else '—'

def render():
    from dashboard.views import table
    allm=table('matches');tm=table('team_matches')
    with st.sidebar:
        st.markdown('#### 🎛️ LEAGUE FILTERS')
        st.caption('All charts, KPIs, insights, rankings and exports use the same match selection.')
        mode=st.radio('Season view',['All seasons','One season','Custom range'],index=0,key='v2_league_mode',horizontal=False)
        if mode=='One season':
            season=st.selectbox('Season',sorted(allm.season_year.unique(),reverse=True),key='v2_league_season')
            years=(int(season),int(season))
        elif mode=='Custom range':
            years=st.slider('Season range',int(allm.season_year.min()),int(allm.season_year.max()),
                (int(allm.season_year.min()),int(allm.season_year.max())),key='v2_league_range')
        else:years=(int(allm.season_year.min()),int(allm.season_year.max()))
        team=st.selectbox('Franchise / participating team',['All teams']+sorted(set(tm.team_code)-{''}),
            format_func=lambda x: ('Entire league' if x=='All teams' else f'{x} · {ALL_TEAMS.get(x,x)}'),key='v2_league_team')
        venues=['All venues']+sorted(allm.venue_group.dropna().unique())
        venue=st.selectbox('Venue',venues,key='v2_league_venue')
        stage=st.selectbox('Match stage',['All stages']+sorted(allm.match_type.dropna().unique()),key='v2_league_stage')
        toss=st.selectbox('Toss choice',['Any toss decision','bat','field'],format_func=lambda t:{'bat':'Choose to bat','field':'Choose to field'}.get(t,t),key='v2_league_toss')
        role='Either innings role';result='Any result'
        if team!='All teams':
            role=st.selectbox('Selected team role',['Either innings role','Batted first','Chased'],key='v2_league_role')
            result=st.selectbox('Selected team outcome',['Any result','Won','Lost','No result'],key='v2_league_result')
        st.divider()
        st.caption('Team filters select matches featuring that team. Unless marked otherwise, league run totals include **both teams** in those matches.')
    filt=LeagueSelection(years[0],years[1],team,venue,stage,toss,role,result)
    m=select_matches(allm,tm,filt)
    inn=scoped(table('innings'),m)
    phase=scoped(table('phase_match'),m)
    bat=scoped(table('bat_match'),m)
    bowl=scoped(table('bowl_match'),m)
    t=scoped(tm,m)
    k=league_kpis(m,inn,phase)

    active=[f'{years[0]}' if years[0]==years[1] else f'{years[0]}–{years[1]}']
    for name,value,whole in [('Team',team,'All teams'),('Venue',venue,'All venues'),('Stage',stage,'All stages'),('Toss',toss,'Any toss decision'),('Role',role,'Either innings role'),('Result',result,'Any result')]:
        if value!=whole:active.append(f'{name}: {value}')
    hero('League Intelligence','Analyze nineteen IPL seasons through a single evidence-linked filter system. Every figure, chart and conclusion updates with your selection.','THE LEAGUE / DEEP DIVE',' · '.join(active[:3]))
    st.caption('**Active scope:** '+'  |  '.join(active) +f'  ·  **{len(m):,} matches**')
    if m.empty:
        st.warning('No matches satisfy this combination. Change a filter in the sidebar to continue.')
        return
    cards=[('MATCHES',f'{k["matches"]:,}','Unique match IDs'),
           ('TOTAL RUNS',f'{k["runs"]:,}','Both teams · all regulation innings'),
           ('TOTAL WICKETS',f'{k["wickets"]:,}','Recorded wickets lost'),
           ('AVG 1ST INNINGS',fmt(k['average_first_innings']),'≥100 legal balls · no DLS'),
           ('CHASE WIN RATE',fmt(k['chase_win_pct'],'%'),'Decided non-DLS · n='+str(k['chase_sample'])),
           ('VENUES',f'{k["venues"]:,}','Distinct normalized grounds'),
           ('FOURS / SIXES',f'{k["fours"]:,} / {k["sixes"]:,}','Regulation innings'),
           ('SCORING RATE',fmt(k['run_rate']),'Runs per 6 legal balls'),
           ('TOSS-WINNER WIN %',fmt(k['toss_win_pct'],'%'),'Decided matches · n='+str(k['toss_sample'])),
           ('BOUNDARY RATE',fmt(k['boundary_per_100_balls']),'4s+6s per 100 legal balls'),
           ('SUPER OVERS',str(k['super_overs']),'Final winner recovered'),
           ('NO FINAL RESULT',str(k['unresolved']),'Excluded from win-rate samples')]
    for start in range(0,len(cards),4):
        cols=st.columns(4,gap='small')
        for c, (label,val,note) in zip(cols,cards[start:start+4]):
            with c:kpi(label,val,note)

    with st.expander('READ ME · Score and filter definitions',expanded=False):
        st.markdown('**Filters select unique matches first**; every source table is joined using the exact selected match IDs. All innings and both sides contribute to league totals. If a franchise is selected, the match universe includes that franchise; by default the charts remain *league activity within its games*. Player leaderboards then show **only that franchise’s own players**. Win percentages use decisive matches only; DLS is additionally excluded for the chase win KPI. First-innings means use ≥100 legal balls and exclude DLS. This is not a model training feature table.')
    analyst(evidence_notes(m,inn,phase,k))

    tabs=st.tabs(['📈 Season pulse','🏏 Scoring DNA','🎯 Toss & chase','🏟️ Venue intelligence','🏅 Player leaders','🏆 Champions & records'])
    seasons=season_evolution(m,inn)
    with tabs[0]:
        section('How the league evolved','Season graphs are regenerated from the selected matches—not from the all-time season summary.')
        a,b=st.columns(2,gap='medium')
        with a:
            f=px.bar(seasons,x='season_year',y='matches',title='Number of IPL Matches Played by Season (Current Filters)',color_discrete_sequence=[B]);chart(f)
        with b:
            eligible=seasons.dropna(subset=['mean_first_innings'])
            if len(eligible):
                f=px.line(eligible,x='season_year',y='mean_first_innings',markers=True,title='Average First-Innings Runs by IPL Season (≥100 Balls, No DLS)',color_discrete_sequence=[C]);f.update_traces(line_width=3,marker_size=7);chart(f)
            else:empty('No first innings meet the ≥100-ball non-DLS qualification.')
        s=t[t.is_decided.astype(bool)&t.team_code.isin(TEAMS)]
        if not s.empty:
            team_rate=s.groupby('team_code').agg(wins=('won','sum'),matches=('match_id','nunique')).reset_index()
            team_rate['win_pct']=100*team_rate.wins/team_rate.matches
            f=px.bar(team_rate.sort_values('win_pct'),x='win_pct',y='team_code',orientation='h',text='matches',title='Decided-Match Win Rate by Franchise (Selected Matches)',color_discrete_sequence=[C]);chart(f,395)
            st.caption('Different franchises have different starting seasons; the bars are descriptive and may overlap when the selected team participated against other current franchises.')
    with tabs[1]:
        section('Run construction and over-by-over identity')
        eligible=inn[(inn.inning==1)&(~inn.is_dls.astype(bool))&(inn.legal_balls>=100)]
        a,b=st.columns(2)
        with a:
            if len(eligible):chart(px.histogram(eligible,x='runs',nbins=24,title='Distribution of First-Innings Scores (≥100 Balls, No DLS)',color_discrete_sequence=[C]))
            else:empty('No qualifying first innings.')
        with b:
            p=phase_evolution(phase)
            if len(p):chart(px.bar(p,x='phase',y='run_rate',text_auto='.2f',title='Runs Scored per Over: Powerplay, Middle and Death Overs',color_discrete_sequence=[B]))
            else:empty('No regulation delivery records.')
        a,b=st.columns(2)
        with a:
            count=pd.DataFrame({'type':['Fours','Sixes'],'count':[k['fours'],k['sixes']]})
            if count['count'].sum():chart(px.pie(count,values='count',names='type',hole=.68,title='Boundary Breakdown: Fours vs Sixes (Batter Runs Only)',color_discrete_sequence=[B,C]))
        with b:
            if len(p):chart(px.bar(p,x='phase',y='wickets',title='Wickets Lost During Powerplay, Middle and Death Overs',color_discrete_sequence=[P]))
        st.caption('Phase rates use recorded legal deliveries; batting boundaries count batter-run fours and sixes, not boundary extras.')
    with tabs[2]:
        section('Toss decisions and chase outcomes','Percentages describe association, not a toss-caused match advantage.')
        a,b=st.columns(2)
        dec=m[m.is_decided.astype(bool)].copy()
        with a:
            vc=m.groupby('toss_decision').agg(matches=('match_id','size')).reset_index()
            if len(vc):chart(px.bar(vc,x='toss_decision',y='matches',title='Toss-Winning Teams: Decision to Bat or Field',color_discrete_sequence=[C]))
        with b:
            if len(dec):
                dec['toss_winner_won']=dec.toss_winner_code==dec.winner_final_code
                g=dec.groupby('toss_decision').agg(matches=('match_id','size'),toss_wins=('toss_winner_won','sum')).reset_index();g['pct']=100*g.toss_wins/g.matches
                chart(px.bar(g,x='toss_decision',y='pct',text_auto='.1f',title='Match Win Rate for Toss-Winning Teams by Decision (%)',color_discrete_sequence=[G]))
        st.caption(f'Chase-win KPI: {k["chase_sample"]} decisive, non-DLS matches with a recorded 2nd innings. Toss win KPI: {k["toss_sample"]} decided fixtures. Different eligibility sets are intentional and labelled.')
    with tabs[3]:
        section('Venue intelligence','Compare ground usage and scoring only within the filtered match set.')
        g=m.groupby('venue_group').agg(matches=('match_id','size')).reset_index().sort_values('matches',ascending=False)
        if len(g):chart(px.bar(g.head(15).sort_values('matches'),x='matches',y='venue_group',orientation='h',title='Number of IPL Matches at Each Venue (Selected Filters)',color_discrete_sequence=[B]),440)
        kval=inn[(inn.inning==1)&(~inn.is_dls.astype(bool))&(inn.legal_balls>=100)]
        byvenue=kval.groupby('venue_group').agg(eligible_innings=('runs','size'),avg_total=('runs','mean')).reset_index()
        byvenue=byvenue[byvenue.eligible_innings>=5].sort_values('avg_total',ascending=False)
        if len(byvenue):
            chart(px.bar(byvenue.head(15),x='venue_group',y='avg_total',hover_data=['eligible_innings'],title='Average First-Innings Score by Venue (At Least 5 Eligible Innings)',color_discrete_sequence=[C]),420)
            st.caption('Ground comparisons are not adjusted for era, team strength or toss. No inference of causality or home advantage.')
        else:empty('Fewer than five eligible first innings per venue in this selection.')
    with tabs[4]:
        section('Players driving the numbers','Rankings use match-level contributions from the exact filtered fixtures.')
        limit_team=team if team!='All teams' else None
        hitters=player_leaders(bat,m,limit_team,'bat',12)
        wicket=player_leaders(bowl,m,limit_team,'bowl',12)
        st.caption('Leaderboard scope: '+('Only '+team+' players in the filtered matches.' if limit_team else 'All players from both sides in the filtered matches.'))
        a,b=st.columns(2)
        with a:
            st.markdown('#### Leading run scorers')
            if len(hitters):
                st.dataframe(hitters[['player_name','matches','runs','balls','strike_rate','fours','sixes']].round(2),hide_index=True,use_container_width=True)
                chart(px.bar(hitters.sort_values('runs'),x='runs',y='player_name',orientation='h',title='Highest Run Scorers in Selected IPL Matches',color_discrete_sequence=[C]),390)
            else:empty('No batters were recorded for these matches.')
        with b:
            st.markdown('#### Leading wicket takers')
            if len(wicket):
                st.dataframe(wicket[['player_name','matches','wickets','balls','economy']].round(2),hide_index=True,use_container_width=True)
                chart(px.bar(wicket.sort_values('wickets'),x='wickets',y='player_name',orientation='h',title='Highest Wicket Takers in Selected IPL Matches',color_discrete_sequence=[B]),390)
            else:empty('No bowler records were found for these matches.')
        st.caption('Bowler wickets exclude run-outs and other non-credited dismissals. Player names are grouped by stable Cricsheet ID.')
    with tabs[5]:
        section('Finals, titles and signature innings','Honor records here reflect only verified match outcomes and the current filter selection.')
        finals=m[m.match_type.eq('Final')].sort_values('season_year')
        if len(finals):
            fin=finals[['season_year','team1_code','team2_code','winner_final_code','venue_group']].rename(columns={'season_year':'Season','team1_code':'Finalist A','team2_code':'Finalist B','winner_final_code':'Champion','venue_group':'Ground'})
            st.dataframe(fin,hide_index=True,use_container_width=True)
            champs=finals.winner_final_code.value_counts().rename_axis('team').reset_index(name='titles')
            chart(px.bar(champs,x='team',y='titles',title='Championships Won in IPL Final Matches Within Current Filters',color_discrete_sequence=[C]),320)
        else:empty('No IPL finals match is in this filtered selection.')
        top=inn.sort_values('runs',ascending=False).head(10)
        if len(top):
            st.markdown('#### Highest recorded team innings in this selection')
            st.dataframe(top[['season_year','batting_team_code','bowling_team_code','runs','wickets','legal_balls','venue_group']].rename(columns={'season_year':'Season','batting_team_code':'Batting side','bowling_team_code':'Opponent','runs':'Runs','wickets':'Wickets','legal_balls':'Balls','venue_group':'Ground'}),hide_index=True,use_container_width=True)
        st.caption('Trophy totals on this page are based on the selected IPL final match records, not an unsourced static honors list.')
    st.divider()
    st.markdown('### EXPORT · YOUR CURRENT SELECTION')
    a,b,c=st.columns(3)
    with a:st.download_button('↓ Filtered matches',m.to_csv(index=False).encode(),file_name='ipl_v2_filtered_matches.csv',mime='text/csv',use_container_width=True)
    with b:st.download_button('↓ Filtered innings',inn.to_csv(index=False).encode(),file_name='ipl_v2_filtered_innings.csv',mime='text/csv',use_container_width=True)
    with c:st.download_button('↓ Match-level phases',phase.to_csv(index=False).encode(),file_name='ipl_v2_filtered_phases.csv',mime='text/csv',use_container_width=True)
    st.caption('Source: your Cricsheet-derived IPL database. Dates and records reflect supplied 2008–2026 coverage. No web or live match feed is used.')
