"""IPL 360° V4X: evidence-only research and conservative franchise decision support.
Model artifacts are portable JSON and can infer without scikit-learn.
"""
from __future__ import annotations
import json
from pathlib import Path
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from dashboard.data import ROOT
from dashboard.design import hero,kpi,section
from dashboard.chart_ui import render_chart
from dashboard.views import setup

V=ROOT/'data'/'v4x';REP=ROOT/'reports'/'v4x'

@st.cache_data(show_spinner=False,max_entries=4)
def read_csv(name):return pd.read_csv(V/name)
@st.cache_data(show_spinner=False,max_entries=1)
def info():
    result=json.loads((REP/'model_results.json').read_text())
    audit=json.loads((REP/'paired_match_cluster_audit.json').read_text())
    return result,audit
@st.cache_data(show_spinner=False,max_entries=5)
def model(name):return json.loads((V/(name+'.json')).read_text())
@st.cache_data(show_spinner=False,max_entries=1)
def names():
    df=pd.read_csv(ROOT/'data/analytics/player_registry_v2f.csv')
    return dict(zip(df.player_id.astype(str),df.canonical_name.astype(str)))

def pname(pid):return names().get(str(pid),str(pid))

def infer(frame,name):
    m=model(name);X=frame.reindex(columns=m['features']).apply(pd.to_numeric,errors='coerce').replace([np.inf,-np.inf],np.nan).fillna(0).to_numpy(float)
    a=(X-np.array(m['mean']))/np.where(np.array(m['scale'])==0,1,np.array(m['scale']))
    z=a@np.array(m['coefficients'])+m['intercept']
    if m['task']=='binary':return 1/(1+np.exp(-np.clip(z,-35,35)))
    return z

def simple_theme(fig,accent='#DDBB62'):
    fig.update_layout(template='plotly_dark',paper_bgcolor='rgba(0,0,0,0)',plot_bgcolor='rgba(0,0,0,0)',
        height=385,font_color='#F0F4FA',margin=dict(l=15,r=20,t=68,b=45))
    return fig

def choose_team(d,key):
    t=sorted(d.team_code.unique());return st.selectbox('Franchise',t,key=f'v4x_{key}_team')

def selection(d,key):
    year=st.selectbox('Historical evaluation season',[2026,2025,2024],key=f'v4x_{key}_year')
    q=d[d.season_year==year]
    team=choose_team(q,key)
    q=q[q.team_code==team]
    mi=st.selectbox('Recorded IPL fixture (retrospective replay)',sorted(q.match_id.unique().tolist()),key=f'v4x_{key}_match')
    return q[q.match_id==mi].copy(),year,team,int(mi)

def show_metrics(title,modelkey):
    metrics=info()[0]['model_results'][modelkey]
    data=[]
    for yy,key in [(2024,'validation_2024'),(2025,'holdout_2025'),(2026,'holdout_2026')]:
        m=metrics[key]
        data.append({'Season':yy,'Cases':m['n'],'Accuracy (%)':round(100*m['accuracy'],2),'Repeat-last-match (%)':round(100*m['naive_accuracy'],2),'ROC-AUC':m['auc'],'Balanced accuracy (%)':round(100*m['balanced_accuracy'],2),'Brier':m['brier'],'Majority baseline (%)':round(100*m['majority_accuracy'],2)})
    st.markdown('**'+title+' — held-out test results**')
    st.dataframe(pd.DataFrame(data),use_container_width=True,hide_index=True)
    return pd.DataFrame(data)

