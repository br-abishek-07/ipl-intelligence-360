"""IPL Intelligence 360°: sports-analysis screens for the ten franchises and IPL EDA."""
from pathlib import Path
import json
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from dashboard.data import load,audit,ROOT
from dashboard.analytics import TEAMS,TEAM_LABELS,ALL_TEAMS,PHASE_ORDER,filter_year,win_rate,franchise_seasons,matchup_table,venue_table,phase_metrics,top_batters,top_bowlers,matchup_h2h,sport_analyst_notes
from dashboard.predict import predict,chase_features,total_features
from dashboard.design import inject_theme,hero,kpi,section
from dashboard.chart_ui import render_chart

BG='#0A1020'; INK='#EAF2FC'; MUTED='#92A7BD'; GOLD='#F0B95C'; POS='#62D7AE'; NEG='#F38A8A'; BLUE='#79C3FB'

def setup(team=None):
    inject_theme(team)
    st.sidebar.markdown('### 🏏 IPL INTELLIGENCE 360°')
    st.sidebar.caption('INSIGHTS • TACTICS • EXPLAINABLE AI')
    st.sidebar.divider()

@st.cache_data(show_spinner=False)
def table(name): return load(name)

@st.cache_data(show_spinner=False)
def get_audit(): return audit()

def years_filter(key,default=None):
    m=table('matches')
    years=sorted(int(v) for v in m.season_year.dropna().unique())
    lo,hi=years[0],years[-1]
    if default:lo_default,hi_default=default
    else:lo_default,hi_default=lo,hi
    return st.sidebar.slider('Seasons',min_value=lo,max_value=hi,value=(max(lo,lo_default),min(hi,hi_default)),key=key)

def blank_chart(label):st.info('No records for this selection: '+label)

def line_chart(frame,x,y,color=None,title=None,ytitle=None,color_map=None):
    if frame.empty:return blank_chart('chart')
    fig=px.line(frame,x=x,y=y,color=color,markers=True,color_discrete_map=color_map,title=title)
    fig.update_traces(line_width=3,marker_size=7)
    fig.update_layout(template='plotly_dark',paper_bgcolor='rgba(0,0,0,0)',plot_bgcolor='rgba(0,0,0,0)',height=345,
       margin=dict(l=8,r=10,t=35,b=12),legend_title_text='',font=dict(color=INK),yaxis_title=ytitle or y)
    render_chart(fig,key=('analytics_'+str(title or y)).lower().replace(' ','_'),title=title or f'{y} by {x}')

def bar_chart(frame,x,y,color=None,title=None,orientation='v',height=340,colors=None):
    if frame.empty:return blank_chart('chart')
    fig=px.bar(frame,x=x,y=y,color=color,orientation=orientation,title=title,color_discrete_sequence=colors or [BLUE])
    fig.update_layout(template='plotly_dark',paper_bgcolor='rgba(0,0,0,0)',plot_bgcolor='rgba(0,0,0,0)',
         height=height,margin=dict(l=8,r=10,t=38,b=10),legend_title_text='',font=dict(color=INK))
    render_chart(fig,key=('analytics_'+str(title or y)).lower().replace(' ','_'),title=title or f'{y} by {x}')

def pct(v):return f'{v:.1%}' if pd.notna(v) else '—'

def csv_export(df,name):
    st.download_button('⬇ Export current table',data=df.to_csv(index=False).encode('utf-8'),file_name=name,mime='text/csv',key='dl'+name)

def section_analyst(notes):
    st.markdown('### 🧠 Sports analyst briefing')
    for item in notes:st.markdown('- '+item)
    st.caption('Explanations are descriptive and conditional on sample size; they are not evidence of causation.')

