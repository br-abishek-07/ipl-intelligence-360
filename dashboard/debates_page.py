"""IPL Cricket Debate Lab: provocative claims checked against source-backed records."""
from pathlib import Path
import pandas as pd
import streamlit as st
from dashboard.data import ROOT
from dashboard.design import hero

@st.cache_data(show_spinner=False)
def _debates():
    return pd.read_csv(ROOT/'reports/v4y/RAGE_BAIT_IPL_DEBATES_VERIFIED.csv').fillna('')

def render():
    hero('IPL FAN WARS — FACT-CHECKED', 'Bold cricket debates. Real numbers. No invented captaincy rankings, no fake predictive accuracy.', 'IPL INTELLIGENCE 360° / CRICKET DEBATE DESK','2008–2026')
    d = _debates()
    a,b,c=st.columns(3)
    a.metric('Data-backed debates',len(d))
    b.metric('Historical IPL matches',1_243)
    c.metric('Coverage','2008–2026')
    st.caption('Provocative headlines are for discussion. Answers are descriptive, backed by source tables, and include the evidence and comparison limitations.')
    left,right=st.columns([1,2])
    with left:
        category=st.selectbox('Choose debate category',['All categories']+sorted(d.category.unique().tolist()),key='rage_debate_category')
    with right:
        query=st.text_input('Search a player, team, or claim',placeholder='Kohli, Dhoni, CSK, Bumrah, toss…',key='rage_debate_query')
    if category!='All categories': d=d[d.category.eq(category)]
    if query.strip():
        q=query.strip().casefold()
        d=d[d[['question','answer','evidence','category']].astype(str).agg(' '.join,axis=1).str.casefold().str.contains(q,regex=False)]
    st.caption(f'{len(d)} debates match your selection')
    if d.empty:
        st.info('No debates match these filters. Clear the search or choose another category.')
    for item in d.itertuples(index=False):
        with st.expander(f'{int(item.number):02d}  {item.question}',expanded=False):
            st.markdown('**THE DATA-BASED VERDICT**')
            st.write(item.answer)
            a,b=st.columns(2)
            with a:
                if str(item.metric_a).strip(): st.metric(str(item.metric_a),str(item.value_a))
            with b:
                if str(item.metric_b).strip(): st.metric(str(item.metric_b),str(item.value_b))
            st.markdown('**SHOW ME THE RECEIPTS**')
            st.write(item.evidence)
            st.caption(f'Source: {item.data_source}')
            st.warning('Context matters: '+str(item.interpretation_limit),icon='⚖️')
    st.download_button('Download all 19 fact-checked fan debates',
                       (ROOT/'reports/v4y/RAGE_BAIT_IPL_DEBATES_VERIFIED.md').read_bytes(),
                       file_name='IPL_RAGE_DEBATES_WITH_EVIDENCE.md', mime='text/markdown')
    st.download_button('Download machine-readable debate evidence (CSV)',
                       (ROOT/'reports/v4y/RAGE_BAIT_IPL_DEBATES_VERIFIED.csv').read_bytes(),
                       file_name='IPL_RAGE_DEBATES_WITH_EVIDENCE.csv',mime='text/csv')