def bowling_tab():
    section('BOWLING DEPLOYMENT RESEARCH','Predict the probability an historically eligible bowler is used during the powerplay or death overs.')
    bow=read_csv('bowling_phase_features.csv.gz');show_metrics('All bowling phases combined','bowling_deployment')
    st.caption('Training: seasons through 2023. Validation: 2024. Retrospective holdouts: 2025–26. Eligible candidates come only from earlier team bowling records; not a confirmed current squad.')
    q,year,team,mi=selection(bow,'bowling')
    phase=st.radio('Bowling phase',['powerplay','death'],horizontal=True,key='v4x_bowl_phase')
    q=q[q.phase==phase].copy()
    if q.empty:st.warning('No candidate bowlers in this historical fixture.');return
    q['Probability (%)']=(100*infer(q,'bowling_deployment')).round(1)
    q['Bowler']=q.player_id.map(pname)
    q['Actually used in this phase']=np.where(q.used.astype(bool),'Yes','No')
    q['Used in previous match']=np.where(q.used_last_game.astype(bool),'Yes','No')
    display=q.sort_values('Probability (%)',ascending=False)
    c1,c2,c3=st.columns(3)
    with c1:kpi('Historical Candidate Bowlers',str(len(q)),'Derived from earlier match bowling appearances')
    with c2:kpi('Predicted to Bowl',str((q['Probability (%)']>=50).sum()),'Threshold = 50%')
    with c3:kpi('Actually Bowled',str(int(q.used.sum())),'Observed retrospectively, not an input')
    fig=px.bar(display,x='Probability (%)',y='Bowler',orientation='h',color='Actually used in this phase',
        title=f'{team}: Predicted {phase.title()} Bowling Usage — Before Match {mi}',color_discrete_map={'Yes':'#E0BE67','No':'#5A708C'})
    render_chart(simple_theme(fig),key=f'v4x_bowler_{year}_{team}_{mi}_{phase}',context='Outcome colors use historical results for evaluation; no outcome information enters model inputs.')
    st.dataframe(display[['Bowler','Probability (%)','Used in previous match','Actually used in this phase','used_recent3','avg_phase_balls']].rename(columns={'used_recent3':'Prior 3-Match Phase Usage','avg_phase_balls':'Prior Avg Phase Balls'}),use_container_width=True,hide_index=True)
    st.caption('Not a recommendation of the BEST bowler: this predicts a team’s likely deployment, not expected runs saved or counterfactual win improvement.')
    ci=info()[1]['bowling_'+phase]
    st.markdown(f"**Paired holdout lift versus repeat-last-match:** {ci['delta_pp']:+.2f} percentage points; 95% match-bootstrap interval {ci['bootstrap_95pct_delta_pp'][0]:+.2f} to {ci['bootstrap_95pct_delta_pp'][1]:+.2f} pp across {ci['matches']} matches.")

def participation_tab():
    section('PLAYER APPEARANCE PREDICTION','Match participation, which can include Impact Players. Not a certified starting XI predictor.')
    xi=read_csv('xi_proxy_features.csv.gz');show_metrics('Player appearance prediction','playing_xi_appearance')
    q,year,team,mi=selection(xi,'xi')
    if q.empty:st.warning('No player appearance candidates available.');return
    q['Probability (%)']=100*infer(q,'xi_appearance');q['Player']=q.player_id.map(pname)
    q['Observed match participant']=np.where(q.selected,'Yes','No')
    q=q.sort_values('Probability (%)',ascending=False)
    fig=px.bar(q.head(22),x='Player',y='Probability (%)',color='Observed match participant',
        title=f'{team}: Predicted Match Participation — Historical Fixture {mi}',
        color_discrete_map={'Yes':'#E0BE67','No':'#62758F'})
    render_chart(simple_theme(fig),key=f'v4x_xi_{year}_{team}_{mi}',context='Candidates come from prior appearances, so newly acquired/debut players may not appear.')
    st.dataframe(q[['Player','Probability (%)','prev_match_selected','prev_3_rate','Observed match participant']].rename(columns={'prev_match_selected':'In previous match','prev_3_rate':'Prior 3-match appearance rate'}),hide_index=True,use_container_width=True)
    ci=info()[1]['participation_overall']
    st.warning(f"Model improvement over repeating previous match is only {ci['delta_pp']:+.2f} pp, 95% match-block interval {ci['bootstrap_95pct_delta_pp'][0]:+.2f} to {ci['bootstrap_95pct_delta_pp'][1]:+.2f} pp. No statistically established lift: research only.")

