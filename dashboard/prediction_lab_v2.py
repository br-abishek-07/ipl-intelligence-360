"""V2-G Prediction Centre: explainable *retrospective* IPL checkpoint forecasts.

No model retraining, no external APIs, no implied live data. Model features, fits,
training periods and phase-specific qualifying gate remain untouched. Public
widget inputs are converted by dashboard.predict functions unchanged.
"""
from __future__ import annotations

from functools import lru_cache
import json
import math
from pathlib import Path

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from dashboard.chart_ui import render_chart
from dashboard.design import hero, kpi, section
from dashboard.predict import chase_features, total_features, predict

ROOT = Path(__file__).resolve().parents[1]
GOLD = '#F0B95C'
CYAN = '#67CBE6'
GREEN = '#65D8AC'
RED = '#F28E97'
BG = '#0A1020'
MUTED = '#A8B9CF'
MODEL_INFO = {
    'chase_after_60_balls': ('Chase Success · After 10 Overs', 'Chasing team eventually wins', 'Second innings, 60 legal balls'),
    'chase_after_90_balls': ('Chase Success · After 15 Overs', 'Chasing team eventually wins', 'Second innings, 90 legal balls'),
    'chase_after_108_balls': ('Chase Success · After 18 Overs', 'Chasing team eventually wins', 'Second innings, 108 legal balls'),
    'first_innings_180_after_60_balls': ('First Innings · 180+ After 10 Overs', 'Innings eventually scores at least 180', 'First innings, 60 legal balls'),
}

@lru_cache(maxsize=1)
def report():
    return json.loads((ROOT/'model_reports'/'model_gate_report.json').read_text(encoding='utf-8'))


def qualified_models():
    from dashboard.predict import _qualified
    accepted = _qualified()
    return {m['name']:m for m in report()['models'] if m.get('gate_passed') and m['name'] in accepted and m['name'] in MODEL_INFO}


@lru_cache(maxsize=4)
def read_holdout(name):
    if name not in qualified_models():
        raise ValueError('Unqualified model or missing holdout record')
    path = ROOT/'model_reports'/'holdout_predictions'/f'{name}.csv.gz'
    df = pd.read_csv(path)
    required={'match_id','season_year','observed_outcome','probability'}
    if not required.issubset(df.columns) or df[list(required)].isna().any().any():
        raise ValueError(f'Invalid holdout columns for {name}')
    if not df.observed_outcome.isin([0,1]).all() or not df.probability.between(0,1).all():
        raise ValueError('Invalid model evaluation probabilities or targets')
    if df.match_id.duplicated().any():
        raise ValueError('Multiple observations per match found in checkpoint holdout')
    return df


def confusion_counts(data, cutoff=0.5):
    """Use strict >? No: sklearn and the original baseline use >=0.5."""
    actual = data.observed_outcome.to_numpy(dtype=int)
    pred = (data.probability.to_numpy(dtype=float) >= cutoff).astype(int)
    return {
        'tp':int(((actual==1)&(pred==1)).sum()),
        'tn':int(((actual==0)&(pred==0)).sum()),
        'fp':int(((actual==0)&(pred==1)).sum()),
        'fn':int(((actual==1)&(pred==0)).sum()),
    }


def evaluation(data, cutoff=0.5):
    counts=confusion_counts(data,cutoff)
    n=len(data)
    y=data.observed_outcome.to_numpy(dtype=int)
    p=data.probability.to_numpy(dtype=float)
    tp,tn,fp,fn=(counts[z] for z in ['tp','tn','fp','fn'])
    return {**counts,'n':n,'accuracy':(tp+tn)/max(n,1),
            'precision':tp/max(1,tp+fp),'recall':tp/max(1,tp+fn),
            'specificity':tn/max(1,tn+fp),
            'balanced_accuracy':.5*(tp/max(1,tp+fn)+tn/max(1,tn+fp)),
            'brier':float(np.mean((p-y)**2)),
            'majority_accuracy':float(max(y.mean(),1-y.mean()))}


