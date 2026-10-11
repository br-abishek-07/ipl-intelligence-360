"""Premium Team DNA & Sports Analyst Studio, V2-H.
All plots use one renderer for descriptive titles and interactive full-screen view.
"""
from __future__ import annotations
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from dashboard.analytics import TEAMS,ALL_TEAMS,PHASE_ORDER
from dashboard.data import load
from dashboard.design import hero,kpi,section,palette
from dashboard.chart_ui import render_chart
from dashboard.team_dna import CURRENT,DNASelection,build_dna,PHASES

@st.cache_data(show_spinner=False)
def _load_inputs():
    return load('team_matches'), load('phase_match')


def _style(fig, color, h=420):
    fig.update_layout(template='plotly_dark',paper_bgcolor='rgba(0,0,0,0)',plot_bgcolor='rgba(0,0,0,0)',
                      font=dict(color='#ECF3FC'),height=h,margin=dict(l=22,r=20,t=75,b=35),
                      legend_title_text='',hoverlabel=dict(bgcolor='#172742',font_color='#EAF2FF'))
    fig.update_xaxes(gridcolor='rgba(167,200,232,.10)',zeroline=False)
    fig.update_yaxes(gridcolor='rgba(167,200,232,.10)',zeroline=False)
    return fig


def _publish(fig,team,tag,context=''):
    if fig is None or len(fig.data)==0:
        st.info('Insufficient eligible observations for this visualization. Try a longer season interval.')
    else:render_chart(fig,key=f'dna_{team}_{tag}',context=context)


def _radar(r,accent):
    s=r['scores'];d=s[s.eligible].copy()
    if len(d)<3:return None
    fig=go.Figure()
    fig.add_trace(go.Scatterpolar(r=list(d.score)+[float(d.score.iloc[0])],
                  theta=list(d.dimension)+[d.dimension.iloc[0]],mode='lines+markers',fill='toself',
                  marker=dict(color=accent,size=8),line=dict(color=accent,width=3),
                  fillcolor='rgba(103,184,236,.17)',name='Relative percentile'))
    fig.add_trace(go.Scatterpolar(r=[50]* (len(d)+1),theta=list(d.dimension)+[d.dimension.iloc[0]],
                  mode='lines',line=dict(color='#9BACBC',width=1,dash='dash'),name='Median peer standing'))
    fig.update_layout(title='Team DNA Profile — Percentile Rankings Among Comparable Franchises',
      polar=dict(radialaxis=dict(range=[0,100],tickvals=[0,25,50,75,100],gridcolor='rgba(184,214,244,.12)'),
        angularaxis=dict(gridcolor='rgba(184,214,244,.12)')),showlegend=True)
    return _style(fig,accent,515)


def _rankings(r,accent):
    d=r['scores'];d=d[d.eligible].sort_values('score')
    if d.empty:return None
    fig=px.bar(d,y='dimension',x='score',orientation='h',color_discrete_sequence=[accent],
       hover_data={'comparison_teams':True,'sample':True,'measured':':.2f','preference':True},
       title='Team Strengths and Weaknesses — Higher Percentile Means Stronger Relative Performance',
       labels={'dimension':'','score':'Relative percentile (0–100)'})
    fig.update_xaxes(range=[0,100]);return _style(fig,accent,405)


def _phase(r,accent,field,kind):
    m=r['metrics'];b=r['benchmark'];data=[]
    for ph,x in zip(['Powerplay (1–6)','Middle (7–15)','Death (16–20)'],('pp','mid','death')):
        k=f'{field}_{x}_rr'
        if np.isfinite(m.get(k,np.nan)):
            data.append({'phase':ph,'group':'Selected franchise','run_rate':m[k]})
        if np.isfinite(b.get(k,np.nan)):
            data.append({'phase':ph,'group':'Independent peer franchises','run_rate':b[k]})
    if not data:return None
    df=pd.DataFrame(data)
    title=('Runs Scored Per Over' if field=='bat' else 'Runs Conceded Per Over')+' — IPL Innings Phases vs Season-Matched Peers'
    fig=px.bar(df,x='phase',y='run_rate',color='group',barmode='group',
       category_orders={'phase':list(PHASES)},color_discrete_map={'Selected franchise':accent,'Independent peer franchises':'#9BAEC4'},
       title=title,labels={'phase':'Innings phase','run_rate':'Runs per six legal balls','group':''})
    return _style(fig,accent,425)


