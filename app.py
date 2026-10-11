"""IPL Intelligence 360° — curated navigation. Legacy research code is retained but not exposed as a main page."""
import streamlit as st
st.set_page_config(page_title="IPL Intelligence 360°", page_icon="🏏", layout="wide", initial_sidebar_state="expanded")
from dashboard.views import overview

sections = {
    'Home': [st.Page(overview, title='Cricket Intelligence Home', icon='🏠', url_path='home', default=True)],
    'League & Franchise Intelligence': [
        st.Page('pages/01_League_EDA.py', title='IPL League Explorer', icon='📊'),
        st.Page('pages/02_Team_Comparison.py', title='Franchise Comparison', icon='⚔️'),
        st.Page('pages/05_CSK_Analyst_Desk.py', title='CSK Intelligence', icon='🏏'),
        st.Page('pages/06_MI_Analyst_Desk.py', title='MI Intelligence', icon='🏏'),
        st.Page('pages/07_RCB_Analyst_Desk.py', title='RCB Intelligence', icon='🏏'),
        st.Page('pages/08_KKR_Analyst_Desk.py', title='KKR Intelligence', icon='🏏'),
        st.Page('pages/09_SRH_Analyst_Desk.py', title='SRH Intelligence', icon='🏏'),
        st.Page('pages/10_RR_Analyst_Desk.py', title='RR Intelligence', icon='🏏'),
        st.Page('pages/11_DC_Analyst_Desk.py', title='DC Intelligence', icon='🏏'),
        st.Page('pages/12_PBKS_Analyst_Desk.py', title='PBKS Intelligence', icon='🏏'),
        st.Page('pages/13_GT_Analyst_Desk.py', title='GT Intelligence', icon='🏏'),
        st.Page('pages/14_LSG_Analyst_Desk.py', title='LSG Intelligence', icon='🏏'),
    ],
    'Player & Match Analysis': [
        st.Page('pages/16_Player_Intelligence_Lab.py', title='Player Intelligence', icon='🧢'),
        st.Page('pages/17_Team_DNA_and_Strategy.py', title='Team DNA & Strategy', icon='🎯'),
        st.Page('pages/15_Records_and_Legends.py', title='Records & Legends', icon='🏆'),
        st.Page('pages/19_Captaincy_and_Franchise_Legacy.py', title='Finals Captaincy & Legacy', icon='👑'),
        st.Page('pages/20_Match_Replay_and_Rivalry.py', title='Match Replay & Rivalry', icon='📈'),
        st.Page('pages/21_CLT20_and_Coaching_Intelligence.py', title='Coaches & CLT20', icon='🧠'),
        st.Page('pages/24_Sports_Analyst_Report_Studio.py', title='Analyst Report Studio', icon='📄'),
        st.Page('pages/26_Cricket_Debate_Lab.py', title='🔥 IPL Fan Wars: Fact Check', icon='💬'),
    ],
    'Predictions': [st.Page('pages/03_AI_Prediction_Lab.py', title='Chase & Score Predictions', icon='🎲')],
    'Research (optional)': [st.Page('pages/27_Research_and_Evaluation.py', title='Research, Model Tests & Capstone', icon='🔬')]
}
pg = st.navigation(sections, expanded=False)
pg.run()