def supported_chase(score,target,wickets,overs):
    """Strict checkpoint and unfinished regulation innings; no guessed projections."""
    if overs not in (10,15,18): return False,'Only 10, 15 and 18 completed legal overs are supported.'
    if any(isinstance(v,bool) for v in (score,target,wickets)):
        return False,'Please enter numeric match-state values.'
    if not 0 <= score < target or target < 1:
        return False,'The chasing side must still need runs to win (score below target).'
    if not 0 <= wickets < 10:
        return False,'Prediction requires an active chase with fewer than ten wickets down.'
    if score < 0 or target > 400 or score > 400:
        return False,'State outside supported input boundaries.'
    return True,''


def supported_total(score,wickets):
    if not 0 <= score < 180:
        return False,'The first innings must be active and below 180 runs after 10 overs.'
    if not 0 <= wickets < 10:
        return False,'Prediction requires an active innings with fewer than ten wickets down.'
    return True,''


def situation_chase(score,target,wickets,overs):
    good,why=supported_chase(score,target,wickets,overs)
    if not good: raise ValueError(why)
    name=f'chase_after_{overs*6}_balls'
    value=predict(name,chase_features(score,target,wickets,overs*6))
    return name,value


def situation_total(score,wickets):
    good,why=supported_total(score,wickets)
    if not good: raise ValueError(why)
    name='first_innings_180_after_60_balls'
    return name,predict(name,total_features(score,wickets))


def _base_fig(fig,height=350):
    fig.update_layout(template='plotly_dark',paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',font=dict(color='#E9F2FE',size=12),
        margin=dict(l=45,r=35,t=68,b=52),height=height,
        legend=dict(orientation='h',yanchor='bottom',y=1.02,xanchor='left',x=0))
    return fig


def gauge(probability, label):
    fig=go.Figure(go.Indicator(mode='gauge+number', value=round(100*probability,2),
        number={'suffix':'%','font':{'size':42,'color':'#F3F8FF'}},
        title={'text':label,'font':{'size':15,'color':MUTED}},
        gauge={'axis':{'range':[0,100],'tickwidth':1,'tickcolor':'#9AB3CC'},
               'bar':{'color':CYAN,'thickness':.24},'bgcolor':'rgba(22,38,62,.7)',
               'bordercolor':'rgba(200,215,230,.15)',
               'steps':[{'range':[0,50],'color':'rgba(243,142,151,.14)'},
                        {'range':[50,100],'color':'rgba(101,216,172,.14)'}],
               'threshold':{'line':{'color':GOLD,'width':3},'thickness':.5,'value':50}}))
    fig.update_layout(title=f'{label} — Estimated Probability (Not a Guarantee)')
    return _base_fig(fig,320)


def chase_sensitivity(score,target,wickets,overs):
    """Counterfactual *model responses*; not actual feature attribution."""
    records=[]
    for delta in [-24,-18,-12,-6,0,6,12,18,24]:
        candidate=score+delta
        ok,_=supported_chase(candidate,target,wickets,overs)
        if ok:
            _,p=situation_chase(candidate,target,wickets,overs)
            records.append({'Runs at checkpoint':candidate,'Predicted chase win probability':p*100,
                            'Scenario': 'Current input' if delta==0 else ('+' if delta>0 else '')+str(delta)+' runs'})
    return pd.DataFrame(records)


def chase_wicket_curve(score,target,wickets,overs):
    records=[]
    for wk in range(0,10):
        _,p=situation_chase(score,target,wk,overs)
        records.append({'Wickets lost':wk,'Predicted chase win probability':p*100})
    return pd.DataFrame(records)


def total_sensitivity(score,wickets):
    records=[]
    for s in range(max(0,score-25),min(179,score+25)+1,5):
        for w in range(0,10):
            _,p=situation_total(s,w)
            records.append({'Runs at 10 overs':s,'Wickets lost':w,'180+ probability':100*p})
    return pd.DataFrame(records)