def _attack_defence(r,accent,team):
    peers=r['peers'];own=r['metrics'];cols=['team','bat_rr','bowl_rr','matches']
    if peers.empty:return None
    d=pd.concat([peers[cols],pd.DataFrame([dict(team=team,bat_rr=own['bat_rr'],bowl_rr=own['bowl_rr'],matches=own['matches'])])],ignore_index=True)
    d=d.dropna(subset=['bat_rr','bowl_rr'])
    d['Focus']=np.where(d.team.eq(team),'Selected franchise','Other franchises')
    fig=px.scatter(d,x='bat_rr',y='bowl_rr',size='matches',size_max=30,color='Focus',text='team',
          color_discrete_map={'Selected franchise':accent,'Other franchises':'#90A8C8'},
          title='Batting Run Rate vs Bowling Economy — Where Each Franchise Sits',
          labels={'bat_rr':'Runs scored per over (higher is better)','bowl_rr':'Runs conceded per over (lower is better)'},
          hover_data=['matches'])
    fig.update_traces(textposition='top center');fig.update_yaxes(autorange='reversed')
    return _style(fig,accent,470)


def _roles(r,accent):
    m=r['metrics'];p=r['benchmark'];rows=[]
    for label,metric,count in [('Chasing','chase_win_pct','chases'),('Defending','defence_win_pct','defences')]:
        if np.isfinite(m.get(metric,np.nan)):
            rows.append(dict(role=label,group='Selected franchise',rate=m[metric],games=m[count]))
        if np.isfinite(p.get(metric,np.nan)):
            rows.append(dict(role=label,group='Independent peers',rate=p[metric],games=int(p.get(count,0))))
    if not rows:return None
    fig=px.bar(pd.DataFrame(rows),x='role',y='rate',color='group',barmode='group',
       color_discrete_map={'Selected franchise':accent,'Independent peers':'#9BAEC4'},
       hover_data=['games'],title='Win Percentage When Chasing vs Batting First',
       labels={'role':'Match role','rate':'Wins per 100 decided games','group':''})
    fig.update_yaxes(range=[0,100],ticksuffix='%')
    return _style(fig,accent,375)


def _season_form(r,accent):
    focus=r['focus'];sub=focus[focus.is_decided]
    if sub.empty:return None
    d=sub.groupby('season_year').agg(matches=('match_id','count'),wins=('won','sum')).reset_index()
    d['win_rate']=100*d.wins/d.matches
    fig=go.Figure()
    fig.add_trace(go.Bar(x=d.season_year,y=d.matches,name='Decided matches',marker_color='#637993',yaxis='y2',opacity=.50))
    fig.add_trace(go.Scatter(x=d.season_year,y=d.win_rate,name='Franchise win rate',mode='lines+markers',line=dict(color=accent,width=3)))
    fig.update_layout(title='Season-by-Season Win Percentage and Number of Decided Matches',
      xaxis=dict(title='Season',dtick=1),yaxis=dict(title='Win rate (%)',range=[0,100],ticksuffix='%'),
      yaxis2=dict(title='Matches',overlaying='y',side='right',showgrid=False),barmode='overlay')
    return _style(fig,accent,420)


def _rivalry(r,accent):
    d=r['focus'];d=d[d.is_decided]
    if d.empty:return None
    x=d.groupby('opponent_code').agg(decided=('match_id','count'),wins=('won','sum')).reset_index()
    x=x[x.decided>=3]
    if x.empty:return None
    x['losses']=x.decided-x.wins;x['Opponent']=x.opponent_code.map(ALL_TEAMS).fillna(x.opponent_code)
    x=x.sort_values('decided').tail(12)
    fig=go.Figure()
    fig.add_trace(go.Bar(y=x.Opponent,x=x.wins,orientation='h',name='Wins',marker_color=accent))
    fig.add_trace(go.Bar(y=x.Opponent,x=x.losses,orientation='h',name='Losses',marker_color='#DC6273'))
    fig.update_layout(title='Head-to-Head Results — Wins and Losses by Opposing Franchise (Minimum 3 Games)',
        barmode='stack',xaxis_title='Decided matches')
    return _style(fig,accent,460)


def _venue(r,accent):
    d=r['focus'];d=d[d.is_decided]
    if d.empty:return None
    x=d.groupby('venue_group').agg(games=('match_id','count'),wins=('won','sum')).reset_index()
    x=x[x.games>=3].sort_values('games',ascending=False).head(13).copy()
    if x.empty:return None
    x['win_rate']=100*x.wins/x.games
    fig=px.scatter(x,x='games',y='win_rate',size='games',size_max=34,hover_name='venue_group',
       hover_data=['wins'],color_discrete_sequence=[accent],
       title='Ground Performance — Match Volume vs Win Percentage (At Least 3 Games)',
       labels={'games':'Decided matches at ground','win_rate':'Franchise win percentage'})
    fig.update_yaxes(range=[0,100],ticksuffix='%')
    return _style(fig,accent,385)