def matchup_tab():
    section('BATTER–BOWLER MATCHUP LAB','Forecast batter runs per next delivery with prior-season player and direct head-to-head evidence.')
    obj=info()[0]['model_results']['matchup_run_risk']
    result=[]
    for year in [2024,2025,2026]:
        d=obj['validation_2024' if year==2024 else f'holdout_{year}']
        result.append({'Year':year,'Deliveries':d['n'],'Run MAE (runs/ball)':d['mae'],'Simple phase MAE':d['baseline_mae'],'RMSE':d['rmse'],'R²':d['r2']})
    st.dataframe(pd.DataFrame(result),use_container_width=True,hide_index=True)
    st.warning('Research only: per-ball MAE is worse than the simple phase-average baseline. This is NOT a validated optimum-bowler or runs-saved recommendation.')
    lookup=read_csv('matchup_2024_2026_point_in_time.csv.gz')
    year=st.selectbox('Season to sample prior-knowledge inputs',[2026,2025,2024],key='v4x_match_year')
    t=lookup[lookup.season_year==year]
    bat=t.groupby('batter_id',as_index=False).agg(balls=('next_ball_runs','size')).query('balls >= 12')
    available=sorted(bat.batter_id.astype(str))
    batter=st.selectbox('Batter',available,format_func=pname,key='v4x_batter')
    bowl=t.groupby('bowler_id',as_index=False).agg(balls=('next_ball_runs','size')).query('balls >= 12')
    players=sorted(bowl.bowler_id.astype(str))
    choice=st.multiselect('Compare bowlers (maximum 4)',players,format_func=pname,default=players[:2],max_selections=4,key='v4x_bowlercompare')
    phase=st.selectbox('Innings phase',[(0,'Powerplay (overs 1–6)'),(1,'Middle overs (7–15)'),(2,'Death overs (16–20)')],format_func=lambda x:x[1],key='v4x_match_phase')[0]
    if not choice:st.info('Select at least one bowler.');return
    bat_row=t[t.batter_id==batter].iloc[0]
    table=[]
    for pid in choice:
        b_row=t[t.bowler_id==pid].iloc[0]
        same=t[(t.batter_id==batter)&(t.bowler_id==pid)]
        if len(same):pair=same.iloc[0]
        else:pair=None
        vals=dict(phase_code=phase,bat_prior_rpb=bat_row.bat_prior_rpb,bowl_prior_rpb=b_row.bowl_prior_rpb,
          bat_prior_boundary=bat_row.bat_prior_boundary,bowl_prior_boundary=b_row.bowl_prior_boundary,
          bat_experience_log=bat_row.bat_experience_log,bowl_experience_log=b_row.bowl_experience_log,
          pair_prior_rpb=pair.pair_prior_rpb if pair is not None else 1.0,
          pair_prior_boundary=pair.pair_prior_boundary if pair is not None else .125,
          pair_experience_log=pair.pair_experience_log if pair is not None else 0.0)
        pred=float(infer(pd.DataFrame([vals]),'matchup_run_risk')[0])
        table.append({'Bowler':pname(pid),'Predicted Batter Runs / Ball':round(pred,3),'Historical Prior Bowler Runs/Ball':round(float(b_row.bowl_prior_rpb),3),'Past Head-to-Head Balls':round(float(np.expm1(vals['pair_experience_log'])),0)})
    df=pd.DataFrame(table).sort_values('Predicted Batter Runs / Ball')
    fig=px.bar(df,x='Bowler',y='Predicted Batter Runs / Ball',title=f'Experimental Expected Runs per Delivery Against {pname(batter)}',color_discrete_sequence=['#DDBB62'])
    render_chart(simple_theme(fig),key=f'v4x_matchup_{year}_{batter}_{phase}',context='Observational conditional expected runs, not a causal forecast of switching bowlers. No confirmed XI, ball sequencing or injuries.')
    st.dataframe(df,hide_index=True,use_container_width=True)