def _model_score_ribbon(name):
    if not getattr(getattr(st, 'session_state', None), 'get', lambda *_: False)('ipl_research_mode', False):
        return
    model=qualified_models()[name]
    hold=model['holdout']
    baseline=model['baseline']['majority_accuracy']
    for col,(label,value,note) in zip(st.columns(4,gap='small'),[
        ('Retrospective Test Accuracy',f"{hold['accuracy']:.1%}",'Season 2025–2026'),
        ('Majority-Class Baseline',f'{baseline:.1%}','Always choose common class'),
        ('ROC-AUC',f"{hold['auc']:.3f}",'Ranking skill, 0.50 is chance'),
        ('Independent Test Matches',f"{model['independent_matches']:,}",'Only matches reaching this checkpoint')]):
        with col:kpi(label,value,note)
    st.caption('The historical test is not a future-season guarantee. Scores apply only to the eligible match-state cohort.')


def _analyst_chase(score,target,wickets,overs,p):
    needed=target-score
    remain=120-overs*6
    required=6*needed/remain
    actual=score*6/(overs*6)
    st.markdown('#### 🧠 Cricket analyst interpretation')
    st.markdown(f'**Match equation:** {needed} runs required from {remain} legal balls, '
        f'with {10-wickets} wickets available. Required scoring rate is **{required:.2f} per over** '
        f'compared with the current rate of **{actual:.2f}**.')
    if required>12:
        text='This is a demanding required rate, but successful chases are still possible; no pitch or player context has been supplied.'
    elif required<=7:
        text='The chase requires a relatively modest remaining scoring rate. Wicket resources and opposition bowling still matter.'
    else:
        text='The chase requires sustained scoring. Future wickets and boundary frequency could change the situation quickly.'
    st.info(text)
    st.caption('The probability is generated from current scoreboard features. This text explains the match equation; it is NOT an explanation of the model’s internal feature importance or a tactical guarantee.')


def _analyst_total(score,wickets,p):
    required=180-score
    rate=required/10
    st.markdown('#### 🧠 Cricket analyst interpretation')
    st.markdown(f'To reach **180 runs**, the batting side needs **{required} runs in the final 10 overs** '
                f'({rate:.2f} runs per over), with **{10-wickets} wickets available**.')
    st.caption('Projection is a probability of crossing 180, not a predicted final score. Opponent quality, pitch, and batting order are not modeled here.')


def _probability_chart(prob,model_name,key):
    _,outcome,_=MODEL_INFO[model_name]
    render_chart(gauge(prob,f'Probability: {outcome}'),key=key,
                 title=f'Estimated Probability of {outcome} — Current Match State',
                 context='Conditional forecast at this exact checkpoint. An estimated 80% probability does not imply 80% certainty or 80% model accuracy.')


def chase_tab():
    section('CHASE PROBABILITY STUDIO','Enter a scoreboard state exactly after 10, 15, or 18 legal overs of a normal 20-over chase.')
    a,b,c,d=st.columns(4)
    overs=a.selectbox('Chase overs completed',[10,15,18],key='v2g_ch_overs')
    score=b.number_input('Chasing team runs',min_value=0,max_value=350,value=92,step=1,key='v2g_ch_score')
    target=c.number_input('Winning target (runs)',min_value=1,max_value=400,value=181,step=1,key='v2g_ch_target')
    wickets=d.number_input('Wickets lost in chase',min_value=0,max_value=10,value=3,step=1,key='v2g_ch_wickets')
    ok,reason=supported_chase(score,target,wickets,overs)
    if not ok:
        st.error(reason+' No prediction shown for an unsupported or already-completed state.')
        return
    name,prob=situation_chase(score,target,wickets,overs)
    _model_score_ribbon(name)
    left,right=st.columns([1,1],gap='large')
    with left:
        _probability_chart(prob,name,'v2g_chase_gauge')
        st.caption(f'Model: {MODEL_INFO[name][0]} · Eligible chases that reach {overs} overs; not shortened matches.')
    with right:
        _analyst_chase(score,target,wickets,overs,prob)
        st.markdown('**Interpret the model output**')
        st.metric('Chasing side · estimated chance',f'{prob:.1%}')
        st.metric('Defending side · complementary chance',f'{1-prob:.1%}')
        st.caption('Complement applies only to decisive matches represented in the binary training target. No separate draw/no-result probability is estimated.')
    section('WHAT-IF ANALYSIS','Change one scoreboard component while keeping the checkpoint fixed. These are model sensitivity experiments, not causal forecasts.')
    l,r=st.columns(2,gap='large')
    runs=chase_sensitivity(score,target,wickets,overs)
    with l:
        fig=go.Figure()
        fig.add_scatter(x=runs['Runs at checkpoint'],y=runs['Predicted chase win probability'],mode='lines+markers',
                        line=dict(color=CYAN,width=3),marker=dict(size=9),name='Model prediction')
        fig.add_vline(x=score,line_dash='dash',line_color=GOLD,
                      annotation_text='Current score',annotation_position='top left')
        fig.update_layout(title='Chase Win Probability as Checkpoint Runs Change',
                          xaxis_title=f'Runs scored at exactly {overs} overs',yaxis_title='Predicted chance of winning (%)',
                          yaxis_range=[0,100])
        render_chart(_base_fig(fig),key='v2g_chase_runs_sensitivity',title='Chase Win Probability as Checkpoint Runs Change')
    wk=chase_wicket_curve(score,target,wickets,overs)
    with r:
        fig=go.Figure(go.Bar(x=wk['Wickets lost'],y=wk['Predicted chase win probability'],
                             marker_color=[GOLD if int(w)==wickets else '#2F9ACB' for w in wk['Wickets lost']],
                             name='Model prediction'))
        fig.update_layout(title='Chase Win Probability by Wickets Lost at Same Score',
                          xaxis_title='Wickets already lost',yaxis_title='Predicted chance of winning (%)',
                          yaxis_range=[0,100])
        render_chart(_base_fig(fig),key='v2g_chase_wicket_sensitivity',
                     title='Chase Win Probability by Wickets Lost at Same Score')
    st.download_button('⬇ Export this chase scenario (JSON)',key='v2g_export_chase',mime='application/json',
        data=json.dumps({'checkpoint_overs':overs,'runs':score,'target':target,'wickets':wickets,
                          'model':name,'estimated_probability':prob,'experimental':True},indent=2),
        file_name='IPL360_chase_scenario.json')


