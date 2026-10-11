"""Two distinct 2026 records: a sourced pre-season post-auction snapshot, and observed season match participants."""
from functools import lru_cache
import pandas as pd
import streamlit as st
from dashboard.data import ROOT
from dashboard.design import kpi,section

@lru_cache(maxsize=1)
def snapshot():
    df=pd.read_csv(ROOT/'data/metadata/ipl_2026_post_auction_squads_sourced.csv')
    assert df.groupby('team_code').size().eq(25).all()
    assert df[['team_code','player_name']].duplicated().sum()==0
    return df

@lru_cache(maxsize=1)
def actual():
    d=pd.read_csv(ROOT/'data/raw/lineups.csv.gz',usecols=['season_year','team_code','cricsheet_player_id','player_name','match_id'])
    d=d[d.season_year==2026].copy()
    return d.groupby(['team_code','cricsheet_player_id','player_name'],as_index=False).agg(recorded_matches=('match_id','nunique')).sort_values('recorded_matches',ascending=False)

def squad_panel(code):
    section('2026 FRANCHISE SQUAD & MATCH PARTICIPANTS',
            'Source-dated team list and actual 2026 match participants are separate. These are NOT confirmed starting XIs.')
    df=snapshot().query('team_code == @code').copy()
    played=actual().query('team_code == @code').copy()
    a,b=st.columns(2)
    with a:kpi('2026 Post-Auction Squad Snapshot',str(len(df)),'25 reported players · 16 Dec 2025')
    with b:kpi('Players Recorded in 2026 Match Lists',str(len(played)),'Cricsheet season participants; may include Impact Players')
    with st.expander('View 2026 squad members and their reported roles', expanded=True):
        role=st.selectbox('Filter the 2026 post-auction squad by reported role', ['All roles','Batter','Bowler','All-rounder'],key='squad_role_'+code)
        show=df if role=='All roles' else df[df.source_role==role]
        st.dataframe(show[['player_name','source_role']].rename(columns={'player_name':'Player','source_role':'Reported role'}),hide_index=True,use_container_width=True)
        st.caption('Historical squad snapshot dated 16 Dec 2025, from a published post-auction compilation. It is not a continuously maintained final registration list; injury replacements and mid-season updates need separate official verification.')
        st.link_button('Source: 2026 post-auction squads',df.source_url.iloc[0])
        st.download_button('Download this 2026 squad snapshot',show.to_csv(index=False).encode(),file_name=code+'_2026_post_auction_squad.csv',mime='text/csv',key='v4y_squad_dl_'+code)
    with st.expander('View players who actually appeared on 2026 match participant lists'):
        st.dataframe(played[['player_name','recorded_matches']].rename(columns={'player_name':'Cricsheet name','recorded_matches':'Recorded matches'}),hide_index=True,use_container_width=True)
        st.caption('Observed match participation is not equivalent to registered squad membership or a starting XI. Source: Cricsheet IPL 2026 player listings.')
