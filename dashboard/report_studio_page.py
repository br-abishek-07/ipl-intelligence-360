"""V3-F premium sports analyst report generator and evidence exports."""
from __future__ import annotations
import pandas as pd
import plotly.express as px
import streamlit as st
from dashboard.analytics import TEAMS,ALL_TEAMS
from dashboard.data import load
from dashboard.design import hero,kpi,section,inject_theme
from dashboard.chart_ui import render_chart
from dashboard.franchise_analytics import TeamSelection
from dashboard.analyst_reports import build_snapshot,generate_pdf,evidence_zip
from dashboard.views import setup

@st.cache_data(show_spinner=False)
def _load_report_tables():
    return {name:load(name) for name in ('matches','team_matches','innings','phase_match','bat_match','bowl_match')}


def run():
    setup()
    data=_load_report_tables()
    allteams=sorted(TEAMS.keys(),key=lambda c:TEAMS[c][0])
    code=st.sidebar.selectbox('Select franchise',allteams,format_func=lambda c:f'{TEAMS[c][0]} ({c})',key='v3f_franchise')
    inject_theme(code)
    hero(f'{TEAMS[code][0]} | Sports Analyst Report Studio',
         'Build a sourced franchise report from synchronized IPL filters, then export a presentation-ready PDF and its underlying match evidence.',
         'IPL 360 / V3-F',f'{code} • REPORT STUDIO',team=code)
    tm=data['team_matches'];team=tm[tm.team_code==code].copy()
    years=sorted(set(int(y) for y in team.season_year.dropna()))
    mode=st.sidebar.radio('Season selection',['All seasons','Single season','Season range'],key='v3f_season_mode')
    if mode=='All seasons': y0,y1=years[0],years[-1]
    elif mode=='Single season':
        y0=y1=int(st.sidebar.selectbox('IPL season',years,index=len(years)-1,key='v3f_exact_year'))
    else:
        y0,y1=st.sidebar.slider('IPL season interval',min_value=years[0],max_value=years[-1],
                 value=(years[0],years[-1]),key='v3f_interval')
    opponents=st.sidebar.multiselect('Opposition franchises',sorted(team.opponent_code.dropna().unique()),
                       format_func=lambda c:ALL_TEAMS.get(c,c),key='v3f_opponents')
    venues=st.sidebar.multiselect('Stadiums',sorted(team.venue_group.dropna().unique()),key='v3f_venues')
    stages=st.sidebar.multiselect('Match stage',sorted(team.match_type.dropna().unique()),key='v3f_stages')
    outcome=st.sidebar.selectbox('Match result',['All results','Won','Lost','No result'],key='v3f_outcome')
    role=st.sidebar.selectbox('Innings role',['Both innings roles','Batted first','Chased'],key='v3f_role')
    toss=st.sidebar.selectbox('Toss result',['All toss outcomes','Won toss','Lost toss'],key='v3f_toss')
    sel=TeamSelection(code,int(y0),int(y1),tuple(opponents or ()),tuple(venues or ()),tuple(stages or ()),outcome,role,toss)
    try:
        snap=build_snapshot(sel,**data)
    except ValueError as exc:
        st.warning(f'Nothing to report: {exc}. Adjust your filters.');return
    st.caption(f'{len(snap.matches)} matches match the selected filters. All report visuals and leaderboard records use exactly these matches. IPL trophy totals are all-time and separately labeled.')
    s=snap.stats
    cards=[('Matches in selection',str(s['matches']),'Eligible team matches'),
           ('Matches won',str(s['wins']),'Match outcomes after Super Overs, if applicable'),
           ('Match win percentage',f'{s["win_pct"]:.1f}%' if pd.notna(s['win_pct']) else '—','Decided matches only'),
           ('All-time IPL titles',str(len(snap.all_time_titles)),'Not changed by page filters'),
           ('Runs scored',f'{s["runs_scored"]:,}','Regulation innings in selection'),
           ('Team batting runs per over',f'{s["batting_rr"]:.2f}' if pd.notna(s['batting_rr']) else '—','Per six legal balls'),
           ('Wickets taken',str(s['wickets_taken']),'Selected match deliveries'),
           ('Bowling runs conceded per over',f'{s["bowling_rr"]:.2f}' if pd.notna(s['bowling_rr']) else '—','Per six legal balls')]
    for i in (0,4):
        row=st.columns(4)
        for col,(lab,val,note) in zip(row,cards[i:i+4]):
            with col:kpi(lab,val,note)
    if snap.is_small_sample:
        st.warning(f'Only {s["decided"]} decided matches in this selection. Avoid strong conclusions from small samples.')
    t1,t2,t3=st.tabs(['📊 Executive summary','🏏 Batting, bowling and rivals','📥 Export verified report'])
    with t1:
        section('SEASON RESULTS | DECIDED MATCHES','Match wins and losses in the selected season window.')
        if not snap.seasons.empty:
            melted=snap.seasons.melt(id_vars=['season_year'],value_vars=['wins','losses'],var_name='Result',value_name='Matches')
            fig=px.bar(melted,x='season_year',y='Matches',color='Result',barmode='group',
                       title='Matches Won and Lost by IPL Season',color_discrete_sequence=['#49C9A1','#F28184'])
            render_chart(fig,key=f'v3f_{code}_season_wins_losses')
        else:st.info('No decided matches in this selection.')
        section('SPORTS ANALYST FINDINGS','Interpretations are conditional on the selected match sample.')
        for note in snap.notes:st.markdown('- '+note)
    with t2:
        left,right=st.columns(2)
        with left:
            if len(snap.batting):
                fig=px.bar(snap.batting.head(12).sort_values('runs'),x='runs',y='player_name',orientation='h',
                           title='Top Run Scorers in the Selected Matches',labels={'runs':'Runs scored','player_name':'Batter'})
                render_chart(fig,key=f'v3f_{code}_batters')
        with right:
            if len(snap.bowling):
                fig=px.bar(snap.bowling.head(12).sort_values('wickets'),x='wickets',y='player_name',orientation='h',
                           title='Most Wickets Taken in the Selected Matches',labels={'wickets':'Wickets','player_name':'Bowler'})
                render_chart(fig,key=f'v3f_{code}_bowlers')
        if len(snap.bat_phase):
            fig=px.bar(snap.bat_phase,x='phase',y='run_rate',title='Team Batting Run Rate by Innings Phase',
                       labels={'phase':'Innings phase','run_rate':'Runs scored per over'})
            render_chart(fig,key=f'v3f_{code}_batting_phase')
        if len(snap.opponents):
            fig=px.bar(snap.opponents.head(10),x='name',y='win_pct',title='Match Win Percentage Against Each Opponent',
                       labels={'name':'Opponent','win_pct':'Wins per 100 decided matches'})
            render_chart(fig,key=f'v3f_{code}_rivals')
        st.caption('Opponent percentages may be based on very different sample sizes; consult the evidence tables before drawing conclusions.')
    with t3:
        st.markdown('### Generate an offline sports analyst report')
        st.write('The PDF includes franchise KPIs, a season trend, batting/bowling leaders, innings-phase evidence, opponents, sports-analyst interpretation, and a method/source appendix.')
        st.caption('The companion Evidence ZIP contains every selected match ID, computed phase tables, player rankings, and a JSON manifest recording the exact filters.')
        with st.expander('Preview selected match evidence',expanded=False):
            st.dataframe(snap.matches[['match_id','match_date','season_year','opponent_code','venue_group','match_type','won','is_decided']].head(100),use_container_width=True)
        # Compute on request so heavy PDF generation does not occur on every slider change.
        if st.button('🖨 Prepare PDF and Evidence ZIP',type='primary',key='v3f_prepare'):
            with st.spinner('Generating filtered evidence and PDF...'):
                pdf=generate_pdf(snap)
                evidence=evidence_zip(snap,pdf)
                st.session_state['v3f_report_bytes']=(pdf,evidence,sel)
        if 'v3f_report_bytes' in st.session_state:
            pdf,z,generated_sel=st.session_state['v3f_report_bytes']
            if generated_sel==sel:
                a,b=st.columns(2)
                with a:st.download_button('⬇ Download analyst PDF',pdf,file_name=f'IPL360_{code}_Analyst_Report.pdf',mime='application/pdf',key='v3f_pdf')
                with b:st.download_button('⬇ Download PDF + raw evidence ZIP',z,file_name=f'IPL360_{code}_Evidence_Bundle.zip',mime='application/zip',key='v3f_evidence')
                st.success('Report generated from the current selection.')
            else:st.info('Filters have changed. Click Prepare again to regenerate the matching report.')