def total_tab():
    section('180+ FIRST-INNINGS SCENARIO','Use the precise 10-over checkpoint, while the innings is still active and below 180 runs.')
    a,b=st.columns(2)
    score=a.number_input('First-innings runs after 10 overs',min_value=0,max_value=300,value=84,step=1,key='v2g_total_runs')
    wickets=b.number_input('First-innings wickets lost after 10 overs',min_value=0,max_value=10,value=2,step=1,key='v2g_total_wickets')
    ok,reason=supported_total(score,wickets)
    if not ok:
        st.error(reason+' This model cannot validly predict an already achieved threshold or completed innings.')
        return
    name,prob=situation_total(score,wickets)
    _model_score_ribbon(name)
    left,right=st.columns(2,gap='large')
    with left:_probability_chart(prob,name,'v2g_total_gauge')
    with right:
        _analyst_total(score,wickets,prob)
        st.metric('Estimated probability of 180 or more',f'{prob:.1%}')
        st.metric('Estimated probability of finishing below 180',f'{1-prob:.1%}')
    section('180+ PROBABILITY RESPONSE MAP','Each cell recalculates the trained model for hypothetical runs and wickets at 10 overs.')
    sens=total_sensitivity(score,wickets)
    pts=sens.pivot(index='Wickets lost',columns='Runs at 10 overs',values='180+ probability').sort_index(ascending=False)
    fig=go.Figure(go.Heatmap(x=pts.columns,y=pts.index,z=pts.values,
               colorscale=[[0,'#152B48'],[.5,'#3877B9'],[1,'#F0B95C']],zmin=0,zmax=100,
               colorbar=dict(title='Probability (%)'),hovertemplate='Runs: %{x}<br>Wickets lost: %{y}<br>Probability: %{z:.1f}%<extra></extra>'))
    fig.update_layout(title='180+ Probability by Runs and Wickets at the 10-Over Mark',
                      xaxis_title='Runs scored after 10 overs',yaxis_title='Wickets lost',height=420)
    render_chart(_base_fig(fig,420),key='v2g_total_heatmap',
                 title='180+ Probability by Runs and Wickets at the 10-Over Mark')
    st.caption('Heatmap points are counterfactual model inputs; some unusual score–wicket combinations may be uncommon in historical cricket.')


