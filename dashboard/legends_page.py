"""V2-E standalone records and legends: all charts have named fullscreen controls."""
from __future__ import annotations
import pandas as pd
import plotly.express as px
import streamlit as st
from dashboard.analytics import TEAMS,ALL_TEAMS
from dashboard.data import ROOT
from dashboard.design import hero, kpi, section
from dashboard.chart_ui import render_chart
from dashboard.legends import (limit_awards,player_award_leaders,batting_records,
                               bowling_records,trophy_table,verify_award_integrity)

@st.cache_data(show_spinner=False)
def get_awards():
    return pd.read_csv(ROOT/'data/analytics/player_of_match_awards.csv',low_memory=False)

def _plot(fig,key):
    fig.update_layout(template='plotly_dark',paper_bgcolor='rgba(0,0,0,0)',
       plot_bgcolor='rgba(0,0,0,0)',font=dict(color='#E8F1FD'),
       margin=dict(l=12,r=12,t=53,b=42),height=395,
       legend=dict(orientation='h',y=-0.24,title_text=''))
    render_chart(fig,key='records_'+key)

def render():
    from dashboard.views import setup, table
    setup()
    full_matches=table('matches')
    full_awards=get_awards()
    full_bat=table('bat_match');full_bowl=table('bowl_match')
    hero('Records & Legends','IPL championships, Player-of-the-Match awards, batting milestones and bowling records — sourced from match-level data.','THE HISTORY BOOK','2008–2026')
    with st.sidebar:
        st.markdown('#### 🏆 RECORDS & LEGENDS FILTERS')
        year_min=int(full_matches.season_year.min());year_max=int(full_matches.season_year.max())
        start,end=st.slider('Seasons for performance & awards',min_value=year_min,max_value=year_max,value=(year_min,year_max),key='v2e_legends_year')
        team=st.selectbox('Franchise',['All teams']+list(TEAMS),format_func=lambda x:'Entire league' if x=='All teams' else ALL_TEAMS.get(x,x),key='v2e_legends_team')
        st.caption('The trophy-history section explicitly remains all-time. Player statistics and award charts follow selected seasons and team.')
    matches=full_matches[full_matches.season_year.between(start,end)]
    if team!='All teams':matches=matches[(matches.team1_code==team)|(matches.team2_code==team)]
    ids=set(matches.match_id)
    awards=limit_awards(full_awards,ids,team)
    bats=batting_records(full_bat,ids,team)
    bowls=bowling_records(full_bowl,ids,team)
    awleaders=player_award_leaders(awards)
    tabs=st.tabs(['🏆 Trophy history','🥇 Match awards','🏏 Batting legends','🎯 Bowling legends','🔎 Source & definitions'])
    with tabs[0]:
        section('IPL CHAMPIONSHIPS BY FRANCHISE','Championship years and finals are based on the final-match outcome in the source dataset; title totals are always all-time.')
        trophies=trophy_table(full_matches,list(TEAMS))
        a,b,c=st.columns(3)
        winner=trophies.iloc[0] if len(trophies) else None
        with a:kpi('Total IPL Finals in Dataset',str(int((full_matches.match_type=='Final').sum())),'Includes all seasons, independent of slicers')
        with b:kpi('Franchises with a Title',str(int((trophies.championships>0).sum())),'Current franchises and their historical aliases')
        with c:kpi('Most Titles in Current Franchise Set',str(int(winner.championships)) if winner is not None else '—',winner.team_code if winner is not None else 'No final records')
        if len(trophies):
            fig=px.bar(trophies.sort_values('championships'),x='championships',y='team_code',orientation='h',color='championships',color_continuous_scale='YlOrBr',
                       title='IPL Championships Won by Each Current Franchise',labels={'championships':'IPL titles','team_code':'Franchise'})
            _plot(fig,'championships_all_time')
            st.dataframe(trophies.rename(columns={'team_code':'Team','championships':'Titles','championship_seasons':'Championship years','finals':'Final appearances','playoff_seasons':'Playoff seasons'}),hide_index=True,use_container_width=True)
    with tabs[1]:
        section('PLAYER-OF-THE-MATCH AWARDS','Recipients are linked to teams using stable Cricsheet identities and the match participant registry.')
        if awards.empty:st.info('No award records available for these filters.')
        else:
            a,b,c=st.columns(3)
            with a:kpi('Player-of-the-Match Awards',str(len(awards)),'Award entries from the selected matches')
            with b:kpi('Players Receiving Awards',str(awards.player_id.nunique()),'Distinct verified player IDs')
            with c:kpi('Highest Individual Award Count',str(int(awleaders.awards.max())),'Awards within selected filter scope')
            left,right=st.columns(2)
            with left:
                top=awleaders.head(14).sort_values('awards')
                fig=px.bar(top,x='awards',y='player_name',orientation='h',color_discrete_sequence=['#F0BE68'],
                           title='Players with the Most Player-of-the-Match Awards',labels={'player_name':'Player','awards':'Awards'})
                _plot(fig,'top_player_of_match_awards')
            with right:
                byyear=awards.groupby('season_year').size().reset_index(name='awards')
                fig=px.line(byyear,x='season_year',y='awards',markers=True,title='Player-of-the-Match Awards Recorded by IPL Season',
                            labels={'season_year':'Season','awards':'Recorded awards'},color_discrete_sequence=['#73C5F9'])
                _plot(fig,'player_of_match_per_season')
            st.dataframe(awleaders.rename(columns={'player_name':'Player','team_code':'Team','awards':'Awards','first_season':'First award season','last_season':'Last award season','player_id':'Cricsheet ID'}).head(40),hide_index=True,use_container_width=True)
    with tabs[2]:
        section('BATTING MILESTONES & CAREER TOTALS','Fifties count 50–99 runs, centuries 100+ runs. Runs and scores are from available regulation innings.')
        if bats.empty:st.info('No batting records with the selected filters.')
        else:
            a,b,c=st.columns(3)
            with a:kpi('Highest Recorded Individual Innings',str(int(bats.highest_score.max())),'Runs by one player in a regulation match')
            with b:kpi('Recorded 100+ Player Innings',str(int(bats.centuries.sum())),'Centuries in selected matches')
            with c:kpi('Total Sixes by Selected Players',str(int(bats.sixes.sum())),'Boundary sixes, not extras')
            top=bats.head(14).sort_values('runs')
            _plot(px.bar(top,x='runs',y='player_name',orientation='h',title='Leading Run Scorers in the Selected IPL Matches',
                  labels={'runs':'Runs scored','player_name':'Batter'},color_discrete_sequence=['#F0BE68']),'batting_runs')
            hi=bats.sort_values('highest_score',ascending=False).head(20)
            _plot(px.scatter(hi,x='runs',y='highest_score',size='innings',hover_name='player_name',
                      title='Career Runs vs Highest Individual Score (Top 20 Innings Leaders)',
                      labels={'runs':'Total runs in selection','highest_score':'Highest score in one match'},color_discrete_sequence=['#79C1F2']),'batter_high_score_scatter')
            st.dataframe(bats.head(30).round(2),hide_index=True,use_container_width=True)
    with tabs[3]:
        section('BOWLING MILESTONES & WICKET RECORDS','Credited wickets only; run-outs are excluded from individual bowler totals.')
        if bowls.empty:st.info('No bowling records with the selected filters.')
        else:
            a,b,c=st.columns(3)
            with a:kpi('Highest Wickets in One Match',str(int(bowls.best_match_wickets.max())),'Credited to an individual bowler')
            with b:kpi('Recorded Four-Wicket Hauls',str(int(bowls.four_wicket_hauls.sum())),'Exactly 4 credited wickets in one match')
            with c:kpi('Recorded Five-Plus Wicket Hauls',str(int(bowls.five_wicket_hauls.sum())),'At least 5 credited wickets in one match')
            _plot(px.bar(bowls.head(14).sort_values('wickets'),x='wickets',y='player_name',orientation='h',
                      title='Leading Wicket Takers in the Selected IPL Matches',
                      labels={'wickets':'Credited wickets','player_name':'Bowler'},color_discrete_sequence=['#76C8E4']),'bowling_wickets')
            q=bowls[(bowls.matches>=10)&bowls.economy.notna()].sort_values('wickets',ascending=False).head(50)
            if len(q):
                _plot(px.scatter(q,x='wickets',y='economy',size='matches',hover_name='player_name',
                      title='Bowler Wickets vs Economy Rate (At Least 10 Matches)',
                      labels={'wickets':'Wickets credited','economy':'Runs conceded per over'},color_discrete_sequence=['#E9B869']),'wickets_economy_scatter')
            st.dataframe(bowls.head(30).round(2),hide_index=True,use_container_width=True)
    with tabs[4]:
        section('RECORD PROVENANCE & LIMITATIONS')
        verification=verify_award_integrity(full_awards,full_matches)
        st.json(verification)
        st.markdown('**Source:** supplied Cricsheet IPL JSON match files; `info.player_of_match`, player registry and team lineups. Batting and bowling contributions are computed from per-match deliveries. The trophy table uses recorded IPL final winners. All player groupings use Cricsheet person IDs rather than names alone.')
        st.warning('Match-level captains are not identified in this archive. Best-captain ratings are unavailable until independently verified scorecard captain records are loaded. Player portraits are not bundled without permission.')
        st.caption('Graphs include an explicit Full screen control and an interactive full-browser HTML export. Tables retain Streamlit’s built-in expand functionality.')