def overview():
    setup()
    hero('THE CRICKET INTELLIGENCE CENTRE',
        'Historical cricket intelligence covering 19 IPL seasons, ten franchises, and match-state forecasts.',
        'IPL INTELLIGENCE 360° / CURATED','DATA • EDA • AI')
    m=table('matches');a=get_audit()
    cols=st.columns(4,gap='small')
    for col,(label,value,note) in zip(cols,[
        ('MATCHES',f'{len(m):,}','2008–2026 verified match IDs'),
        ('SEASONS',f'{m.season_year.nunique():,}','Nineteen IPL editions'),
        ('FRANCHISES','10','Ten dedicated analyst desks'),
        ('DATA YEARS','19','Seasonal match coverage')]):
        with col:kpi(label,value,note)
    section('EXPLORE THE PLATFORM','Start with league trends; drill into the teams or open the AI lab.')
    left,right=st.columns(2)
    with left:
        st.markdown('### 📊 League Analysis')
        st.markdown('**Synchronized slicers** by season, team, ground, stage, toss, innings role and team result. Dynamic leaderboards and sports analyst commentary.')
        st.page_link('pages/01_League_EDA.py',label='Open premium IPL League Overview →')
        st.markdown('### ⚔️ Franchise Intelligence')
        st.markdown('Ten themed team desks, with records, performance, batting/bowling DNA and tactical explanations.')
        st.page_link('pages/05_CSK_Analyst_Desk.py',label='Explore CSK Intelligence →')
        st.page_link('pages/15_Records_and_Legends.py',label='Explore IPL Records & Legends →')
        st.page_link('pages/16_Player_Intelligence_Lab.py',label='Explore Advanced Player Intelligence →')
        st.page_link('pages/17_Team_DNA_and_Strategy.py',label='Explore Team DNA & Strategy Studio →')
        st.page_link('pages/27_Research_and_Evaluation.py',label='Research & Evaluation Library →')
        st.page_link('pages/19_Captaincy_and_Franchise_Legacy.py',label='Explore Verified Championship Captains →')
        st.page_link('pages/20_Match_Replay_and_Rivalry.py',label='Explore Ball-by-Ball Match Replay →')
        st.page_link('pages/21_CLT20_and_Coaching_Intelligence.py',label='Explore CLT20 Trophies and Coaches →')
        st.page_link('pages/24_Sports_Analyst_Report_Studio.py',label='V3-F: generate a downloadable sports analyst report →')
    with right:
        st.markdown('### 🧠 AI Predictions')
        st.markdown('Explore chase and innings-score probabilities, with optional match-scenario comparisons.')
        st.page_link('pages/03_AI_Prediction_Lab.py',label='Open AI Prediction Centre 2.0 →')
        st.markdown('### 🧪 Source & Methods')
        st.markdown('Data source and model-validation details are housed in the Research Library.')
        st.page_link('pages/27_Research_and_Evaluation.py',label='View Research & Data Quality Library →')
    section('LEAGUE SCORING THROUGH THE YEARS','First innings of at least 100 legal balls; matches affected by DLS excluded.')
    season=table('season').copy()
    line_chart(season,'season_year','mean_first_innings',title='Average IPL First-Innings Runs by Season (At Least 100 Balls, No DLS)',ytitle='Runs')
    st.caption('The EDA describes observed score changes; it does not claim their cause. The league page supplies deeper, synchronized drill-downs.')


def league_page():
    setup()
    from dashboard.league_v2 import render
    render()


def team_page(code):
    """V2-C premium franchise intelligence. The original 10 routes remain unchanged."""
    setup(code)
    from dashboard.franchise_v2 import render_team
    render_team(code,table)
    st.markdown('### More franchise research')
    st.page_link('pages/19_Captaincy_and_Franchise_Legacy.py',label='🏆 Verified finals captaincy and franchise legacy →')
    st.page_link('pages/20_Match_Replay_and_Rivalry.py',label='🏟️ Historical match replay and head-to-head intelligence →')
    from dashboard.v3d_coaching import clt20,coaching_2026
    historical_clt=clt20();coach_2026=coaching_2026()
    n_clt=int((historical_clt.champion_ipl_code==code).sum())
    snapshot=coach_2026[coach_2026.team_code==code]
    st.markdown('### Franchise legacy beyond the IPL')
    x,y=st.columns(2)
    with x:kpi('Champions League T20 titles (separate from IPL)',n_clt,'CLT20 ran from 2009 to 2014')
    with y:kpi('Head coach during the 2026 IPL season',snapshot.head_coach.iloc[0] if len(snapshot) else 'Not verified','Sourced 2026 season snapshot; not present-day appointment')
    st.page_link('pages/21_CLT20_and_Coaching_Intelligence.py',label='🏆 CLT20 titles and coaching intelligence →')


