"""V2-F premium Player Intelligence Lab — all visuals use titled fullscreen chart UI."""
from __future__ import annotations
import math
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from dashboard.data import ROOT
from dashboard.analytics import TEAMS,ALL_TEAMS
from dashboard.design import hero,inject_theme,kpi,section,palette
from dashboard.chart_ui import render_chart
from dashboard.player_intelligence import (PHASES,player_filter,summary,seasons,by_category,
    phase_breakdown,matchup_scope,matchup_leaders,sample_note)

@st.cache_data(show_spinner=False)
def data_marts():
    base=ROOT/'data'/'analytics'
    return {k:pd.read_csv(base/f'{v}.csv.gz',low_memory=False) for k,v in {
        'player':'player_match_intelligence','bat_phase':'player_batting_phase_match',
        'bowl_phase':'player_bowling_phase_match','matchup':'player_matchup_match'}.items()}

@st.cache_data(show_spinner=False)
def names_map():
    r=pd.read_csv(ROOT/'data/analytics/player_registry_v2f.csv',dtype={'player_id':'string'})
    return dict(zip(r.player_id.astype(str),r.canonical_name.astype(str)))


def _display_number(n,dec=1,suffix=''):
    return '—' if n is None or pd.isna(n) else f'{n:,.{dec}f}{suffix}'


def _kpis(stat):
    blocks=[('Recorded IPL Appearances',f"{stat['matches']:,}",'Match participant; includes possible Impact Players'),
        ('Batting Innings',f"{stat['innings']:,}",'Innings with recorded batting participation'),
        ('Runs Scored',f"{stat['runs']:,}",'Batter runs; excludes extras and Super Overs'),
        ('Batting Average',_display_number(stat['bat_average'],2),'Runs divided by batting dismissals'),
        ('Batting Strike Rate',_display_number(stat['strike_rate'],1),'Batter runs per 100 balls faced'),
        ('Highest Individual Score',f"{stat['highest']:,}",'Highest in the selected match sample'),
        ('50s / 100s',f"{stat['fifties']} / {stat['hundreds']}",'50–99 / 100+ in an innings'),
        ('Fours / Sixes',f"{stat['fours']} / {stat['sixes']}",'Batter hit boundaries'),
        ('Bowling Innings',f"{stat['bowl_innings']:,}",'Innings in which bowled'),
        ('Credited Wickets',f"{stat['wickets']:,}",'Dismissals credited to the bowler'),
        ('Bowling Economy Rate',_display_number(stat['economy'],2),'Runs conceded per six legal deliveries'),
        ('Player-of-the-Match Awards',f"{stat['pom']:,}",'Verified Cricsheet award entries'),
        ('Innings Not Out',f"{stat['not_outs']:,}",'Batting innings without dismissal'),
        ('Recorded Team Wins',f"{stat['won']:,}",'Wins in matched appearances'),
        ('Team Win Rate',_display_number(stat['win_rate'],1,'%'),'Only decided games containing the player'),
        ('Franchises Represented',f"{stat['team_count']:,}",'Within current player filters')]
    for offset in range(0,len(blocks),4):
        cols=st.columns(4,gap='small')
        for col,(label,val,description) in zip(cols,blocks[offset:offset+4]):
            with col:kpi(label,val,description)


def _chart(fig,key,note=None):
    if fig is None or not len(fig.data):
        st.info('Not enough observations to build this chart under the current slicers.')
        return
    fig.update_layout(template='plotly_dark',height=385,paper_bgcolor='rgba(0,0,0,0)',
      plot_bgcolor='rgba(0,0,0,0)',font=dict(color='#EAF2FC'),margin=dict(l=30,r=12,t=60,b=53),
      legend=dict(orientation='h',y=-.22,title_text=''),transition=dict(duration=220),
      hoverlabel=dict(bgcolor='#16283E'))
    fig.update_xaxes(gridcolor='rgba(170,193,220,.12)',zeroline=False)
    fig.update_yaxes(gridcolor='rgba(170,193,220,.12)',zeroline=False)
    render_chart(fig,key='v2f_'+key,context=note)


