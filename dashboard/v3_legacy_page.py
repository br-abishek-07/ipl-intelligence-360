"""Sourced trophy captain history, deliberately not full career captaincy rankings."""
import pandas as pd
import plotly.express as px
import streamlit as st
from dashboard.analytics import TEAMS
from dashboard.design import hero,kpi,section
from dashboard.chart_ui import render_chart
from dashboard.v3_legacy import finals_registry,winning_captains

SOURCE='https://www.business-standard.com/amp/cricket/ipl/2008-to-2026-check-full-list-of-ipl-winners-runners-up-and-their-captains-126053100390_1.html'

def render():
    hero('Captaincy & Franchise Legacy','Verified IPL final captains, title-winning leadership, and franchise championship history.','V3 / CAPTAINCY RESEARCH','2008–2026 FINALS')
    d=finals_registry()
    selector=['ALL IPL FRANCHISES']+[x for x in TEAMS]
    team=st.selectbox('Filter historical IPL finals by franchise',selector,format_func=lambda x:'All franchises' if x.startswith('ALL') else f'{x} — {TEAMS[x][0]}',key='v3_legacy_team')
    f=d if team.startswith('ALL') else d[d.team_code==team].copy()
    nfinals=len(f)
    titles=int((f.role_in_final=='Winner').sum())
    runners=int((f.role_in_final=='Runner-up').sum())
    st.caption('**Scope: IPL FINALS ONLY.** This is not a general match captaincy database or an all-time captain win-rate ranking. Historical discontinued teams are kept separate.')
    cols=st.columns(4)
    for col,(label,value,note) in zip(cols,[('IPL Finals Reached',nfinals,'Selected franchise(s)'),('IPL Titles Won',titles,'Final wins'),('IPL Runner-Up Finishes',runners,'Final defeats'),('Final Captain Records',len(f),'38 source-verified entries league-wide')]):
        with col:kpi(label,value,note)
    tabs=st.tabs(['🏆 Trophy Leadership','📅 Championship Timeline','🥇 Team Legacy','🔍 Sources & Captaincy Coverage'])
    with tabs[0]:
        c=winning_captains(None if team.startswith('ALL') else team)
        section('IPL Titles Won by Each Championship Captain','Count of championship FINAL appearances as captain, not total career win percentage.')
        if not c.empty:
            fig=px.bar(c.sort_values('titles'),x='titles',y='captain_name',orientation='h',color='titles',color_continuous_scale='YlOrBr',title='IPL Championships Won by Winning Finals Captains')
            fig.update_layout(template='plotly_dark',paper_bgcolor='rgba(0,0,0,0)',height=max(330,len(c)*36),coloraxis_showscale=False,xaxis_title='Championships',yaxis_title='Captain')
            render_chart(fig,key='v3_titles_by_captain_'+team,title='IPL Championships Won by Winning Finals Captains')
            st.dataframe(c.rename(columns={'captain_name':'Winning Captain','titles':'IPL Titles as Captain','years':'Championship Seasons'}),hide_index=True,use_container_width=True)
        else:st.info('No IPL title-winning captain for this franchise in the supplied history.')
    with tabs[1]:
        section('IPL Finals and Their Captains','Each season has one winner and one runner-up; both captains are independently sourced.')
        display=f.sort_values(['season_year','role_in_final'],ascending=[False,False])
        st.dataframe(display[['season_year','role_in_final','team_code','captain_name','identity_status']].rename(columns={'season_year':'Season','role_in_final':'Final Result','team_code':'Team','captain_name':'Final Captain','identity_status':'Player ID Check'}),hide_index=True,use_container_width=True)
        if not f.empty:
            timeline=f.assign(final_count=1)
            fig=px.scatter(timeline,x='season_year',y='team_code',color='role_in_final',hover_name='captain_name',size='final_count',size_max=18,
                color_discrete_map={'Winner':'#EFC26E','Runner-up':'#7497BE'},title='IPL Finals by Season, Franchise and Final Result')
            fig.update_layout(template='plotly_dark',paper_bgcolor='rgba(0,0,0,0)',height=420,xaxis_title='IPL Season',yaxis_title='Franchise')
            render_chart(fig,key='v3_final_timeline_'+team,title='IPL Finals by Season, Franchise and Final Result')
    with tabs[2]:
        summary=d.pivot_table(index='team_code',columns='role_in_final',values='season_year',aggfunc='count',fill_value=0).reset_index()
        for col in ['Winner','Runner-up']:
            if col not in summary:summary[col]=0
        ordered=summary.sort_values(['Winner','Runner-up'],ascending=[False,False])
        if not team.startswith('ALL'):ordered=ordered[ordered.team_code==team]
        fig=px.bar(ordered,x='team_code',y=['Winner','Runner-up'],barmode='group',color_discrete_sequence=['#EFC26E','#79C3FB'],
            title='IPL Championship Titles and Runner-Up Finishes by Franchise')
        fig.update_layout(template='plotly_dark',paper_bgcolor='rgba(0,0,0,0)',height=380,xaxis_title='Franchise',yaxis_title='Finals')
        render_chart(fig,key='v3_team_finals_'+team,title='IPL Championship Titles and Runner-Up Finishes by Franchise')
        st.info('Franchise identities remain historically distinct. The 2009 Deccan Chargers title is not attributed to SRH; former franchises are included in league-wide history.')
    with tabs[3]:
        st.markdown('**Published final-captain list:** [Business Standard (May 31, 2026)]('+SOURCE+')')
        st.markdown('**Match result and player ID verification:** Cricsheet IPL JSON included in `data/source/ipl_json.zip`. Each captain listed here was found in that franchise’s lineup for the corresponding final.')
        st.warning('The Cricsheet player list does not designate a captain. The captain labels come from the cited external source for the 19 IPL finals. Ordinary IPL league-match captain records are **not yet verified**, so “best captain by full-season win percentage” is intentionally unavailable.')
        st.dataframe(f[['season_year','match_id','captain_name','team_code','source_url','captain_player_id']],hide_index=True,use_container_width=True)
        st.download_button('Download source-linked captaincy evidence (CSV)',data=f.to_csv(index=False),file_name='IPL_V3C_final_captains.csv',mime='text/csv',key='v3_final_evidence')