def comparison_page():
    setup();st.title('⚔️ Team Comparison Laboratory')
    years=years_filter('compare_years')
    c1,c2=st.columns(2)
    a=c1.selectbox('Franchise A',list(TEAMS),index=0,format_func=lambda x:f'{x} — {TEAMS[x][0]}')
    b=c2.selectbox('Franchise B',[x for x in TEAMS if x!=a],index=0,format_func=lambda x:f'{x} — {TEAMS[x][0]}')
    tm=filter_year(table('team_matches'),years)
    h=matchup_h2h(tm,a,b)
    ca,cb,cc=st.columns(3);ca.metric(f'{a} wins',h['a_wins']);cb.metric('Decided H2H games',h['matches']);cc.metric(f'{b} wins',h['b_wins'])
    if h['matches']<5:st.warning('Small historical head-to-head sample; percentages should not drive conclusions.')
    elif h['matches']:
        diff=h['a_wins']-h['b_wins'];leader=a if diff>0 else b if diff<0 else None
        st.markdown(f'**Analyst note:** {leader} leads by {abs(diff)} win(s) across {h["matches"]} decided meetings.' if leader else f'**Analyst note:** The sides are tied after {h["matches"]} decided meetings.')
    p=table('phase')
    league=phase_metrics(p,years)
    phase_list=[]
    for team in [a,b]:
        bat=phase_metrics(p,years,team,'bat')[['phase','run_rate']].assign(team=team,metric='Batting run rate')
        bow=phase_metrics(p,years,team,'bowl')[['phase','run_rate']].assign(team=team,metric='Bowling conceded rate')
        phase_list.extend([bat,bow])
    allp=pd.concat(phase_list)
    for metric in ['Batting run rate','Bowling conceded rate']:
        st.subheader(metric)
        bar_chart(allp[allp.metric==metric],'phase','run_rate',color='team',title=f'{a} vs {b}: {metric}',colors=[TEAMS[a][1],TEAMS[b][1]])
    st.caption('Batting: higher rate means faster scoring. Bowling: lower conceded rate means better run prevention. These are unconditional historical differences, not causal ratings.')
    st.markdown('### Season-by-season comparison')
    s=pd.concat([franchise_seasons(tm,x).assign(team=x) for x in [a,b]])
    line_chart(s,'season_year','win_pct',color='team',title='Win percentage across selected seasons',ytitle='Win %',color_map={a:TEAMS[a][1],b:TEAMS[b][1]})


def prediction_page():
    """V2-G unified AI match-state lab (retains the ten teams and other pages)."""
    setup()
    from dashboard.prediction_lab_v2 import render
    render(public=True)
    st.divider()
    st.page_link('pages/27_Research_and_Evaluation.py',label='Research and model validation details →')


def audit_page():
    setup();st.title('🧪 Data Quality & Scientific Method')
    a=get_audit()
    c=st.columns(4)
    for col,(label,v) in zip(c,[('Raw IPL matches',a['matches']),('Delivery mismatches',a['invalid_run_total']),('Recovered Super Overs',a['super_over_winner_recovered']),('No final winner',a['matches_without_final_winner'])]):col.metric(label,f'{v:,}')
    st.markdown('### Audit checks')
    important={k:v for k,v in a.items() if k in ['match_ids_unique','duplicate_delivery_positions','deliveries_to_missing_match_ids','invalid_run_total','matches_missing_regulation_winner','super_over_winner_recovered','matches_without_final_winner','matches_flagged_dls','match_team_lineup_counts_not_11','missing_batter_player_id_delivery_rows','missing_bowler_player_id_delivery_rows','duplicate_match_team_rows','team_match_rows_not_twice_matches','venue_aliases_grouped']}
    st.dataframe(pd.DataFrame([{'Check':k.replace('_',' ').capitalize(),'Value':v} for k,v in important.items()]),hide_index=True,use_container_width=True)
    st.subheader('Methodology and limitations')
    for note in a['restrictions']:st.markdown('- '+note)
    st.markdown('''**Source identity:** Phase 2 Cricsheet IPL JSON-derived tables are the primary source for results, deliveries and player IDs. Historical auction transactions are a separate partial dataset. **No fuzzy player matches are silently accepted.**

**Data leakage:** The EDA summarizes historical results. These retrospective tables must **not** be joined unchanged into pre-match ML features—future-season career totals and post-match outcomes would leak targets. Phase 3D predictions instead load the historical model artifacts with their original point-in-time feature definitions.

**Scorecard context:** Scorecard linkage from Phase 2 is maintained as a separate research artifact, not used to rewrite Cricsheet match IDs in this dashboard.

**Statistical literacy:** Relative scoring rates, venue win percentages and toss associations are descriptive. They are not causal explanations, and do not adjust for opponent difficulty, era effects, squad changes, or DLS. Compare denominators and sample sizes before drawing conclusions.''')
    st.markdown('### Season and venue record completeness')
    season=table('season');st.dataframe(season,hide_index=True,use_container_width=True)
    st.markdown('### Source documentation')
    st.code('data/raw/matches.csv.gz\ndata/raw/deliveries.csv.gz\ndata/raw/wickets.csv.gz\ndata/raw/lineups.csv.gz\ndata/raw/auction_sales.csv\nreports/data_quality_audit.json\nreports/eda_findings.md\nscripts/build_analytics.py',language='text')
    st.download_button('⬇ Download audit JSON',data=json.dumps(a,indent=2),file_name='IPL_Data_Quality_Audit.json',mime='application/json')