def _cards_scope(player_rows):
    if player_rows.empty:return
    r=player_rows.sort_values('match_date')
    st.caption(f"Selected sample: {len(r)} recorded matches · {r.match_date.iloc[0]} to {r.match_date.iloc[-1]} · {r.team_code.nunique()} team(s). All figures on this page respect the same match filters, except separately labelled all-time history.")
    note=sample_note(r)
    if note:st.warning(note)


def _season_tab(x,name,accent):
    d=seasons(x)
    if d.empty:return st.info('No season statistics for these filters.')
    section('SEASON-BY-SEASON PERFORMANCE','Runs and wickets reflect selected matches only, not full-season totals unless the entire season is selected.')
    l,r=st.columns(2)
    with l:
        f=px.area(d,x='season_year',y='bat_runs',markers=True,title=f'{name}: Runs Scored by IPL Season',
             labels={'season_year':'IPL season','bat_runs':'Batter runs'},color_discrete_sequence=[accent])
        _chart(f,'season_runs')
    with r:
        f=px.bar(d,x='season_year',y='bowl_wickets',title=f'{name}: Credited Wickets by IPL Season',
             labels={'season_year':'IPL season','bowl_wickets':'Bowling wickets'},color_discrete_sequence=[accent])
        _chart(f,'season_wickets')
    l,r=st.columns(2)
    with l:
        b=d[d.bat_balls>=30]
        if len(b):
            f=px.line(b,x='season_year',y='strike_rate',markers=True,title=f'{name}: Batting Strike Rate by Season (30+ Balls)',
                 labels={'season_year':'IPL season','strike_rate':'Runs per 100 balls'},color_discrete_sequence=['#76D3F8'])
            _chart(f,'season_sr','Season strike rate = total batter runs × 100 / total balls faced; seasons with fewer than 30 selected balls are hidden.')
        else:st.info('At least 30 selected balls are needed to show seasonal strike rate.')
    with r:
        b=d[d.bowl_balls>=30]
        if len(b):
            f=px.line(b,x='season_year',y='economy',markers=True,title=f'{name}: Bowling Economy by Season (30+ Balls)',
                 labels={'season_year':'IPL season','economy':'Bowler runs conceded per over'},color_discrete_sequence=['#F4A886'])
            _chart(f,'season_econ')
        else:st.info('At least 30 selected legal balls are needed to chart seasonal bowling economy.')
    st.dataframe(d.rename(columns={'season_year':'Season','matches':'Matches','bat_runs':'Batting runs','bat_balls':'Balls faced','bowl_wickets':'Wickets','strike_rate':'Strike rate','economy':'Economy'}),hide_index=True,use_container_width=True)


def _opponent_venue(x,name,accent):
    left,right=st.columns(2)
    with left:
        d=by_category(x,'opponent_code').head(12).sort_values('runs')
        if len(d):
            d['Opponent']=d.opponent_code.map(ALL_TEAMS).fillna(d.opponent_code)
            f=px.bar(d,x='runs',y='Opponent',orientation='h',color_discrete_sequence=[accent],
                     title=f'{name}: Runs Scored Against IPL Opponents',labels={'runs':'Runs scored'})
            _chart(f,'opponent_runs','Opponent records are raw totals; teams may have played different numbers of matches.')
    with right:
        d=by_category(x,'opponent_code').sort_values('wickets').tail(12)
        if len(d):
            d['Opponent']=d.opponent_code.map(ALL_TEAMS).fillna(d.opponent_code)
            f=px.bar(d,x='wickets',y='Opponent',orientation='h',color_discrete_sequence=['#69BDEB'],
                     title=f'{name}: Wickets Taken Against IPL Opponents',labels={'wickets':'Credited wickets'})
            _chart(f,'opponent_wickets')
    d=by_category(x,'venue_group')
    if len(d):
        left,right=st.columns(2)
        with left:
            top=d.sort_values('runs').tail(10)
            f=px.bar(top,x='runs',y='venue_group',orientation='h',color_discrete_sequence=[accent],
                     title=f'{name}: Highest-Scoring IPL Venues',labels={'venue_group':'Venue','runs':'Batter runs'})
            _chart(f,'venue_runs','Venue total is not a causal measure of ground suitability; match counts and era can differ.')
        with right:
            top=d.sort_values('wickets').tail(10)
            f=px.bar(top,x='wickets',y='venue_group',orientation='h',color_discrete_sequence=['#81C9FD'],
                     title=f'{name}: Most Bowling Wickets by Venue',labels={'venue_group':'Venue','wickets':'Credited wickets'})
            _chart(f,'venue_wickets')
        st.dataframe(d.rename(columns={'venue_group':'Venue','matches':'Matches','runs':'Runs','balls':'Balls faced','wickets':'Wickets','strike_rate':'Strike rate','economy':'Bowling economy'}).head(40),hide_index=True,use_container_width=True)