def compare_tab():
    section('CHASE SCENARIO COMPARISON','Compare two possible scoreboards at the SAME chase checkpoint and target. Neither scenario is a prediction of what happens next.')
    o,t=st.columns(2)
    overs=o.selectbox('Shared completed chase overs',[10,15,18],index=0,key='v2g_cmp_overs')
    target=t.number_input('Shared target to win',min_value=1,max_value=400,value=181,key='v2g_cmp_target')
    a,b=st.columns(2,gap='large')
    with a:
        st.markdown('#### Scenario A')
        sa=st.number_input('A · Runs scored',min_value=0,max_value=350,value=90,key='v2g_cmp_a_runs')
        wa=st.number_input('A · Wickets lost',min_value=0,max_value=10,value=2,key='v2g_cmp_a_wk')
    with b:
        st.markdown('#### Scenario B')
        sb=st.number_input('B · Runs scored',min_value=0,max_value=350,value=100,key='v2g_cmp_b_runs')
        wb=st.number_input('B · Wickets lost',min_value=0,max_value=10,value=4,key='v2g_cmp_b_wk')
    good_a,why_a=supported_chase(sa,target,wa,overs)
    good_b,why_b=supported_chase(sb,target,wb,overs)
    if not (good_a and good_b):
        st.warning('Both states must represent active, unfinished chases. '+(why_a if not good_a else why_b))
        return
    _,pa=situation_chase(sa,target,wa,overs)
    name,pb=situation_chase(sb,target,wb,overs)
    cols=st.columns(3)
    for col,(label,val,note) in zip(cols,[
        ('Scenario A · Win Probability',f'{pa:.1%}',f'{target-sa} runs needed · {10-wa} wickets remaining'),
        ('Scenario B · Win Probability',f'{pb:.1%}',f'{target-sb} runs needed · {10-wb} wickets remaining'),
        ('B Minus A · Probability Gap',f'{100*(pb-pa):+.1f} pp','Descriptive model difference, not causal uplift')]):
        with col:kpi(label,val,note)
    fig=go.Figure(go.Bar(x=['Scenario A','Scenario B'],y=[pa*100,pb*100],
                         marker_color=[CYAN,GOLD],text=[f'{pa:.1%}',f'{pb:.1%}'],textposition='outside'))
    fig.update_layout(title='Estimated Chase Win Probabilities for Two Match Scenarios',
                      yaxis_title='Chasing team win probability (%)',yaxis_range=[0,110],showlegend=False)
    render_chart(_base_fig(fig),key='v2g_compare_bar',
                 title='Estimated Chase Win Probabilities for Two Match Scenarios')
    st.caption('The difference combines changes in runs and wickets when both inputs differ. It cannot isolate a causal effect and is NOT evidence of a strategic advantage.')


