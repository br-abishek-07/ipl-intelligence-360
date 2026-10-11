"""V3E: Verified coaching timeline + retrospective prior-season player-context model research."""
import json
from pathlib import Path
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from dashboard.design import hero,section,kpi,inject_theme
from dashboard.chart_ui import render_chart
from dashboard.analytics import TEAMS
from dashboard.v3d_coaching import coaching_eras,coaching_2026,coach_era_stats
from dashboard.v3e_player_inference import player_probability, prior_registry_2026
from dashboard.v3d_context_inference import context_probability
from dashboard.predict import predict,chase_features
from dashboard.prediction_lab_v2 import supported_chase
ROOT=Path(__file__).resolve().parents[1]

@st.cache_data(show_spinner=False)
def _roster_and_player_names():
    reg=pd.read_csv(ROOT/'data/analytics/player_registry_v2f.csv')
    names=dict(zip(reg.player_id.astype(str),reg.canonical_name.astype(str)))
    lineups=pd.read_csv(ROOT/'data/raw/lineups.csv.gz',usecols=['season_year','team_code','cricsheet_player_id'])
    return names,lineups

@st.cache_data(show_spinner=False)
def _eval():
    return json.loads((ROOT/'reports/v3e/player_aware_holdout_audit.json').read_text())

def page():
    hero('Coaching Timeline & Player-Aware Chase Research',
         'Verified franchise coaching seasons and disciplined prior-season player statistics in an experimental chase model.',
         'IPL INTELLIGENCE 360° / V3-E','COACHING • PLAYER FEATURES • AUDIT')
    tab_coach,tab_research=st.tabs(['🧑‍🏫 Historical Coaching Intelligence','🏏 Prior-Season Player Context Research'])
    with tab_coach:coaching_tab()
    with tab_research:research_tab()

def coaching_tab():
    eras=coaching_eras();franchise=st.selectbox('Franchise for historical coaching review',list(TEAMS),format_func=lambda x:f'{x} — {TEAMS[x][0]}',key='v3e_coaching_team')
    inject_theme(franchise)
    team_eras=eras[eras.team_code==franchise].sort_values('start_season')
    summary=pd.read_csv(ROOT/'data/analytics/team_match_summary.csv',usecols=['team_code','season_year']).drop_duplicates()
    active=sorted(summary[summary.team_code==franchise].season_year.unique().astype(int).tolist())
    verified={int(year):r.head_coach for r in team_eras.itertuples() for year in range(r.start_season,r.end_season+1) if year in active}
    covered=sorted(verified);unknown=sorted(set(active)-set(covered))
    cols=st.columns(4)
    for col,label,val,detail in zip(cols,['Seasons played','Verified coach-season records','Unverified season gaps','Documented head-coach eras'],
                                    [len(active),len(covered),len(unknown),len(team_eras)],
                                    ['IPL seasons in dataset','Individual source-linked periods','Blank rather than inferred','One row per sourced tenure']):
        with col:kpi(label,val,detail)
    st.caption('Historical coach sources vary in strength. Source URLs and documentary notes are visible below. The coaching-era results are associations, not causal claims.')
    timeline=pd.DataFrame([{'Season':int(y),'Coach':verified.get(int(y),'Unverified'),'Verification':'Sourced' if y in verified else 'Missing documentation'} for y in active])
    timeline['Verified']=timeline.Verification.eq('Sourced').astype(int)
    fig=px.bar(timeline,x='Season',y='Verified',color='Verification',color_discrete_map={'Sourced':'#27B795','Missing documentation':'#7D8595'},
               hover_data=['Coach'],title=f'{franchise} — Which IPL Seasons Have Documented Head-Coach Records?')
    fig.update_layout(template='plotly_dark',paper_bgcolor='rgba(0,0,0,0)',height=330,yaxis_title='Coach identified (1=yes; 0=no)',xaxis_dtick=1)
    render_chart(fig,key='v3e_coach_coverage_'+franchise,title=f'{franchise} — Which IPL Seasons Have Documented Head-Coach Records?')
    st.dataframe(timeline[['Season','Coach','Verification']].rename(columns={'Coach':'Documented head coach'}),hide_index=True,use_container_width=True)
    if unknown:st.warning('Still unverified for '+franchise+': '+', '.join(str(x) for x in unknown)+'. These are NOT silently filled.')
    else:st.success('A coach is documented for every season played by this franchise in the current dataset. Source reliability still varies.')
    section('Sourced Head-Coach Periods and Results','Era performance is based on the historical team-match table. Team strength, opponents and squad changes are confounders.')
    stats=coach_era_stats(franchise)
    if not stats.empty:
        view=stats[['coach','start','end','played','decided','wins','titles','win_rate','source_url']].copy()
        view['win_rate']=view.win_rate.map(lambda x:f'{x:.1%}' if pd.notna(x) else 'No decided matches')
        st.dataframe(view.rename(columns={'coach':'Head coach','start':'From','end':'Through','played':'Matches','decided':'Decided','wins':'Wins','titles':'IPL trophies during tenure','win_rate':'Win rate','source_url':'Source link'}),hide_index=True,use_container_width=True)
        fig=px.bar(stats,x='coach',y='win_rate',hover_data=['start','end','decided','wins'],title=f'{franchise} — Decided-Match Win Rate During Documented Coach Eras')
        fig.update_layout(template='plotly_dark',paper_bgcolor='rgba(0,0,0,0)',xaxis_title='Coach (era)',yaxis_title='Win rate',yaxis_tickformat='.0%',height=440)
        render_chart(fig,key='v3e_coach_win_'+franchise,title=f'{franchise} — Decided-Match Win Rate During Documented Coach Eras')
        st.dataframe(team_eras[['start_season','end_season','head_coach','source_url','evidence']].rename(columns={'head_coach':'Head coach','source_url':'Read source','evidence':'Evidence note'}),hide_index=True,use_container_width=True)
    st.download_button('Download verified coach-year coverage (CSV)',timeline.to_csv(index=False),file_name=f'{franchise}_coaching_timeline.csv',mime='text/csv',key='v3e_coach_download')