def _phase_tab(x,name,accent,marts):
    b,w=phase_breakdown(x,marts['bat_phase'],marts['bowl_phase'])
    left,right=st.columns(2)
    with left:
        if len(b):
            b['phase']=pd.Categorical(b.phase,categories=PHASES,ordered=True)
            f=px.bar(b.sort_values('phase'),x='phase',y='bat_runs',title=f'{name}: Runs by Batting Phase',
              color_discrete_sequence=[accent],labels={'phase':'Overs in innings','bat_runs':'Batter runs'})
            _chart(f,'bat_phase_runs')
    with right:
        if len(w):
            w['phase']=pd.Categorical(w.phase,categories=PHASES,ordered=True)
            f=px.bar(w.sort_values('phase'),x='phase',y='wickets',title=f'{name}: Credited Wickets by Bowling Phase',
              color_discrete_sequence=['#78BDF3'],labels={'phase':'Overs in innings','wickets':'Wickets credited to bowler'})
            _chart(f,'bowl_phase_wickets')
    if len(b):
        a,c=st.columns(2)
        with a:
            bs=b[b.balls_faced>=12]
            if len(bs):
                f=px.line(bs.sort_values('phase'),x='phase',y='strike_rate',markers=True,
                  title=f'{name}: Batting Strike Rate Across Innings Phases',labels={'phase':'Innings phase','strike_rate':'Runs / 100 balls'},color_discrete_sequence=['#EAC575'])
                _chart(f,'phase_strike_rate','Minimum 12 balls faced in each displayed phase; rates are based on aggregated balls, not averages of innings rates.')
        with c:
            bs=b[b.balls_faced>=12]
            if len(bs):
                f=px.bar(bs.sort_values('phase'),x='phase',y='dot_pct',title=f'{name}: Dot-Ball Percentage by Batting Phase',
                  labels={'phase':'Innings phase','dot_pct':'Dot balls / balls faced (%)'},color_discrete_sequence=['#F18BA3'])
                _chart(f,'phase_dot_rate')
    st.caption('Phase analysis uses completed regulation deliveries only. Powerplay: overs 1–6; middle: 7–15; death: 16–20. Super Overs are excluded.')


def _consistency_tab(x,name,accent):
    d=x[x.batting_innings>0].sort_values(['match_date','match_id']).copy()
    b=x[x.bowling_innings>0].sort_values(['match_date','match_id']).copy()
    a,c=st.columns(2)
    with a:
        if len(d):
            d['last_five_runs_avg']=d.bat_runs.rolling(5,min_periods=3).mean()
            f=px.line(d,x='match_date',y='last_five_runs_avg',title=f'{name}: Last-Five-Batting-Innings Average Runs',
                labels={'match_date':'Match date','last_five_runs_avg':'Runs per innings (rolling five)'},color_discrete_sequence=[accent])
            _chart(f,'recent_bat_form','Uses only played batting innings, not matches in which the player did not bat. First two innings have no rolling value.')
    with c:
        if len(b):
            b['last_five_wickets_avg']=b.bowl_wickets.rolling(5,min_periods=3).mean()
            f=px.line(b,x='match_date',y='last_five_wickets_avg',title=f'{name}: Last-Five-Bowling-Innings Average Wickets',
                labels={'match_date':'Match date','last_five_wickets_avg':'Wickets per bowling innings (rolling five)'},color_discrete_sequence=['#78C8EA'])
            _chart(f,'recent_bowl_form')
    if len(d):
        d['Innings outcome']=pd.cut(d.bat_runs,bins=[-1,9,19,29,49,99,1000],labels=['0–9','10–19','20–29','30–49','50–99','100+'])
        f=px.histogram(d,x='Innings outcome',category_orders={'Innings outcome':['0–9','10–19','20–29','30–49','50–99','100+']},
          title=f'{name}: Distribution of Runs Scored per Batting Innings',color_discrete_sequence=[accent],
          labels={'Innings outcome':'Runs per batting innings'})
        _chart(f,'bat_innings_distribution')
        st.caption(f'Median runs per recorded batting innings: {d.bat_runs.median():.1f} across {len(d)} innings. Medians and distributions are descriptive, not future predictions.')


