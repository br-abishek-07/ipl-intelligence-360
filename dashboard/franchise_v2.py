"""V2-C Streamlit franchise desks; pure calculations live in franchise_analytics."""
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from dashboard.franchise_analytics import *
from dashboard.analytics import TEAMS,ALL_TEAMS
from dashboard.design import hero,kpi,section,palette
from dashboard.data import ROOT,load
from dashboard import franchise_charts as fc
from dashboard.chart_ui import render_chart
from dashboard.legends import limit_awards,player_award_leaders

def _styled(fig,height=345):
    fig.update_layout(template='plotly_dark',paper_bgcolor='rgba(0,0,0,0)',plot_bgcolor='rgba(0,0,0,0)',height=height,
       font=dict(color='#EAF2FC'),margin=dict(l=8,r=8,t=25,b=25),legend_title_text='')
    fig.update_xaxes(gridcolor='rgba(172,193,219,.10)',zeroline=False)
    fig.update_yaxes(gridcolor='rgba(172,193,219,.10)',zeroline=False)
    render_chart(fig,key='franchise_legacy_'+str(fig.layout.title.text or 'untitled').lower().replace(' ','_'))


def _bar(df,x,y,accent,orientation='v',height=345,color=None):
    if df.empty:st.info('No observations satisfy these filters.');return
    fig=px.bar(df,x=x,y=y,color=color,orientation=orientation,color_discrete_sequence=[accent,'#A5B8D0','#EEBF82'])
    _styled(fig,height)


def _role_win_pct(t,batted_first):
    d=t[t.is_decided.astype(bool) & t.batted_first.eq(batted_first)]
    return f'{100*d.won.mean():.1f}%' if len(d) else '—'

def _metrics_row(stats,history,team_matches):
    all_titles=int(history.champion.sum()) if len(history) else 0
    cards=[('Matches Played',str(stats['matches']),'Matches matching current filters'),
      ('Matches Won',str(stats['wins']),f"Out of {stats['decided']} decided matches"),
      ('Match Win Rate',f"{stats['win_pct']:.1f}%" if np.isfinite(stats['win_pct']) else '—','Decided games only'),
      ('IPL Championships',str(all_titles),'Franchise history · all seasons'),
      ('Total Runs Scored',f"{stats['runs_scored']:,}",'Filtered regulation innings'),
      ('Batting Run Rate',f"{stats['batting_rr']:.2f}" if np.isfinite(stats['batting_rr']) else '—','Batting per 6 legal balls'),
      ('Opposition Wickets Taken',str(stats['wickets_taken']),'All team dismissals'),
      ('Bowling Runs Conceded/Over',f"{stats['bowling_rr']:.2f}" if np.isfinite(stats['bowling_rr']) else '—','Opposition runs / 6 balls'),
      ('Batting Boundary Ball %',f"{stats['batting_boundary_rate']:.1f}%" if np.isfinite(stats['batting_boundary_rate']) else '—','4s+6s per 100 legal balls'),
      ('Sixes Hit',str(stats['batting_sixes']),'Selected-match batting'),
      ('Highest Innings Total',str(stats['highest_total']) if stats['highest_total'] is not None else '—','Recorded team innings'),
      ('Matches Without a Result',str(stats['no_result']),'Not treated as losses'),
      ('Average Runs per Innings',f"{stats['batting_run_average']:.1f}" if np.isfinite(stats['batting_run_average']) else '—','Selected regulation innings'),
      ('Run Difference (For − Against)',f"{stats['runs_scored']-stats['runs_conceded']:+,}",'Scored minus conceded'),
      ('Chasing Win Rate',_role_win_pct(team_matches,False),'Decided chases only'),
      ('Batting-First Win Rate',_role_win_pct(team_matches,True),'Decided batting-first games')]
    for offset in range(0,len(cards),4):
        cols=st.columns(4,gap='small')
        for col,(name,value,note) in zip(cols,cards[offset:offset+4]):
            with col:kpi(name,value,note)