def _season_ticks_html(first: int, last: int, years: tuple[int, int], accent: str) -> str:
    """Visible year-by-year season timeline for Streamlit's end-labeled range slider.

    The Streamlit slider displays only endpoints natively. These explicit tick
    labels make every season readable; selected years are highlighted.
    """
    if first > last or years[0] > years[1]:
        raise ValueError('Invalid season boundaries')
    items = []
    for yr in range(first, last + 1):
        is_active = years[0] <= yr <= years[1]
        status = 'dna-year-active' if is_active else 'dna-year-muted'
        aria = 'included' if is_active else 'excluded'
        items.append(f'<span class="dna-year-label {status}" title="{yr} season — {aria}">{yr}</span>')
    return f"""<style>
      .dna-seasons-scroller {{ width:100%;overflow-x:auto;scrollbar-width:thin; padding:4px 0 8px; }}
      .dna-seasons-ticks {{display:flex;align-items:center;justify-content:space-between;
        min-width:{(last-first+1)*25}px;gap:1px;}}
      .dna-year-label {{ flex:1;min-width:0;text-align:center;white-space:nowrap;
        padding:6px 0;font-family:inherit;font-size:9px;font-weight:600;
        border-radius:5px;font-variant-numeric:tabular-nums;letter-spacing:-.15px; }}
      .dna-year-muted {{ color:#96A7BE;background:rgba(164,187,215,.06); }}
      .dna-year-active {{color:{accent};background:rgba(193,208,230,.13);
        box-shadow:inset 0 -2px 0 {accent}; }}
      @media(max-width:700px) {{.dna-year-label {{font-size:10px;}}}}
    </style><div class="dna-seasons-scroller" role="group" aria-label="All IPL season years">
      <div class="dna-seasons-ticks">{''.join(items)}</div>
    </div>"""


def _choose_inputs(tm):
    c1,c2=st.columns([1.5,2.0])
    with c1:
        team=st.selectbox('Select a franchise to analyze',list(CURRENT),
                         format_func=lambda k: f'{k} — {TEAMS[k][0]}',key='dna_franchise')
    first=int(tm[tm.team_code.eq(team)].season_year.min());last=int(tm.season_year.max())
    default_first=max(first,last-4)
    with c2:
        mode=st.radio('Season selection mode',('Season range','Single season'),
                      horizontal=True,key='dna_season_mode')
        if mode=='Single season':
            selected_year=st.selectbox('Choose an IPL season (all years available)',
                       options=list(range(first,last+1)),index=last-first,key='dna_single_season')
            years=(int(selected_year),int(selected_year))
        else:
            years=st.slider('Seasons to compare',min_value=first,max_value=last,
                            value=(default_first,last),key='dna_season_range',step=1)
        if not isinstance(years,(tuple,list)):years=(default_first,last)
        years=(int(years[0]),int(years[1]))
        st.markdown(_season_ticks_html(first,last,years,TEAMS[team][1]),unsafe_allow_html=True)
        st.caption(f'Active seasons: {years[0]}' + (f'–{years[1]}' if years[0]!=years[1] else '')
                   + '. Every season is labeled above; use Single season for an exact-year view.')
    t=tm[tm.team_code.eq(team)&tm.season_year.between(*years)]
    a,b,c=st.columns(3)
    with a:
        opponents=st.multiselect('Filter this franchise by opponent',sorted(t.opponent_code.dropna().unique()),
          format_func=lambda k:ALL_TEAMS.get(k,k),key='dna_opponent') or []
    with b:venues=st.multiselect('Match venues',sorted(t.venue_group.dropna().unique()),key='dna_venue') or []
    with c:stages=st.multiselect('Match stage',sorted(t.match_type.dropna().unique()),key='dna_stage') or []
    st.caption('Seasons, venues and stage also constrain peers. Opponent filters affect the selected franchise only; peer teams are sampled independently.')
    return DNASelection(team,years[0],years[1],tuple(opponents),tuple(venues),tuple(stages))