def _matchups_tab(x,name,player_id,accent,marts,lookup):
    mode=st.radio('Analyze this player',options=['As batter','As bowler'],horizontal=True,key='v2f_matchup_mode')
    phase=st.selectbox('Batter–bowler matchup phase',['All phases']+PHASES,key='v2f_matchup_phase')
    d=matchup_scope(x,marts['matchup'],player_id,mode,phase)
    rows=matchup_leaders(d,mode)
    rows['Opponent Player']=rows.other_id.map(lookup).fillna(rows.other_id)
    st.caption('Direct delivery matchups only; all filters restrict match IDs. Bowler dismissals exclude run-outs. Runs are batter-only runs and do not include extras. Phase choice affects matchup data only.')
    if rows.empty:return st.info('No deliveries recorded for this selection.')
    display=rows[rows.balls>=12].copy()
    if display.empty:st.warning('All opponents have fewer than 12 balls in this slice; showing the observed records without ranking claims.')
    else:
        subset=display.sort_values('balls',ascending=False).head(12)
        f=px.bar(subset.sort_values('runs'),x='runs',y='Opponent Player',orientation='h',
          title=f'{name}: Batter Runs in Direct Matchups (Minimum 12 Balls)',
          color_discrete_sequence=[accent],labels={'runs':'Batter runs'})
        _chart(f,'matchup_runs','Bars show direct batter runs off the counterpart bowler; minimum 12 balls faced.')
        f=px.scatter(subset,x='balls',y='strike_rate',size='runs',hover_name='Opponent Player',
          title=f'{name}: Matchup Balls Faced vs Scoring Rate',labels={'balls':'Balls faced','strike_rate':'Batter runs per 100 balls'},
          color_discrete_sequence=['#82C9EF'])
        _chart(f,'matchup_scatter','Every dot represents a direct batter–bowler pair, not a model forecast. Larger bubbles mean more batter runs.')
    st.dataframe(rows[['Opponent Player','matches','runs','balls','fours','sixes','dismissals','strike_rate','dot_pct']].rename(columns={
       'matches':'Matches','runs':'Batter runs','balls':'Balls faced','fours':'Fours','sixes':'Sixes','dismissals':'Bowler-credited dismissals',
       'strike_rate':'Batter strike rate','dot_pct':'Dot-ball %'}).head(80),hide_index=True,use_container_width=True)


