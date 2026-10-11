"""V2-J: transparent retrospective research into the user's earlier live chase engine.
No uploaded in-sample probabilities or notebook credentials are shipped.
The new research candidate is NOT a deployed/qualified prediction model.
"""
from functools import lru_cache
from pathlib import Path
import json
import plotly.graph_objects as go
import streamlit as st
from dashboard.chart_ui import render_chart
from dashboard.design import section, kpi

PATH=Path(__file__).resolve().parents[1]/'research'/'live_chase_research_metrics.json'

@lru_cache(maxsize=1)
def load_evidence():
    doc=json.loads(PATH.read_text(encoding='utf-8'))
    if doc['test_matches'] <= 0 or doc['train_matches'] <= 0 or doc['calibration_matches'] <= 0:
        raise ValueError('Missing match-disjoint research evidence')
    for label in ('rebuilt_model_all_states','uploaded_csv_in_sample_predictions'):
        v=doc[label]
        if not 0 <= v['accuracy'] <= 1 or not 0 <= v['brier'] <= 1:
            raise ValueError('Invalid research metrics')
    return doc

def render():
    section('EARLIER LIVE MODEL — INDEPENDENT CODE AUDIT',
            'What we can safely learn from the previous IPL notebook without promoting its leaked results.')
    st.warning('**Research only.** This page does not deploy or use the older notebook model. Its 0.9288 ROC-AUC was computed on training rows; it is not independent accuracy. The 2025–2026 seasons have also influenced earlier research decisions.')
    d=load_evidence()
    for col,(label,value,note) in zip(st.columns(4),[
        ('Training matches',f"{d['train_matches']:,}",'Through 2022'),
        ('Calibration matches',f"{d['calibration_matches']:,}",'2023–2024; separate matches'),
        ('Retrospective test matches',f"{d['test_matches']:,}",'2025–2026; already examined'),
        ('Corrected model state accuracy',f"{d['rebuilt_model_all_states']['accuracy']:.1%}",'Repeated states; correlated observations'),
    ]):
        with col:kpi(label,value,note)
    st.markdown('#### Fixed-over checkpoint outcomes (one state per eligible match)')
    checkpoints=[('After 10 completed overs','after_10_overs'),
                 ('After 15 completed overs','after_15_overs'),
                 ('After 18 completed overs','after_18_overs')]
    rows=[]
    for label,code in checkpoints:
        rec=d['checkpoints'][code]
        rows.append({'checkpoint':label,'accuracy':rec['rebuilt']['accuracy']*100,
                     'majority':rec['rebuilt']['majority_accuracy']*100,
                     'n':rec['rebuilt']['n'], 'auc':rec['rebuilt']['auc'],
                     'brier':rec['rebuilt']['brier']})
    fig=go.Figure()
    fig.add_bar(name='Corrected research model',x=[r['checkpoint'] for r in rows],
                y=[r['accuracy'] for r in rows],marker_color='#67CBE6',
                text=[f"{r['accuracy']:.1f}%" for r in rows],textposition='outside')
    fig.add_bar(name='Majority-class baseline',x=[r['checkpoint'] for r in rows],
                y=[r['majority'] for r in rows],marker_color='#E8BE73')
    fig.update_layout(title='Corrected Live Chase Accuracy Compared with Naive Baselines by Over',
                      yaxis=dict(title='Retrospective classification accuracy (%)',range=[0,105]),
                      xaxis_title='Second-innings checkpoint',barmode='group',
                      template='plotly_dark',height=450,paper_bgcolor='rgba(0,0,0,0)',
                      plot_bgcolor='rgba(0,0,0,0)',legend=dict(orientation='h',y=1.17))
    render_chart(fig,key='v2j_live_research_checkpoint_accuracy',
                 title='Corrected Live Chase Accuracy Compared with Naive Baselines by Over',
                 context='Different eligibility cohorts: 111 matches at 10 overs, 106 at 15 overs, 80 at 18 overs. Do not compare these as one identical match set.')
    st.markdown('#### What was wrong with the notebook predictions?')
    a,b=st.columns(2)
    with a:
        st.metric('Wrong season-year entries',f"{d['fixed_wrong_season_year_rows_full_active_dataset']:,}")
    with b:
        st.metric('Wrong wickets-in-hand entries',f"{d['fixed_wrong_wickets_in_hand_rows_full_active_dataset']:,}")
    st.markdown("The notebook’s later model trained and predicted on overlapping rows, and another experiment used random delivery-row splits that mixed deliveries from the same match into training and testing. The rebuilt experiment uses date-separated matches and corrected state variables; it is *still not* a fresh, untouched future-season evaluation.")
    st.info("**Deployment decision:** Keep the existing four match-checkpoint models unchanged. The rebuilt live model remains an optional, separately validated research candidate. It has not passed the capstone’s future-blind validation requirement.")
    st.download_button('Download live-model audit results (JSON)',
                       data=json.dumps(d,indent=2),file_name='IPL360_live_research_metrics.json',
                       mime='application/json',key='v2j_research_evidence_download')
    st.caption('Reproduction script and full cell-by-cell code audit: research/retrain_live_research.py and research/original_notebook_review.md. Original notebook with database credentials is deliberately excluded.')