def _choose_filters(code:str,tm,full_lineups)->TeamSelection:
    all_t=tm[tm.team_code==code]
    yr_min=int(tm.season_year.min());yr_max=int(tm.season_year.max())
    st.sidebar.markdown(f'### {code} SCOUTING FILTERS')
    yr=st.sidebar.slider('Seasons',min_value=yr_min,max_value=yr_max,value=(yr_min,yr_max),key=f'v2c_{code}_years')
    if not isinstance(yr,(list,tuple)):yr=(yr_min,yr_max)
    st.sidebar.caption('All team sections update together. Trophy totals are explicitly all-time.')
    opponents=st.sidebar.multiselect('Opponents',[x for x in sorted(all_t.opponent_code.dropna().unique())],
            format_func=lambda x:ALL_TEAMS.get(x,x),key=f'v2c_{code}_opponents') or ()
    venues=st.sidebar.multiselect('Venues',sorted(all_t.venue_group.dropna().unique()),key=f'v2c_{code}_venues') or ()
    stages=st.sidebar.multiselect('Match stage',sorted(all_t.match_type.dropna().unique()),key=f'v2c_{code}_stages') or ()
    result=st.sidebar.selectbox('Team match result',['All results','Won','Lost','No result'],key=f'v2c_{code}_result')
    role=st.sidebar.selectbox('Innings role',['Both innings roles','Batted first','Chased'],key=f'v2c_{code}_role')
    toss=st.sidebar.selectbox('Toss outcome',['All toss outcomes','Won toss','Lost toss'],key=f'v2c_{code}_toss')
    players=full_lineups[full_lineups.team_code==code][['cricsheet_player_id','player_name']].dropna().drop_duplicates('cricsheet_player_id').sort_values('player_name')
    names=dict(zip(players.cricsheet_player_id.astype(str),players.player_name))
    options=['All recorded participants']+list(names)
    selected=st.sidebar.selectbox('Match participant',options,
            format_func=lambda x:names.get(x,x),key=f'v2c_{code}_player')
    if selected!='All recorded participants':
        st.sidebar.caption('Participant lists can include Impact Players; not guaranteed starting XI.')
    return TeamSelection(code,int(yr[0]),int(yr[1]),tuple(opponents),tuple(venues),tuple(stages),result,role,toss,
                selected if selected!='All recorded participants' else None)


@st.cache_data(show_spinner=False,max_entries=2)
def _cached_match_awards():
    """Cache static award data to avoid disk reads after every filter change."""
    return pd.read_csv(ROOT/"data/analytics/player_of_match_awards.csv", low_memory=False)

@st.cache_data(show_spinner=False,max_entries=2)
def _cached_lineups():
    return pd.read_csv(ROOT/'data/raw/lineups.csv.gz',
      usecols=['match_id','team_code','cricsheet_player_id','player_name'],low_memory=False)

def _show(fig, key):
    if fig is None: st.info('Insufficient observations for this visual with the selected filters.')
    else: render_chart(fig,key=f'ipl_team_{key}')

def _chart_pair(left,right, key):
    a,b=st.columns(2,gap='medium')
    with a: _show(left, key+'_left')
    with b: _show(right, key+'_right')