def research_tab():
    st.warning('EXPERIMENTAL. The existing scoreboard model remains preferred. Prior-season player histories are used as research features only; not independent future-season validation.')
    audit=_eval();checkpoint=st.selectbox('Completed legal overs in chase',[10,15,18],format_func=lambda x:f'{x} overs',key='v3e_player_overs');balls=checkpoint*6
    rec=next(r for r in audit['models'] if r['checkpoint_legal_balls']==balls)
    for col,name,item in zip(st.columns(3),['Original scoreboard accuracy','New player-context accuracy','Matches in retrospective test'],
                             [f"{rec['existing_scoreboard_model']['accuracy']:.1%}",f"{rec['model_with_prior_player_context']['accuracy']:.1%}",rec['test_matches']]):
        with col:kpi(name,item,'2025–2026 matched holdout')
    c1,c2=st.columns(2)
    batting=c1.selectbox('Chasing team',list(TEAMS),key='v3e_player_batting');defending=c2.selectbox('Defending team',[t for t in TEAMS if t!=batting],key='v3e_player_defending')
    inject_theme(batting)
    @st.cache_data(show_spinner=False)
    def venues():return sorted(pd.read_csv(ROOT/'data/analytics/matches_enriched.csv',usecols=['venue_group']).venue_group.dropna().unique().tolist())
    venue=st.selectbox('Ground / venue context',venues(),key='v3e_player_venue')
    cols=st.columns(3)
    target=int(cols[0].number_input('Target to win (runs)',min_value=1,max_value=400,value=185,key='v3e_player_target'))
    runs=int(cols[1].number_input('Runs already scored in chase',min_value=0,max_value=400,value={10:92,15:143,18:164}[checkpoint],key='v3e_player_runs'))
    wickets=int(cols[2].number_input('Wickets lost',min_value=0,max_value=10,value=4,key='v3e_player_wickets'))
    names,lineups=_roster_and_player_names()
    # 2026 *involved* list is not a confirmed playing XI: user must pick historical player actors manually.
    bat_ids=sorted(set(lineups[(lineups.season_year==2026)&(lineups.team_code==batting)].cricsheet_player_id.dropna().astype(str)))
    bowl_ids=sorted(set(lineups[(lineups.season_year==2026)&(lineups.team_code==defending)].cricsheet_player_id.dropna().astype(str)))
    def display(pid):return names.get(str(pid),str(pid))
    if not bat_ids or not bowl_ids:
        st.info('Historical player list unavailable for this team and 2026; player-aware inference cannot be shown for this selection.')
        return
    a,b,c=st.columns(3)
    b1=a.selectbox('Batter on last delivered ball',bat_ids,format_func=display,key='v3e_last_batter')
    n1=b.selectbox('Non-striker on last delivered ball',bat_ids,format_func=display,index=min(1,len(bat_ids)-1),key='v3e_last_non_striker')
    w1=c.selectbox('Bowler on last delivered ball',bowl_ids,format_func=display,key='v3e_last_bowler')
    valid,why=supported_chase(runs,target,wickets,checkpoint)
    if b1==n1:valid=False;why='Select two different batters.'
    if not valid:st.error(why);return
    orig=predict(f'chase_after_{balls}_balls',chase_features(runs,target,wickets,balls))
    context=context_probability(balls,runs,target,wickets,batting,defending,venue)
    candidate=player_probability(balls,runs,target,wickets,batting,defending,venue,b1,n1,w1)
    chart=pd.DataFrame({'Approach':['Existing qualified scoreboard model','Research team+venue model','Research prior-season player model'],
                        'Chase win chance (%)':[orig*100,context*100,candidate*100]})
    fig=px.bar(chart,x='Approach',y='Chase win chance (%)',text='Chase win chance (%)',title='Same Match State — How Player Context Changes the Estimated Chase Probability')
    fig.update_traces(texttemplate='%{y:.1f}%',textposition='outside')
    fig.update_layout(template='plotly_dark',paper_bgcolor='rgba(0,0,0,0)',yaxis_range=[0,110],yaxis_title='Chase win probability (%)',xaxis_title='',height=420)
    render_chart(fig,key='v3e_player_probability_'+str(balls),title='Same Match State — How Player Context Changes the Estimated Chase Probability')
    st.caption('The player actors refer to the LAST completed delivery, not guaranteed participants on the NEXT delivery. Prior-form statistics are from seasons before 2026; no 2026 season aggregate is used.')
    source=prior_registry_2026()
    notes=[]
    for pid,role in [(b1,'batter'),(n1,'batter'),(w1,'bowler')]:
        r,b=source.get((pid,role),(0,0))
        notes.append({'Player':display(pid),'Prior-history role':role,'Prior runs (or bowler charged runs)':r,'Prior balls':b,'History status':'Available' if b else 'No earlier-season history'})
    st.dataframe(pd.DataFrame(notes),hide_index=True,use_container_width=True)
    section('Retrospective model evaluation on exactly the same eligible matches','Player-aware logistic model trained through 2024; no 2025–2026 outcome used in its fit.')
    metrics=[]
    for item in audit['models']:
        for group,label in [('existing_scoreboard_model','Existing scoreboard model'),('existing_team_venue_research_model','Team + venue research'),('model_with_prior_player_context','Player-context research')]:
            m=item[group]
            metrics.append({'Checkpoint':str(item['checkpoint_legal_balls']//6)+' overs','Approach':label,
                            'Accuracy (%)':100*m['accuracy'],'Brier score':m['brier'],'Matches':m['n']})
    evidence=pd.DataFrame(metrics)
    fig=px.bar(evidence,x='Checkpoint',y='Accuracy (%)',color='Approach',barmode='group',title='2025–2026 Chase Prediction Accuracy — Same Matches, Three Methods',text_auto='.1f')
    fig.update_layout(template='plotly_dark',paper_bgcolor='rgba(0,0,0,0)',yaxis_range=[0,105])
    render_chart(fig,key='v3e_player_acc',title='2025–2026 Chase Prediction Accuracy — Same Matches, Three Methods')
    st.dataframe(evidence,hide_index=True,use_container_width=True)
    st.info('Why not deploy? The original scoreboard model wins on accuracy at every checkpoint. The player-context model improves the 10-over Brier score slightly but does not beat the full model across 15/18 overs. The test seasons are not untouched in the project history.')
    st.download_button('Download player-context evaluation audit',json.dumps(audit,indent=2),file_name='V3E_Player_Model_Research_Audit.json',mime='application/json',key='v3e_audit_dl')