def performance_tab():
    section('RETROSPECTIVE MODEL VALIDATION','Historical 2025–2026 held-out rows and 2025–2026 feedback from earlier development; no future-season verification.')
    good=qualified_models()
    options=list(good)
    selected=st.selectbox('Select the prediction model to audit',options,
                          format_func=lambda x:MODEL_INFO[x][0],key='v2g_perf_model')
    model=good[selected]
    d=read_holdout(selected)
    e=evaluation(d)
    assert len(d)==model['independent_matches'], 'Holdout file and summary do not reconcile'
    assert abs(e['accuracy']-model['holdout']['accuracy'])<1e-10, 'Holdout classification mismatch'
    st.markdown(f"**Historical eligibility:** {MODEL_INFO[selected][2]}. **Target:** {MODEL_INFO[selected][1]}.")
    _model_score_ribbon(selected)
    threshold=st.slider('Classification decision threshold for audit (not a retrained model)',min_value=.2,max_value=.8,
                        value=.5,step=.05,key='v2g_threshold')
    at=evaluation(d,threshold)
    st.caption(f'The threshold changes only the win/loss label shown for evaluation. It does not alter fitted probabilities or the original model-quality gate. Baseline evaluated at 0.50.')
    x,y=st.columns(2,gap='large')
    with x:
        mat=[[at['tn'],at['fp']],[at['fn'],at['tp']]]
        fig=go.Figure(go.Heatmap(z=mat,x=['Predicted No','Predicted Yes'],y=['Actual No','Actual Yes'],
                                 colorscale=[[0,'#152B48'],[1,'#4EB8D3']],showscale=False,
                                 text=mat,texttemplate='%{text}',textfont=dict(size=26,color='white'),
                                 hovertemplate='%{y} vs %{x}<br>Matches: %{z}<extra></extra>'))
        fig.update_layout(title=f'Confusion Matrix at {threshold:.0%} Prediction Threshold',
                          xaxis_title='Predicted match outcome',yaxis_title='Actual match outcome')
        render_chart(_base_fig(fig),key='v2g_performance_confusion',
                     title=f'Confusion Matrix at {threshold:.0%} Prediction Threshold')
    with y:
        # Same match cohort, compare model accuracy with majority-class baseline.
        fig=go.Figure(go.Bar(x=['Selected threshold accuracy','Cohort majority baseline'],
                             y=[at['accuracy']*100,e['majority_accuracy']*100],marker_color=[GREEN,GOLD],
                             text=[f"{at['accuracy']:.1%}",f"{e['majority_accuracy']:.1%}"],textposition='outside'))
        fig.update_layout(title='Classification Accuracy Compared with the Majority-Class Baseline',
                          yaxis_title='Accuracy on eligible matches (%)',yaxis_range=[0,110],showlegend=False)
        render_chart(_base_fig(fig),key='v2g_perf_accuracy',
                     title='Classification Accuracy Compared with the Majority-Class Baseline')
    st.markdown(f"**At this threshold:** Precision {at['precision']:.1%} · Recall {at['recall']:.1%} · "
                f"Balanced accuracy {at['balanced_accuracy']:.1%} · Brier score {at['brier']:.3f} (unchanged by threshold).")
    st.caption('Classification accuracy is conditional on the relevant checkpoint being reached. These rows are independent MATCH checkpoints, not repeatedly sampled deliveries.')
    sec=st.columns(2,gap='large')
    with sec[0]:
        bins=pd.cut(d.probability,[-.001,.2,.4,.6,.8,1],include_lowest=True)
        cal=(d.assign(bin=bins).groupby('bin',observed=True)
                 .agg(predicted=('probability','mean'),observed=('observed_outcome','mean'),count=('match_id','size')).reset_index())
        fig=go.Figure()
        fig.add_scatter(x=[0,1],y=[0,1],mode='lines',line=dict(dash='dash',color=MUTED),name='Ideal calibration')
        fig.add_scatter(x=cal.predicted,y=cal.observed,mode='lines+markers',
                        line=dict(color=CYAN,width=3),marker=dict(size=np.maximum(8,np.sqrt(cal['count'])*3)),
                        text=[f'n={n}' for n in cal['count']],name='Observed win rate',
                        hovertemplate='Mean forecast: %{x:.1%}<br>Observed rate: %{y:.1%}<br>%{text}<extra></extra>')
        fig.update_layout(title='Historical Probability Calibration by Forecast Range',
                          xaxis_title='Average predicted event probability',yaxis_title='Observed event frequency',
                          xaxis_range=[0,1],yaxis_range=[0,1])
        render_chart(_base_fig(fig),key='v2g_perf_calibration',
                     title='Historical Probability Calibration by Forecast Range',
                     context='Five probability bins; inspect sample size before judging reliability. This is not an independent calibration study.')
    with sec[1]:
        # Use a direct iteration for compatibility across Pandas 2.x versions.
        rows=[{'year':int(s),'accuracy':100*evaluation(frame)['accuracy'],'n':len(frame)} for s,frame in d.groupby('season_year')]
        yr=pd.DataFrame(rows).sort_values('year')
        fig=go.Figure(go.Bar(x=yr.year.astype(str),y=yr.accuracy,marker_color=[CYAN,GOLD],
                             text=[f"{z:.1f}% (n={n})" for z,n in zip(yr.accuracy,yr.n)],textposition='outside'))
        fig.update_layout(title='Season-by-Season Historical Classification Accuracy',
                          xaxis_title='Held-out IPL season',yaxis_title='Accuracy (%)',yaxis_range=[0,110],showlegend=False)
        render_chart(_base_fig(fig),key='v2g_perf_yearly',
                     title='Season-by-Season Historical Classification Accuracy')
    st.markdown('#### Evaluation evidence')
    st.dataframe(d.rename(columns={'observed_outcome':'Actual outcome (1=yes)','probability':'Predicted probability',
                                   'season_year':'Season','match_id':'Match ID'}),hide_index=True,use_container_width=True)
    st.download_button('⬇ Export historical holdout predictions (CSV)',d.to_csv(index=False),
                       file_name=f'IPL360_{selected}_holdout.csv',mime='text/csv',key='v2g_performance_export')
    with st.expander('Show rejected model experiments and reason codes'):
        rejected=[{'Experiment':m['name'].replace('_',' ').title(),
                   'Holdout accuracy':f"{m.get('holdout',{}).get('accuracy',0):.1%}",
                   'Exclusion reason':m.get('gate_reason','Not eligible')} for m in report()['models'] if not m.get('gate_passed')]
        st.dataframe(pd.DataFrame(rejected),hide_index=True,use_container_width=True)