def render_team(code:str,data_provider=load):
    """Replace former basic franchise pages while preserving the same ten page routes."""
    name,accent=TEAMS[code]
    full_matches=data_provider('matches')
    full_tm=data_provider('team_matches')
    # lineups are used solely to restrict matches to recorded participants, never to infer captaincy.
    full_lineups=_cached_lineups()
    selection=_choose_filters(code,full_tm,full_lineups)
    t=select_team_matches(full_tm,selection,full_lineups)
    hero(f'{name} | Franchise Intelligence',
        'A data-backed scouting dossier covering legacy, results, batting and bowling, opposition and ground tactics.',
        'IPL INTELLIGENCE 360° / FRANCHISE DESK',f'{code} • TEAM THEME',team=code)
    from dashboard.squad_2026 import squad_panel
    squad_panel(code)
    st.page_link('pages/16_Player_Intelligence_Lab.py',label='🏏 Open Advanced Player Intelligence Lab →')
    st.page_link('pages/17_Team_DNA_and_Strategy.py',label='🧬 Open Team DNA & Strategy Studio →')
    st.caption('Franchise crests use IPL-hosted image URLs when available; offline an original decorative team mark appears instead. Images are not packaged as licensed assets. Trophy totals are all-time; analysis cards follow filters.')
    if t.empty:
        st.warning('No matches match every chosen filter. Widen one or more filters in the sidebar.')
        return
    ids=t.match_id.unique()
    all_innings=data_provider('innings');all_phase=data_provider('phase_match')
    all_bat=data_provider('bat_match');all_bowl=data_provider('bowl_match')
    scope=team_scope(ids,code,all_innings,all_phase,all_bat,all_bowl)
    stats=count_stats(t,scope)
    history=playoff_history(full_matches,code)
    leaders=player_leaders(scope['bat'],scope['bowl'])
    _metrics_row(stats,history,t)
    section('THE ANALYST’S DESK','All qualitative observations below use the active match-selection sample.')
    for note in analyst_brief(t,scope,scope,code):st.markdown('- '+note)
    tabs=st.tabs(['🏆 Titles & achievements','📈 Match results by season','🏏 Batting performance','🎯 Bowling performance',
                  '⭐ Player records & captains','🥇 Match awards','⚔️ Opponents & venues','📋 Match records & download'])
    with tabs[0]:
        section('FRANCHISE HONOURS','All-time honours are independent of active filters so the trophy cabinet never disappears.')
        titles=history[history.champion] if len(history) else history
        finals=history[history.finalist] if len(history) else history
        a,b,c=st.columns(3)
        with a:kpi('IPL Championships Won',str(len(titles)),'Verified from recorded IPL Finals')
        with b:kpi('IPL Final Appearances',str(len(finals)),'Includes runner-up seasons')
        with c:kpi('Seasons Reaching Playoffs',str(len(history)),'Recorded playoff participation')
        if len(titles):st.success('🏆 Championship seasons: '+', '.join(map(str,titles.season.tolist())))
        else:st.info('No IPL championship recorded for this franchise within the source’s seasons.')
        if len(history):st.dataframe(history.rename(columns={'season':'Season','outcome':'Achievement','champion':'Champion','finalist':'Finalist'}),hide_index=True,use_container_width=True)
        section('INTERESTING FACTS · SOURCE-DERIVED','Dynamic facts about the current filtered matches.')
        opp=opponents_table(t);venue=venues_table(t)
        if len(opp):
            most=opp.iloc[0];st.markdown(f'- **Most frequent opponent:** {most["name"]}, {int(most.matches)} decided meetings in the selected sample.')
        if len(venue):
            v=venue.iloc[0];st.markdown(f'- **Most frequently played ground:** {v.venue_group}, {int(v.matches)} decided appearances; this does not automatically mean home ground.')
        if len(leaders['batting']):
            x=leaders['batting'].iloc[0];st.markdown(f'- **Leading batter in selection:** {x.player_name} — {int(x.runs):,} runs in {int(x.matches)} recorded batting matches.')
        if len(leaders['bowling']):
            x=leaders['bowling'].iloc[0];st.markdown(f'- **Leading wicket-taker in selection:** {x.player_name} — {int(x.wickets):,} credited wickets in {int(x.matches)} recorded bowling matches.')
        st.caption('Finals/qualifiers are explicitly recorded; playoff qualification in formats without a played playoff is not inferred.')
    with tabs[1]:
        section('MATCH RESULTS BY SEASON','Seasonal wins, losses, win rate, recent form and scoring patterns in the selected matches.')
        _chart_pair(fc.season_combo(t,accent),fc.season_win_pct_fig(t,accent), f'{code}_season_results')
        _chart_pair(fc.form_line(t,accent),fc.scoring_area(t,accent), f'{code}_rolling_form')
        _show(fc.season_win_combo(t,accent), f'{code}_wins_losses_line')
        _show(fc.scoring_scatter(t,accent), f'{code}_runs_for_against_scatter')
        st.caption('Comparisons are descriptive: shorter innings, DLS revisions and changing season rules can affect raw scoring totals. Rolling form uses the last ten *decided* games (at least five observations).')
        d=fc.season_result_table(t)
        st.dataframe(d.round(2),hide_index=True,use_container_width=True)
        decided=t[t.is_decided.astype(bool)]
        role=decided.groupby('batted_first').agg(matches=('match_id','size'),wins=('won','sum')).reset_index()
        role['role']=role.batted_first.map({True:'Bat first',False:'Chase'})
        role['win_pct']=100*role.wins/role.matches.replace(0,np.nan)
        st.markdown('#### Bat first vs chase · decided matches')
        st.dataframe(role[['role','matches','wins','win_pct']].round(1),hide_index=True,use_container_width=True)
    with tabs[2]:
        section('BATTING PERFORMANCE BY INNINGS PHASE','Three match phases: 1–6, 7–15 and 16–20 overs. The benchmark is from the same selected fixtures.')
        _chart_pair(fc.phase_grouped(scope,accent),fc.boundary_stacked(scope,accent), f'{code}_batting_phase')
        _show(fc.phase_trends(scope,accent), f'{code}_batting_phase_trend')
        _chart_pair(fc.scoring_area(t,accent),fc.score_distribution(scope,accent), f'{code}_batting_score_distribution')
        st.caption('Boundary chart shows absolute counts, not rates. The phases have different lengths; compare phase run rates for normalized performance. The histogram uses regulation innings recorded in Cricsheet.')
        st.dataframe(phase_table(scope['bat_phase']).round(2),hide_index=True,use_container_width=True)
        section('TOP BATTERS: RUNS AND SCORING SPEED','Volume, intent and sample size are shown together.')
        _chart_pair(fc.bat_horizontal(leaders,accent),fc.bat_scatter(leaders,accent), f'{code}_batter_leaders')
        bat=leaders['batting'].head(18)
        st.dataframe(bat[['player_name','matches','runs','balls','strike_rate','fours','sixes']].round(2),hide_index=True,use_container_width=True)
        st.caption('Bubble size is matches recorded for each batter. Scatter minimum: 60 balls. Player rankings use only the current filtered match IDs.')
    with tabs[3]:
        section('BOWLING PERFORMANCE BY INNINGS PHASE','Economy is runs conceded per six legal deliveries; lower is better.')
        _chart_pair(fc.phase_grouped(scope,accent,bowling=True),fc.bowling_wickets_by_phase(scope,accent), f'{code}_bowling_phase')
        _show(fc.phase_trends(scope,accent,bowling=True), f'{code}_bowling_phase_trend')
        st.dataframe(phase_table(scope['bowl_phase']).round(2),hide_index=True,use_container_width=True)
        section('TOP BOWLERS: WICKETS AND ECONOMY','Credited wickets, economy and workloads.')
        _chart_pair(fc.bow_horizontal(leaders,accent),fc.bow_scatter(leaders,accent), f'{code}_bowler_leaders')
        bowl=leaders['bowling'].head(18)
        st.dataframe(bowl[['player_name','matches','wickets','balls','economy']].round(2),hide_index=True,use_container_width=True)
        st.caption('Team phase dismissals include run-outs; individual bowler wickets exclude uncredited dismissals. Scatter minimum: 60 legal balls. Bubble size is delivery volume.')
    with tabs[4]:
        section('FRANCHISE PLAYER RECORDS','Statistical leaders are recalculated for the exact selected match universe.')
        bat=leaders['batting'];bowl=leaders['bowling']
        cols=st.columns(3)
        if len(bat):
            a=bat.iloc[0]
            with cols[0]:kpi('Most Runs for Selected Team',a.player_name,f'{int(a.runs):,} runs · {int(a.matches)} batting matches')
            qualified=bat[bat.balls>=120].sort_values('strike_rate',ascending=False)
            if len(qualified):
                x=qualified.iloc[0]
                with cols[1]:kpi('Highest Batting Strike Rate',x.player_name,f'{x.strike_rate:.1f} SR · ≥120 balls')
        if len(bowl):
            x=bowl.iloc[0]
            with cols[2]:kpi('Most Wickets for Selected Team',x.player_name,f'{int(x.wickets)} credited wickets')
        section('CAPTAINCY & LEADERSHIP')
        capfile=ROOT/'data/metadata/captaincy_match_registry.csv'
        if capfile.exists():
            captain_registry=pd.read_csv(capfile)
            try:
                captains=verified_captain_stats(t,captain_registry,full_lineups)
                if not captains.empty:
                    st.dataframe(captains.round(1),hide_index=True,use_container_width=True)
                    complete=len(captain_registry[(captain_registry.team_code==code)&captain_registry.match_id.isin(t.match_id)])
                    st.caption(f'Captain dataset covers {complete} of {len(t)} selected team matches. Missing captain records are not inferred; sources must be independently checked.')
                    qualified=captains[captains.decided>=20]
                    if len(qualified):
                        leader=qualified.iloc[0]
                        st.markdown(f'**Leadership leader among verified records (min 20 decided matches):** {leader.captain_player_name}, {int(leader.wins)} wins in {int(leader.decided)} decided matches. Coverage may be incomplete.')
                else:st.info('No cited captain-by-match records are available for this selection. Captain rankings remain unavailable.')
            except ValueError as err:st.warning('Captain registry rejected: '+str(err))
        else:st.info('**Captain rankings are intentionally pending verification.** Cricsheet player lists identify participants, not captains. A best-captain claim would be misleading without a cited captain-by-match registry.')
        st.caption('Import template: data/metadata/captaincy_match_registry_template.csv. Each captain needs a source, player ID and matching franchise-match; structural checks cannot replace manual verification.')
        st.markdown('#### Batting leaders');st.dataframe(bat.head(15).round(2),hide_index=True,use_container_width=True)
        st.markdown('#### Bowling leaders');st.dataframe(bowl.head(15).round(2),hide_index=True,use_container_width=True)
    with tabs[5]:
        section('PLAYER-OF-THE-MATCH HONOURS','Awards follow all active franchise slicers and are matched to stable Cricsheet player IDs.')
        awards=_cached_match_awards()
        award_scope=limit_awards(awards,ids,code)
        award_rank=player_award_leaders(award_scope)
        if award_rank.empty:
            st.info('No player-of-the-match awards found for this selection.')
        else:
            x,y,z=st.columns(3)
            with x:kpi('Player-of-the-Match Awards',str(len(award_scope)),'From selected franchise appearances')
            with y:kpi('Award-Winning Franchise Players',str(award_scope.player_id.nunique()),'Unique Cricsheet player identities')
            with z:kpi('Most Match Awards by One Player',str(int(award_rank.awards.max())),award_rank.iloc[0].player_name)
            top=award_rank.head(12).sort_values('awards')
            fig=px.bar(top,x='awards',y='player_name',orientation='h',
                title='Franchise Players with the Most Player-of-the-Match Awards',
                labels={'awards':'Awards earned','player_name':'Player'},color_discrete_sequence=[accent])
            _show(fc.finish(fig,accent,410), f'{code}_award_leaders')
            season_awards=award_scope.groupby('season_year').size().reset_index(name='awards')
            fig=px.bar(season_awards,x='season_year',y='awards',
                title='Player-of-the-Match Awards Won by Franchise Players Each Season',
                labels={'season_year':'IPL season','awards':'Awards'},color_discrete_sequence=[accent])
            _show(fc.finish(fig,accent,360), f'{code}_awards_by_season')
            st.dataframe(award_rank[['player_name','awards','first_season','last_season']].rename(columns={
                'player_name':'Player','awards':'Match awards','first_season':'First recorded award season',
                'last_season':'Latest recorded award season'}),hide_index=True,use_container_width=True)
            st.caption('Source: Cricsheet match JSON player-of-the-match field. Multiple franchise stints remain separate; awards do not measure overall causal impact.')
    with tabs[6]:
        section('OPPONENT HEAD-TO-HEAD AND VENUE RESULTS','Historical labels preserved: pre-rebrand team histories are consolidated within their continuity.')
        opp=opponents_table(t);grounds=venues_table(t)
        _chart_pair(fc.rival_stacked(t,accent),fc.venue_bubbles(t,accent), f'{code}_rivalry_venue')
        a,b=st.columns(2)
        with a:
            st.markdown('#### Head-to-head record')
            st.dataframe(opp.round(1),hide_index=True,use_container_width=True)
        with b:
            st.markdown('#### Ground performance')
            st.dataframe(grounds.head(25).round(1),hide_index=True,use_container_width=True)
        st.caption('Opponent and ground win % excludes no-result games. Venue performance reflects fixture composition and is not causal home advantage.')
    with tabs[7]:
        section('MATCH-LEVEL EVIDENCE & DOWNLOAD')
        cols=['match_date','season_year','opponent_code','match_type','venue_group','runs_for','runs_against','won','lost','no_result','batted_first']
        st.dataframe(t[cols].sort_values('match_date',ascending=False),hide_index=True,use_container_width=True)
        st.download_button('Download selected franchise matches',data=t.to_csv(index=False).encode('utf-8'),
            file_name=f'{code}_IPL_Intelligence_V2C_matches.csv',mime='text/csv',key=f'dl_{code}_v2c')
        st.download_button('Download selected player batting records',data=bat.to_csv(index=False).encode('utf-8'),
            file_name=f'{code}_IPL_V2C_batting.csv',mime='text/csv',key=f'dlb_{code}_v2c')
        st.download_button('Download selected player bowling records',data=bowl.to_csv(index=False).encode('utf-8'),
            file_name=f'{code}_IPL_V2C_bowling.csv',mime='text/csv',key=f'dlw_{code}_v2c')
        st.caption(f'{len(t)} matches selected · all tables filtered by the exact selected match IDs · seasons {selection.year_min}–{selection.year_max}.')
