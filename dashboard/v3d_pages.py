"""V3-D sources-first CLT20, coaching timeline, and contextual chase research."""
from pathlib import Path
import json
from functools import lru_cache
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from dashboard.design import hero,kpi,section,inject_theme
from dashboard.chart_ui import render_chart
from dashboard.analytics import TEAMS
from dashboard.predict import chase_features
from dashboard.prediction_lab_v2 import situation_chase, supported_chase
from dashboard.v3d_coaching import clt20,coaching_2026,coaching_eras,coach_era_stats
ROOT=Path(__file__).resolve().parents[1]

@lru_cache(maxsize=1)
def evaluation():return json.loads((ROOT/'reports/v3d/contextual_holdout_comparison.json').read_text(encoding='utf-8'))

from dashboard.v3d_context_inference import context_probability

@st.cache_data(show_spinner=False)
def roster_for_year(year):
    f=pd.read_csv(ROOT/'data/raw/lineups.csv.gz',low_memory=False)
    f=f[f.season_year==year]
    return f

def clt20_page():
    hero('CLT20 & Coaching Intelligence','Separate IPL and Champions League titles, explore sourced 2026 coaching staff, and compare verified historical coaching eras.','IPL INTELLIGENCE 360° / V3-D','HISTORICAL • SOURCED')
    st.caption('CLT20 is a different competition from the IPL. Trophy totals and titles are never mixed silently. Coaching records are linked to public source URLs and are incomplete outside verified periods.')
    allcl=clt20(); snapshots=coaching_2026(); eras=coaching_eras()
    options=['All teams']+list(TEAMS)
    selected=st.selectbox('Select franchise',options,format_func=lambda x:x if x=='All teams' else f'{x} — {TEAMS[x][0]}',key='v3d_coach_team')
    if selected in TEAMS:inject_theme(selected)
    title_rows=allcl if selected=='All teams' else allcl[allcl.champion_ipl_code==selected]
    team_2026=snapshots if selected=='All teams' else snapshots[snapshots.team_code==selected]
    a,b,c,d=st.columns(4)
    with a:kpi('CLT20 championships',len(title_rows),'Distinct from IPL trophies')
    with b:kpi('Historical CLT20 editions',6,'2009–2014, competition discontinued')
    with c:kpi('Verified 2026 head-coach entries',len(team_2026),'Official IPL team pages')
    with d:kpi('Sourced historical coach eras',len(eras) if selected=='All teams' else len(eras[eras.team_code==selected]),'Partial coverage; not inferred')
    tab1,tab2,tab3=st.tabs(['🏆 CLT20 title history','🧑‍🏫 2026 head coaches','📈 Historical coaching eras'])
    with tab1:
        section('Champions League T20 — Winners and Runners-up','Six historical tournaments (2009–2014). Other countries’ teams remain distinct from IPL franchises.')
        data=allcl.assign(season=allcl.season_year.astype(str),edition=1)
        fig=px.bar(data,x='season',y='edition',color='champion',text='champion',title='CLT20 Winners by Tournament Year (2009–2014)')
        fig.update_layout(template='plotly_dark',paper_bgcolor='rgba(0,0,0,0)',height=440,xaxis_title='Tournament season',yaxis_title='Championship edition',showlegend=False)
        fig.update_traces(textposition='outside',cliponaxis=False)
        render_chart(fig,key='v3d_clt20_winners',title='CLT20 Winners by Tournament Year (2009–2014)')
        st.dataframe(allcl[['season_year','champion','runner_up','source_url']].rename(columns={'season_year':'Season','champion':'Champions','runner_up':'Runners-up','source_url':'Evidence URL'}),hide_index=True,use_container_width=True)
        st.info('Chennai Super Kings: 2010 and 2014. Mumbai Indians: 2011 and 2013. CLT20 titles are NOT additional IPL titles.')
        st.download_button('Download verified CLT20 champions (CSV)',data=allcl.to_csv(index=False),file_name='CLT20_2009_2014.csv',mime='text/csv',key='v3d_clt_dl')
    with tab2:
        section('IPL 2026 Head Coach Reference','Historical snapshot sourced from the official IPL team profiles. It does not assert present-day employment after the 2026 season.')
        st.dataframe(team_2026[['team_code','head_coach','season_year','source_url']].rename(columns={'team_code':'Team','head_coach':'Head Coach','season_year':'Season','source_url':'Official IPL Source'}),hide_index=True,use_container_width=True)
        st.caption('Only HEAD COACH roles are shown. Specialist coach and mentor designations require separate, year-specific verification.')
        st.download_button('Download 2026 coach reference (CSV)',data=team_2026.to_csv(index=False),file_name='IPL_2026_Sourced_Head_Coaches.csv',mime='text/csv',key='v3d_coach_2026_dl')
    with tab3:
        section('Verified coaching tenures and team results','Only sourced historical eras are calculated. Missing franchises/years are reported as unavailable, not reconstructed.')
        available=sorted(eras.team_code.unique())
        st.caption('Source-backed historical coach periods now available for: '+', '.join(available)+'. Other team histories are not yet complete.')
        frame=eras if selected=='All teams' else eras[eras.team_code==selected]
        st.dataframe(frame[['team_code','head_coach','start_season','end_season','source_url']].rename(columns={'team_code':'Franchise','head_coach':'Head Coach','start_season':'From','end_season':'To','source_url':'Evidence'}),hide_index=True,use_container_width=True)
        chosen=st.selectbox('Team for verified coaching-era performance',available,index=available.index(selected) if selected in available else 0,key='v3d_coach_era_team')
        stats=coach_era_stats(chosen)
        display_stats=stats[['coach','start','end','played','decided','wins','titles','win_rate','source_url']].copy()
        display_stats['win_rate']=display_stats.win_rate.map(lambda z: f'{z:.1%}' if pd.notna(z) else '—')
        st.dataframe(display_stats.rename(columns={'coach':'Head Coach','start':'From','end':'To','played':'All matches','decided':'Decided matches','wins':'Won','titles':'IPL titles during era','win_rate':'Win rate','source_url':'Source'}),hide_index=True,use_container_width=True)
        if not stats.empty:
            fig=px.bar(stats,x='coach',y='win_rate',hover_data=['start','end','played'],color='coach',title=f'{chosen} — IPL Win Rate During Verified Head-Coach Eras')
            fig.update_layout(template='plotly_dark',paper_bgcolor='rgba(0,0,0,0)',showlegend=False,yaxis_tickformat='.0%',xaxis_title='Coach era',yaxis_title='Decided-match win percentage')
            render_chart(fig,key='v3d_coach_win_era_'+chosen,title=f'{chosen} — IPL Win Rate During Verified Head-Coach Eras')
        st.warning('Era results are descriptive associations, not proof that a coach caused wins. Roster strength, opponent quality, venue, and match-era conditions also change.')
        st.download_button('Download verified coaching eras',data=frame.to_csv(index=False),file_name='Sourced_IPL_coaching_eras.csv',mime='text/csv',key='v3d_coach_era_dl')