def _compare_tab(x,all_player,name,player_id,accent,lookup,scope):
    other=[pid for pid in lookup if pid!=player_id and pid in set(all_player.player_id)]
    if not other:return st.info('No comparison players in the database.')
    other=sorted(other,key=lambda p:lookup[p].casefold())
    second=st.selectbox('Compare with a second IPL player',other,format_func=lambda p:f'{lookup[p]} · {p}',key='v2f_comparison_player')
    y=player_filter(all_player,second,**scope)
    s1,s2=summary(x),summary(y)
    st.caption('Identical season/venue/opponent/stage/innings-role filters are applied to both players independently. Different roles and sample sizes make rankings non-equivalent.')
    comparison=[('Recorded appearances','matches'),('Runs scored','runs'),('Batting innings','innings'),('Batting strike rate','strike_rate'),
      ('Batting average','bat_average'),('Credited wickets','wickets'),('Bowling economy','economy'),('Player-of-the-Match awards','pom')]
    table=pd.DataFrame([{'Metric':label,name:s1[key],lookup[second]:s2[key]} for label,key in comparison])
    st.dataframe(table,hide_index=True,use_container_width=True)
    records=pd.DataFrame([{'Player':name,'Metric':'Batter runs','Value':s1['runs']},{'Player':lookup[second],'Metric':'Batter runs','Value':s2['runs']},
        {'Player':name,'Metric':'Credited wickets','Value':s1['wickets']},{'Player':lookup[second],'Metric':'Credited wickets','Value':s2['wickets']}])
    f=px.bar(records,x='Metric',y='Value',color='Player',barmode='group',
       title=f'{name} vs {lookup[second]}: Batting Runs and Bowling Wickets',
       color_discrete_sequence=[accent,'#79C7EF'],labels={'Value':'Observed count'})
    _chart(f,'comparison_grouped','Separate run and wicket scales should not be interpreted as a combined skill score.')
    d=pd.concat([seasons(x).assign(Player=name),seasons(y).assign(Player=lookup[second])])
    if len(d):
        f=px.line(d,x='season_year',y='bat_runs',color='Player',markers=True,
          title=f'{name} vs {lookup[second]}: Batting Runs by Season',
          labels={'season_year':'IPL season','bat_runs':'Batter runs'},color_discrete_sequence=[accent,'#79C7EF'])
        _chart(f,'comparison_season_runs')