def methodology_tab():
    st.markdown('### What these predictions CAN tell you')
    st.markdown('''The models estimate binary outcomes at **specific completed-over checkpoints**. Inputs are current runs, wickets, target and completed legal overs. We display prediction probabilities and how they respond to hypothetical scoreboard changes. The trained models do not know the current batting lineup, bowlers remaining, pitch wear, weather, match-up history or venue conditions.''')
    st.markdown('### What these predictions CANNOT tell you')
    st.markdown('''- They **cannot** predict the winner before a match or at arbitrary ball counts.
- They are **not** a live-streaming score service; enter current scoreboard values manually.
- What-if charts show **local model response**, not causal feature contribution, intervention effects, or SHAP scores.
- A 90% win probability **does not mean 90% classification accuracy**, and the checkpoint models are evaluated only on matches that reach their checkpoint.
- They are **provisional retrospective research models**. The 2025–2026 holdout seasons influenced earlier development decisions. Test on a truly new season before production claims.
- The binary test datasets exclude abandoned/no-result games and certain shortened/unsupported innings. The display does not estimate DLS or tie/Super Over paths independently.''')
    st.markdown('### Dataset, audit and reproducibility')
    st.markdown('''The app uses four portable JSON model exports. Its historical match-level holdout probabilities are retained under `model_reports/holdout_predictions/`. Models are **unchanged from Phase 3D**. Model quality and qualifications are reported in `model_reports/model_gate_report.json`. All plots pass through the shared titled full-screen chart viewer. See `reports/V2G_Prediction_Centre_Methodology.md` for additional scientific notes.''')
    st.download_button('⬇ Download model-selection report (JSON)',json.dumps(report(),indent=2),
                       file_name='IPL360_retro_model_gate_report.json',mime='application/json',key='v2g_gate_json')


def render(public=False):
    if not public:
        hero('AI MODEL RESEARCH & EVALUATION', 'Historical probabilities, comparison charts, calibration and model-qualification evidence.', 'IPL INTELLIGENCE 360° / RESEARCH', 'Retrospective model audit')
        try:
            tabs=st.tabs(['Chase Probability', '180+ Innings Score', 'Compare Scenarios', 'Accuracy & Calibration', 'Interpretation', 'Earlier Live Model Audit'])
            with tabs[0]: chase_tab()
            with tabs[1]: total_tab()
            with tabs[2]: compare_tab()
            with tabs[3]: performance_tab()
            with tabs[4]: methodology_tab()
            with tabs[5]:
                from dashboard.live_research import render as research_render
                research_render()
        finally:
            pass
        return
    hero('CHASE & INNINGS PREDICTIONS',
         'Explore match situation and possible outcomes. Detailed model validation and capstone methodology are kept in the Research & Evaluation page.',
         'IPL INTELLIGENCE 360° / MATCH CENTRE', 'Historical match-state models')
    st.caption('These are retrospective checkpoint predictors, not an authorized live feed or a guarantee of future match results.')
    tabs=st.tabs(['🏏 Chase Probability', '📈 180+ Innings Score', '⚔️ Compare Scenarios'])
    with tabs[0]: chase_tab()
    with tabs[1]: total_tab()
    with tabs[2]: compare_tab()