def render_team_dna():
    tm,ph=_load_inputs()
    # Control rendered before themed hero; CSS is installed from selected code immediately afterward.
    selection=_choose_inputs(tm)
    from dashboard.design import inject_theme
    inject_theme(selection.team)
    name,accent=TEAMS[selection.team]
    hero(f'{name} | Team DNA & Strategy Studio',
         'A scouting-grade view of innings tactics, attack vs defence, consistency, chasing and rivalry patterns.',
         'IPL INTELLIGENCE 360° / V2-H SPORTS ANALYST STUDIO',f'{selection.first}–{selection.last}',team=selection.team)
    r=build_dna(tm,ph,selection)
    if r['focus'].empty:
        st.warning('No matches satisfy all selected filters. Expand the season, venue, opponent or match-stage selection.')
        return
    m=r['metrics'];bench=r['benchmark']
    section('TACTICAL SNAPSHOT','Filtered franchise fixtures only; rates are descriptive. A small-sample warning appears where appropriate.')
    cards=[('Matches Examined',str(m['matches']),'Matches after all selected filters'),
      ('Decided Match Win Rate',f"{m['win_pct']:.1f}%" if np.isfinite(m['win_pct']) else '—',f"{m['wins']} wins / {m['decided']} decided games"),
      ('Runs Scored per Over',f"{m['bat_rr']:.2f}" if np.isfinite(m['bat_rr']) else '—','Six legal batting deliveries'),
      ('Runs Conceded per Over',f"{m['bowl_rr']:.2f}" if np.isfinite(m['bowl_rr']) else '—','Lower means better run prevention'),
      ('Wickets Taken per 120 Balls',f"{m['wickets_120']:.2f}" if np.isfinite(m['wickets_120']) else '—','Standardized bowling wicket rate'),
      ('Chase Win Rate',f"{m['chase_win_pct']:.1f}%" if np.isfinite(m['chase_win_pct']) else '—',f"{m['chases']} decided chases"),
      ('Batting Boundary-Ball Rate',f"{m['boundary_pct']:.1f}%" if np.isfinite(m['boundary_pct']) else '—','Fours or sixes per 100 legal balls'),
      ('Independent Peer Matches',str(bench.get('matches',0)),'Other current teams in matched seasons')]
    for start in (0,4):
        cols=st.columns(4)
        for col,(label,value,note) in zip(cols,cards[start:start+4]):
            with col:kpi(label,value,note)
    tabs=st.tabs(['🧬 Relative strength','🏏 Phase tactics','⚔️ Rivals & grounds','🎛️ Tactical scenarios','🧠 Analyst briefing','📦 Audit & download'])
    with tabs[0]:
        section('RELATIVE TEAM DNA','Percentiles compare the team to eligible peer franchises; 50 represents roughly the middle of peers, not a 50% win probability.')
        l,rr=st.columns(2)
        with l:_publish(_radar(r,accent),selection.team,'radar','Requires at least 3 eligible DNA dimensions; all axes are sample-qualified.')
        with rr:_publish(_rankings(r,accent),selection.team,'rankings','Higher percentile = better measured outcome for that dimension; direction of bowling rate is reversed.')
        _publish(_attack_defence(r,accent,selection.team),selection.team,'attack_defence',
           'Each point represents a franchise during the selected seasons. The Y axis is reversed because fewer runs conceded is better.')
    with tabs[1]:
        a,b=st.columns(2)
        with a:_publish(_phase(r,accent,'bat','Batting'),selection.team,'bat_phase',
               'Batting run rates use runs divided by legal balls; independent peers match season, venue and stage selections.')
        with b:_publish(_phase(r,accent,'bowl','Bowling'),selection.team,'bowl_phase',
               'Bowling run prevention is measured as opposition runs per six legal balls; lower is better.')
        a,b=st.columns(2)
        with a:_publish(_roles(r,accent),selection.team,'roles',
                 'Only decided matches are included; no-results are excluded, and late-stage chase records have smaller samples.')
        with b:_publish(_season_form(r,accent),selection.team,'season_form',
                 'The season win percentage is shown alongside the match sample to avoid overstating small-sample trends.')
    with tabs[2]:
        a,b=st.columns(2)
        with a:_publish(_rivalry(r,accent),selection.team,'rivalry')
        with b:_publish(_venue(r,accent),selection.team,'venue')
        st.caption('Ground win percentages are not adjusted for opponent, venue assignment or toss; they do not establish true home advantage.')
    with tabs[3]:
        section('HYPOTHETICAL SCORING SCENARIO','Explore how a small change in batting run rate would alter a theoretical 20-over innings, not a prediction of wins.')
        a,b,c=st.columns(3)
        with a:pp=st.slider('Powerplay run-rate change (runs per over)',min_value=-2.0,max_value=2.0,value=0.0,step=0.25,key=f'dna_pp_whatif_{selection.team}')
        with b:mid=st.slider('Middle-overs run-rate change (runs per over)',min_value=-2.0,max_value=2.0,value=0.0,step=0.25,key=f'dna_mid_whatif_{selection.team}')
        with c:death=st.slider('Death-overs run-rate change (runs per over)',min_value=-2.0,max_value=2.0,value=0.0,step=0.25,key=f'dna_death_whatif_{selection.team}')
        impact={'Powerplay (6 overs)':float(pp)*6,'Middle overs (9 overs)':float(mid)*9,'Death overs (5 overs)':float(death)*5}
        baseline=sum([m.get('bat_pp_rr',float('nan'))*6,m.get('bat_mid_rr',float('nan'))*9,m.get('bat_death_rr',float('nan'))*5])
        total=sum(impact.values())
        a,b=st.columns(2)
        with a:kpi('Theoretical Change in Innings Runs',f'{total:+.1f} runs','Arithmetic only: +RR × number of overs')
        with b:kpi('Theoretical 20-Over Total',f'{baseline+total:.1f}' if np.isfinite(baseline) else '—','Observed phase RR extended to full 20-over innings')
        df=pd.DataFrame({'Innings phase':list(impact),'Hypothetical run difference':list(impact.values())})
        fig=px.bar(df,x='Innings phase',y='Hypothetical run difference',color_discrete_sequence=[accent],
          title='Hypothetical Runs Added or Lost by Changes in Batting Run Rate',
          labels={'Innings phase':'Innings phase','Hypothetical run difference':'Change in runs vs baseline'})
        fig.add_hline(y=0,line_color='#92A5BB',line_width=1)
        _publish(_style(fig,accent,375),selection.team,'what_if',
          'Scenario uses fixed six-, nine- and five-over lengths. It does not model wicket risk, opposition, venue or match-winning probability.')
        st.warning('Theoretical arithmetic, not a forecast or recommendation: teams cannot freely increase scoring without affecting wicket risk and other match factors.')
    with tabs[4]:
        section('EVIDENCE-BASED SPORTING ASSESSMENT','These observations summarize historical associations and do not claim a winning strategy or causal effects.')
        for note in r['insights']:st.markdown('- '+note)
        section('COACHING AND ANALYST FOLLOW-UP QUESTIONS','Questions to investigate before strategic decisions.')
        st.markdown('''- Do weaker innings phases persist after adjusting for opponents and ground conditions?
- Is the apparent chase advantage explained by toss choice or unusually weak targets?
- Are top batting and bowling performers available in the current season?
- Which tactical differences survive a minimum 10-match sample or season-by-season split?
- Are the team’s observed strengths stable against the strongest opposition?''')
    with tabs[5]:
        section('MODEL-FREE SPORTS ANALYSIS','These are descriptive sports KPIs; they are not AI prediction models or 70% accuracy claims.')
        st.markdown('**Benchmark protocol:** Nine other current franchises; independent fixtures, same season window and optional venues/stages. Franchise opponent selection does not also filter peers. When fewer than five peers have qualifying samples, the DNA percentile is intentionally left blank.')
        st.markdown('**Minimum sample gates:** At least 120 legal deliveries in the phase or bowling comparison; at least 8 decided chases. Historical team names are harmonized to the existing project codes. Cricket rain/no-results excluded from win-rate denominators.')
        st.dataframe(r['scores'].rename(columns={'dimension':'Dimension','measured':'Actual value','score':'Relative percentile','sample':'Observed sample','required':'Minimum sample','comparison_teams':'Qualifying peer teams','definition':'Definition','eligible':'Qualified'}),use_container_width=True,hide_index=True)
        st.download_button('⬇ Export scored Team DNA dimensions',r['scores'].to_csv(index=False).encode(),
              file_name=f'IPL360_{selection.team}_team_dna.csv',mime='text/csv',key=f'dna_download_{selection.team}')
        st.download_button('⬇ Export selected franchise match evidence',r['focus'].to_csv(index=False).encode(),
              file_name=f'IPL360_{selection.team}_team_match_evidence.csv',mime='text/csv',key=f'dna_evidence_{selection.team}')
        st.caption('Source: Cricsheet IPL match-level/phase tables, through 2026; this is a retrospective descriptive assessment. No captaincy or injury status is inferred.')