def research_page():
    hero('Contextual Chase Intelligence','Evaluate whether batting team, bowling team and venue help predict chase success beyond the scoreboard.','IPL INTELLIGENCE 360° / V3-D','RESEARCH • NOT DEPLOYED')
    st.warning('Research-only model. On held-out 2025–2026 retrospective matches, the original scoreboard-only models performed better. The contextual model is **not** a replacement or newly qualified deployed predictor.')
    d=evaluation(); checkpoint=st.selectbox('Chase checkpoint',[10,15,18],format_func=lambda x:f'After {x} legal overs',key='v3d_chase_checkpoint');balls=6*checkpoint
    row=next(x for x in d['rows'] if x['checkpoint_legal_balls']==balls)
    cols=st.columns(4)
    for col,label,value,note in zip(cols,['Context model accuracy','Existing model accuracy','Context Brier score','Same-match test sample'],
        [f"{row['context_model_test']['accuracy']:.1%}",f"{row['existing_scoreboard_model_same_test_matches']['accuracy']:.1%}",f"{row['context_model_test']['brier']:.3f}",row['test_matches']],
        ['Not promoted','Preferred model','Lower is better','2025–2026 retrospective']):
        with col:kpi(label,value,note)
    left,right=st.columns(2)
    batting=left.selectbox('Team batting second',list(TEAMS),index=0,format_func=lambda x:f'{x} — {TEAMS[x][0]}',key='v3d_context_batting')
    inject_theme(batting)
    bowling=right.selectbox('Team defending target',[t for t in TEAMS if t!=batting],key='v3d_context_bowling')
    @st.cache_data(show_spinner=False)
    def venue_list():
        m=pd.read_csv(ROOT/'data/analytics/matches_enriched.csv')
        return sorted(m.venue_group.dropna().unique().tolist())
    venue=st.selectbox('Match venue',venue_list(),key='v3d_context_venue')
    c1,c2,c3=st.columns(3)
    target=c1.number_input('Target to win (runs)',min_value=1,max_value=400,value=185,key='v3d_c_target')
    runs=c2.number_input('Chasing runs already scored',min_value=0,max_value=400,value={10:90,15:140,18:165}[checkpoint],key='v3d_c_runs')
    wk=c3.number_input('Wickets lost',min_value=0,max_value=10,value=4,key='v3d_c_wickets')
    good,reason=supported_chase(runs,target,wk,checkpoint)
    if good:
        oldname,oldp=situation_chase(runs,target,wk,checkpoint)
        newp=context_probability(balls,runs,target,wk,batting,bowling,venue)
        a,b=st.columns(2)
        with a:st.metric('Existing scoreboard model · winning chance',f'{oldp:.1%}')
        with b:st.metric('New team + venue research model · winning chance',f'{newp:.1%}',delta=f'{100*(newp-oldp):+.1f} percentage points')
        fig=go.Figure(go.Bar(x=['Scoreboard baseline','Team + venue experiment'],y=[100*oldp,100*newp],marker_color=['#EFC26E','#6DBCD3'],text=[f'{oldp:.1%}',f'{newp:.1%}'],textposition='outside'))
        fig.update_layout(title='Chase Win Probability — Same Match State Under Two Research Models',template='plotly_dark',paper_bgcolor='rgba(0,0,0,0)',yaxis_title='Estimated chance of chasing successfully (%)',yaxis_range=[0,110])
        render_chart(fig,key='v3d_context_comparison',title='Chase Win Probability — Same Match State Under Two Research Models')
    else:st.error(reason)
    with st.expander('Optional player context: exploratory only — not fed into either model',expanded=False):
        st.caption('2026 match-participation list, which may include Impact Players. This is for analyst exploration, not a verified live playing XI.')
        lineup=roster_for_year(2026)
        names=[]
        # Raw lineup records may use team_code/player columns, inspect dynamically and disclose missing.
        team_col=next((v for v in ['team_code','team','team_code_context'] if v in lineup.columns),None)
        player_col=next((v for v in ['player','player_name','name'] if v in lineup.columns),None)
        if team_col and player_col:
            bnames=sorted(lineup[lineup[team_col]==batting][player_col].dropna().unique().tolist())
            onames=sorted(lineup[lineup[team_col]==bowling][player_col].dropna().unique().tolist())
            if bnames:
                x,y=st.columns(2)
                x.selectbox('Batter at crease (descriptive only)',bnames,key='v3d_batter_1')
                y.selectbox('Second batter (descriptive only)',bnames,key='v3d_batter_2')
            if onames:st.selectbox('Current bowler (descriptive only)',onames,key='v3d_bowler')
        else:st.info('Player-name column not available in the lineup source; player context cannot be safely shown.')
        st.warning('Player selection DOES NOT alter either probability. We would need temporally valid player features and new testing before using it in predictions.')
    section('Retrospective accuracy on identical match checkpoints','Context model trained through 2024 after development through 2022; existing scoreboard model used its separately fitted training pipeline. Training methods are not identical.')
    comparisons=[]
    for item in d['rows']:
        for model_name,col in [('Original scoreboard model','existing_scoreboard_model_same_test_matches'),('Contextual research model','context_model_test')]:
            comparisons.append({'Checkpoint':f"{int(item['checkpoint_legal_balls'])//6} overs",'Model':model_name,'Accuracy (%)':100*item[col]['accuracy'],'Brier':item[col]['brier'],'Matches':item['test_matches']})
    frame=pd.DataFrame(comparisons)
    fig=px.bar(frame,x='Checkpoint',y='Accuracy (%)',color='Model',barmode='group',title='Existing vs Team-and-Venue Chase Models — 2025–2026 Same-Match Accuracy',text_auto='.1f')
    fig.update_layout(template='plotly_dark',paper_bgcolor='rgba(0,0,0,0)',yaxis_range=[0,105])
    render_chart(fig,key='v3d_model_accuracy',title='Existing vs Team-and-Venue Chase Models — 2025–2026 Same-Match Accuracy')
    st.dataframe(frame,hide_index=True,use_container_width=True)
    st.caption('A player-aware probability is not reported because robust, past-only player form and actual chase-context identities have not been validated. Scores are retrospective and subject to further untouched-season testing.')
    st.download_button('Download V3-D contextual evaluation results',data=json.dumps(d,indent=2),mime='application/json',file_name='V3D_contextual_model_comparison.json',key='v3d_eval_download')
