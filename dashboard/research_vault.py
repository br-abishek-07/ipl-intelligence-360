"""Research, model evaluation, and capstone materials — deliberately off main sports pages."""
import json
import pandas as pd
import streamlit as st
from dashboard.data import ROOT, audit
from dashboard.design import hero,section
from dashboard.prediction_lab_v2 import performance_tab, methodology_tab

def render():
    hero('RESEARCH & EVALUATION LIBRARY',
         'Historical model scores, source-quality audits, experimental alternatives, and academic deliverables are kept here instead of cluttering cricket analysis.',
         'IPL INTELLIGENCE 360° / SCIENTIFIC WORKBENCH','EVIDENCE · LIMITATIONS')
    tabs=st.tabs(['Model tests & calibration','Data quality','Experimental decision models','Capstone & submissions'])
    with tabs[0]:
        st.session_state['ipl_research_mode']=True
        try:
            performance_tab()
        finally:
            st.session_state['ipl_research_mode']=False
    with tabs[1]:
        a=audit()
        keep=['matches','duplicate_delivery_positions','invalid_run_total','matches_without_final_winner','super_over_winner_recovered','missing_batter_player_id_delivery_rows']
        st.dataframe(pd.DataFrame([{'Audit check':k.replace('_',' ').title(),'Value':str(a.get(k,'Not captured'))} for k in keep]),hide_index=True,use_container_width=True)
        with st.expander('Full audit and quality limitations'):
            st.json(a)
        st.download_button('Download data audit JSON',json.dumps(a,indent=2),file_name='IPL_Data_Audit.json',mime='application/json')
    with tabs[2]:
        st.warning('Historical experimentation only. Player participation barely improves on repeat-last-XI; matchup and scouting regression models did not achieve deployable quality.')
        from dashboard.franchise_decision_lab import run
        if st.checkbox('Load advanced franchise research experiments (slower)', value=False, key='v4y_load_research'):
            run(embedded=True)
    with tabs[3]:
        st.markdown('### Methodology & academic documentation')
        st.info('The historical 2025–26 seasons were already inspected during development. Retrospective accuracy is not an independently blinded future score.')
        with st.expander('How to interpret the predictions'):
            methodology_tab()
        for base in ['deliverables','docs']:
            for p in sorted((ROOT/base).glob('*')):
                if p.is_file() and p.suffix.lower() in {'.pdf','.pptx','.docx','.png','.md'}:
                    st.download_button('Download '+p.name, data=p.read_bytes(),file_name=p.name,key='research_dl_'+p.name)
        st.caption('Research pages removed from primary navigation remain in the project source for reproducibility.')