def scouting_tab():
    section('CROSS-LEAGUE SCOUTING & AUCTION READINESS','IPL player strike-rate forecasts with prior IPL, SMAT and BBL form, plus auction data coverage.')
    sc=info()[0]['model_results']['cross_league_scouting'];met=[]
    for yr in [2024,2025,2026]:
        d=sc['validation_2024' if yr==2024 else f'holdout_{yr}']
        met.append({'Season':yr,'Eligible batters':d['n'],'Model SR MAE':d['mae'],'Previous IPL career SR MAE':d['baseline_mae'],'R²':d['r2'],'Test criterion':'minimum 30 balls in target season'})
    st.dataframe(pd.DataFrame(met),hide_index=True,use_container_width=True)
    st.info('Lower MAE is better. A forecast MAE of 25 SR points is not 75% accuracy. Negative R² means the model is weaker than a constant within-season mean.')
    scout=read_csv('scouting_asof_features.csv.gz')
    yr=st.selectbox('Retrospective player season',[2026,2025,2024],key='v4x_scoutyr')
    q=scout[scout.season_year==yr].copy();q['Player']=q.player_id.map(pname)
    all_names=sorted(q.Player.unique())
    selected=st.selectbox('Player (at least 30 recorded IPL batting balls)',all_names,key='v4x_scoutplayer')
    sub=q[q.Player==selected].iloc[0];prediction=float(infer(pd.DataFrame([sub]),'scouting_future_strike_rate')[0])
    c1,c2,c3=st.columns(3)
    with c1:kpi('Model-Predicted IPL Strike Rate',f'{prediction:.1f}','Retrospective forecast using prior seasons')
    with c2:kpi('Actual IPL Season Strike Rate',f'{sub.strike_rate_target:.1f}','Observed after that season')
    with c3:kpi('Previous IPL Career Strike Rate',f'{sub.ipl_prior_sr:.1f}','Baseline available before season')
    x=pd.DataFrame([{'Data stream':'Previous IPL','Previous balls':sub.experience_log and round(np.expm1(sub.experience_log)) or 0},
     {'Data stream':'Prior SMAT','Previous balls':sub.sma_prior_balls},{'Data stream':'Prior BBL','Previous balls':sub.bbl_prior_balls}])
    fig=px.bar(x,x='Data stream',y='Previous balls',title=f'{selected}: Historical Batting Evidence Available Before IPL {yr}',color_discrete_sequence=['#E0BE67'])
    render_chart(simple_theme(fig),key=f'v4x_scout_{yr}_{selected}',context='No 2025–2026 SMAT coverage in the supplied archive; missing evidence is not a zero-quality score.')
    st.markdown('**Auction data: what can be verified**')
    a=info()[0]['model_results']['auction_data_readiness']
    st.caption(f"{a['observed_sales']} observed historical sales/transactions ({min(a['auction_years'])}–{max(a['auction_years'])}). Complete unsold, withdrawn and bid-round outcomes are missing; therefore no sold/unsold or fair-auction-price model has been deployed.")
    hist=pd.read_csv(ROOT/'data/raw/auction_sales.csv')
    hist['amount_crore']=pd.to_numeric(hist.amount_crore,errors='coerce')
    roles=hist.groupby('role',dropna=False).agg(transactions=('amount_crore','size'),median_amount_cr=('amount_crore','median')).reset_index()
    fig=px.bar(roles.sort_values('median_amount_cr'),x='median_amount_cr',y='role',orientation='h',title='Historical Recorded Auction Sale Price by Player Role (Sold Only)',color_discrete_sequence=['#DDBB62'])
    render_chart(simple_theme(fig),key='v4x_auction_roles',context='Descriptive historical transaction amounts in ₹ crore; this is NOT fair market value and does not include unsold players.')
    st.dataframe(roles.rename(columns={'role':'Role','transactions':'Recorded sales','median_amount_cr':'Median recorded sale price (₹ crore)'}),hide_index=True,use_container_width=True)

def run(embedded=False):
    if not embedded: setup()
    hero('Franchise Decision Intelligence Lab','Four rigorously evaluated research tasks: Bowling roles, participant selection, matchup run risk, and scouting intelligence.', 'IPL INTELLIGENCE 360° / V4X RESEARCH','2024 VALIDATION • 2025–26 HISTORICAL HOLDOUTS')
    st.warning('Model governance: These are retrospective research models. Only bowling deployment reliably improves on naive decisions; this does NOT certify future franchise performance. Existing four chase/score models remain the deployed predictors.')
    tabs=st.tabs(['🎯 Bowling Deployment','🧢 Playing XI & Impact Participation','⚔️ Batter–Bowler Matchup','🔎 Cross-League Scouting & Auction','📋 Full Test Results'])
    with tabs[0]:bowling_tab()
    with tabs[1]:participation_tab()
    with tabs[2]:matchup_tab()
    with tabs[3]:scouting_tab()
    with tabs[4]:
        results=info()[0]; st.json(results)
        st.download_button('⬇ Download complete evaluation JSON',data=(REP/'model_results.json').read_bytes(),file_name='IPL_V4X_Model_Test_Results.json',mime='application/json',key='v4x_metrics_dl')
        st.download_button('⬇ Download match-clustered confidence audit',data=(REP/'paired_match_cluster_audit.json').read_bytes(),file_name='IPL_V4X_Paired_Audit.json',mime='application/json',key='v4x_audit_dl')
        st.caption('Model fitting finishes at 2023; 2024 is a validation season; 2025 and 2026 are historical holdouts for this training run, but were investigated during earlier project development. Samples within matches are correlated and cannot be treated as independent.')
