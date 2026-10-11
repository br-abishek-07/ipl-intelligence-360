"""V2-I: project-level methodology and capstone delivery assets."""
from pathlib import Path
import pandas as pd
import streamlit as st
from dashboard.views import setup
from dashboard.design import hero, kpi, section
from dashboard.data import ROOT

setup()
hero('CAPSTONE RESEARCH & PRESENTATION CENTRE',
     'Project architecture, verified dataset scope, retrospective model results, scientific limitations, and viva resources.',
     'IPL INTELLIGENCE 360° / V2-I','ACADEMIC SUBMISSION')

tabs=st.tabs(['Project overview','Research methodology','Model evidence','Submission & viva'])
with tabs[0]:
    section('END-TO-END AI DRIVEN DATA SCIENCE CAPSTONE')
    columns=st.columns(4)
    for col,(label,value,note) in zip(columns,[
        ('Historical IPL Matches','1,243','Seasons 2008–2026'),
        ('Identified Players','809','Cricsheet identity keys'),
        ('Franchise Desks','10','Current franchises'),
        ('Provisional ML Models','4','Specific match checkpoints')]):
        with col:kpi(label,value,note)
    pic=ROOT/'deliverables'/'IPL360_System_Architecture.png'
    if pic.exists():st.image(str(pic),caption='Source to dashboard architecture — design diagram, not a live software capture.',use_container_width=True)
    st.markdown('**User workflow:** inspect league EDA → filter a franchise → study player and team DNA → investigate a match checkpoint → examine the validation and data-quality audit.')

with tabs[1]:
    section('SCIENTIFIC AND DATA-ENGINEERING APPROACH')
    st.markdown('''1. **Source:** Cricsheet IPL JSON, retained unmodified in `data/source/ipl_json.zip`.
2. **ETL:** flatten results and deliveries, normalize franchise identities, preserve Cricsheet player IDs, exclude Super Overs from routine career totals, and recover eligible Super Over match winners.
3. **Quality:** detect duplicate deliveries, missing IDs, invalid runs, unresolved winners and roster/Impact Player ambiguity.
4. **EDA:** calculate match-specific batting, bowling, innings-phase, opponent, venue and player performance metrics under synchronized filters.
5. **Model evaluation:** restrict predictions to fixed information-availability checkpoints; compare against majority-class baselines, Brier, AUC and confidence intervals.
6. **Interactive product:** Streamlit/Plotly app with reusable fullscreen charts, readable KPI labels and theme-specific franchise pages.''')
    st.info('Captaincy ranks require independently confirmed captains for individual games; player images and external logos require appropriate use permissions.')

with tabs[2]:
    section('REPRODUCIBLE RETROSPECTIVE EVALUATION')
    p=ROOT/'model_reports/model_gate_summary.csv'
    df=pd.read_csv(p)
    allowed=df[df.gate_passed.astype(str).str.lower().eq('true')][['name','accuracy','auc','brier','majority_accuracy','independent_matches']].copy()
    st.dataframe(allowed.rename(columns={'name':'Checkpoint model','accuracy':'Retrospective accuracy','auc':'ROC-AUC','brier':'Brier score (lower better)','majority_accuracy':'Majority baseline','independent_matches':'Held-out matches'}),hide_index=True,use_container_width=True)
    st.warning('2025–2026 were inspected during model development. The results are historical, not an independent blind confirmation for future IPL seasons. The pre-match winner model did not qualify.')
    st.info('The separate **Earlier Live Model Audit** tab in AI Prediction Lab documents the corrected research baseline and why earlier in-sample accuracy cannot be used as a valid test result. This research candidate is not an additional deployed model.')

with tabs[3]:
    section('SUBMISSION AND DEMONSTRATION FILES')
    deliver=ROOT/'deliverables'
    options=[('Academic project report (Word)','IPL360_Capstone_Report.docx','application/vnd.openxmlformats-officedocument.wordprocessingml.document'),
             ('Project report (PDF)','IPL360_Capstone_Report.pdf','application/pdf'),
             ('Viva presentation (PowerPoint)','IPL360_Viva_Presentation.pptx','application/vnd.openxmlformats-officedocument.presentationml.presentation'),
             ('System architecture illustration','IPL360_System_Architecture.png','image/png')]
    for title,name,mime in options:
        fp=deliver/name
        if fp.exists():
            st.download_button(title,data=fp.read_bytes(),file_name=name,mime=mime,key='v2i_dl_'+name)
    with st.expander('Presenter checklist',expanded=True):
        st.markdown('''- Open **League EDA** and change the season range; show that all KPIs and charts update.
- Open **CSK Analyst Desk**, switch rival or venue, and expand one chart full screen.
- Open **Player Intelligence** and compare batting phases or head-to-head samples.
- Open **Team DNA**, show that percentile rankings are not model accuracy.
- Open **AI Prediction Lab**, run a 10-over chase, and explain its input eligibility and retrospective limitations.
- Open **Data Quality Centre**, mention the nine unresolved results and captaincy data gap.''')
    st.caption('Offline automated audit and scripted rendering tests do not replace final browser sign-off on your Windows laptop.')