def render():
    from dashboard.views import setup
    setup()
    marts=data_marts();allp=marts['player'];names=names_map()
    options=sorted(allp.player_id.astype(str).unique(),key=lambda p:(names.get(p,p).casefold(),p))

    # The player picker belongs in the main content area, NOT inside a sidebar
    # that users often collapse. Streamlit selectboxes support type-to-search.
    st.markdown('### 🏏 Select an IPL player')
    st.caption(f'Search {len(options):,} IPL players by typing a name. The selection changes all player KPIs, charts and head-to-head records below.')

    # First visit: show the dataset's leading batter by total recorded runs
    # rather than the alphabetically first name (A Ashish Reddy). Keep the
    # user's selection on later reruns and across page navigation.
    initial=allp.groupby('player_id',sort=False).bat_runs.sum().idxmax()
    state=getattr(st,'session_state',None)
    if hasattr(state,'get') and hasattr(state,'__setitem__'):
        if state.get('v2f_player_id') not in options:
            state['v2f_player_id']=initial

    familiar_names={'V Kohli':'Virat Kohli','RG Sharma':'Rohit Sharma',
                    'S Dhawan':'Shikhar Dhawan','DA Warner':'David Warner'}
    def display_name(pid):
        canonical=names.get(pid,pid)
        friendly=familiar_names.get(canonical,canonical)
        return (f'{friendly} ({canonical}) · {pid}' if friendly!=canonical
                else f'{canonical} · {pid}')

    choose=st.selectbox('IPL player',options,format_func=display_name,
                        key='v2f_player_id',help='Type a player name to find them; all 809 Cricsheet player IDs remain available.')

    # Filters specific to a previous player can accidentally hide every match
    # for a newly selected player. Clear those selections on player changes.
    if hasattr(state,'get') and hasattr(state,'pop'):
        if state.get('_v2f_previous_player') != choose:
            for filter_key in ('v2f_club','v2f_opponent','v2f_venue','v2f_stage','v2f_role'):
                state.pop(filter_key,None)
            state['_v2f_previous_player']=choose

    with st.sidebar:
        st.markdown('### 🏏 PLAYER INTELLIGENCE FILTERS')
        st.caption('Choose a player at the top of this page. Use these additional filters to focus their records.')
        base=allp[allp.player_id.eq(choose)]
        lo,hi=int(allp.season_year.min()),int(allp.season_year.max())
        years=st.slider('IPL season range',min_value=lo,max_value=hi,value=(lo,hi),key='v2f_years')
        clubs=['All franchises']+sorted(base.team_code.dropna().unique().tolist())
        club=st.selectbox('Franchise represented',clubs,format_func=lambda v:ALL_TEAMS.get(v,v),key='v2f_club')
        opponents=['All opponents']+sorted(base.opponent_code.dropna().unique().tolist())
        opponent=st.selectbox('Opponent franchise',opponents,format_func=lambda v:ALL_TEAMS.get(v,v),key='v2f_opponent')
        venue=st.selectbox('Venue',['All venues']+sorted(base.venue_group.dropna().unique().tolist()),key='v2f_venue')
        stage=st.selectbox('Match stage',['All stages']+sorted(base.match_type.dropna().unique().tolist()),key='v2f_stage')
        role=st.selectbox('Team innings role',['All innings roles','Batting first','Chasing'],key='v2f_role')
        st.caption('All main charts and KPI totals share this match selection. Matchup phase has its own targeted filter.')
    if club in TEAMS:inject_theme(club)
    name=names.get(choose,choose)
    accent=TEAMS[club][1] if club in TEAMS else '#E8B86A'
    scope=dict(year_min=int(years[0]),year_max=int(years[1]),team=club,opponent=opponent,venue=venue,stage=stage,role=role)
    x=player_filter(allp,choose,**scope)
    hero(f'{name} | Player Intelligence','Career trajectory, opponent and venue splits, innings phases, genuine head-to-head records, and player comparisons.',
        'IPL INTELLIGENCE 360° / PLAYER LAB',f'{choose} • 2008–2026',team=club if club in TEAMS else None)
    st.caption('Player identities use verified Cricsheet identifiers. Season data is historical IPL only; no automated real-time updates. Official player photos are not bundled without licensed rights.')
    if x.empty:return st.warning('No recorded appearances meet all selected filters. Try widening season, opponent or venue filters.')
    _cards_scope(x)
    _kpis(summary(x))
    st.markdown('#### 🧠 Sports analyst reading')
    ss=summary(x)
    interpretations=[]
    if ss['innings']>=10 and ss['balls']>=120:
        interpretations.append(f"Across {ss['innings']} selected batting innings, {name} scored {ss['runs']:,} runs at {ss['strike_rate']:.1f} runs per 100 balls. Strike rate indicates scoring tempo, not match impact in isolation.")
    if ss['bowl_innings']>=10 and ss['bowl_balls']>=120:
        interpretations.append(f"With {ss['wickets']} credited wickets in {ss['bowl_innings']} bowling innings, {name} conceded {ss['economy']:.2f} runs per over in this sample. Opposition strength and match conditions are not controlled.")
    if not interpretations:interpretations.append('Selected observations are limited; broaden the filters before drawing conclusions about consistency or tactical advantage.')
    for item in interpretations:st.markdown('- '+item)
    tabs=st.tabs(['📈 Career & seasons','⚔️ Opponents & venues','🎯 Innings-phase DNA','📊 Form & consistency','🏏 Batter–bowler matchups','🆚 Compare players','📥 Sources & data'])
    with tabs[0]:_season_tab(x,name,accent)
    with tabs[1]:_opponent_venue(x,name,accent)
    with tabs[2]:_phase_tab(x,name,accent,marts)
    with tabs[3]:_consistency_tab(x,name,accent)
    with tabs[4]:_matchups_tab(x,name,choose,accent,marts,names)
    with tabs[5]:_compare_tab(x,allp,name,choose,accent,names,scope)
    with tabs[6]:
        section('SOURCE TRACEABILITY','One row per source-recorded player/team/match appearance.')
        st.dataframe(x.rename(columns={'player_id':'Player ID','match_id':'Match ID','team_code':'Franchise','opponent_code':'Opponent','bat_runs':'Batter runs','bowl_wickets':'Credited wickets'}),hide_index=True,use_container_width=True)
        st.download_button('⬇ Export selected player records',data=x.to_csv(index=False).encode('utf-8'),
             file_name='IPL360_'+choose+'_match_records.csv',mime='text/csv',key='v2f_download')
        st.caption('Record coverage: IPL Cricsheet 2008–2026 · unique player IDs; career totals exclude Super Overs; player lists may include substitutes. Batting average excludes non-dismissals; bowling wickets exclude non-credited dismissals.')
