"""V2-D: explainable, fully match-ID-scoped cricket visuals. Pure pandas/Plotly.

These functions accept already-filtered V2-C team match records and scopes.
They do not look at future seasons, do not estimate captains, and do not
silently turn no-results into losses. Use hover data to audit samples.
"""
from __future__ import annotations
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from dashboard.analytics import PHASE_ORDER, ALL_TEAMS
from dashboard.franchise_analytics import phase_table,opponents_table,venues_table,player_leaders

BG='rgba(0,0,0,0)'
OTHER='#8CA4BE'
GOLD='#E9BE70'
RED='#E96E86'
BLUE='#74CBE9'

def finish(fig,accent,height=335,percent_axis=None):
    fig.update_layout(template='plotly_dark',height=height,
        paper_bgcolor=BG,plot_bgcolor=BG,
        margin=dict(l=10,r=12,t=43,b=35),
        font=dict(family='Arial, sans-serif',color='#E9F2FC',size=12),
        legend=dict(orientation='h',y=-.24,x=0,title_text=''),
        hoverlabel=dict(bgcolor='#142641',font_size=12),
        transition=dict(duration=240,easing='cubic-in-out'),
        uirevision='filtered-franchise',
        hovermode='closest')
    fig.update_xaxes(gridcolor='rgba(163,194,228,.10)',zeroline=False)
    fig.update_yaxes(gridcolor='rgba(163,194,228,.10)',zeroline=False)
    if percent_axis:fig.update_layout(**{f'{percent_axis}axis':dict(range=[0,100],ticksuffix='%')})
    return fig

def season_result_table(t):
    d=t.groupby('season_year').agg(matches=('match_id','size'),wins=('won','sum'),losses=('lost','sum'),
       decided=('is_decided','sum'),runs_for=('runs_for','sum'),runs_against=('runs_against','sum')).reset_index()
    d['win_pct']=100*d.wins/d.decided.replace(0,np.nan)
    d['avg_runs_for']=d.runs_for/d.matches.replace(0,np.nan)
    d['avg_runs_against']=d.runs_against/d.matches.replace(0,np.nan)
    d['no_result']=d.matches-d.decided
    return d

def phase_compare_data(s):
    own=phase_table(s['bat_phase']);ref=phase_table(s['all_phase'])
    a=own[['phase','run_rate']].rename(columns={'run_rate':'Franchise'})
    r=ref[['phase','run_rate']].rename(columns={'run_rate':'Opponent + franchise in selected fixtures'})
    return a.merge(r,on='phase').melt(id_vars='phase',var_name='Series',value_name='Runs per over')

def season_combo(t,accent):
    d=season_result_table(t)
    fig=go.Figure()
    for name,field,color in [('Wins','wins',accent),('Losses','losses',RED),('No result','no_result',OTHER)]:
        fig.add_trace(go.Bar(x=d.season_year.astype(str),y=d[field],name=name,marker_color=color,
                             customdata=np.stack([d.matches,d.decided],axis=-1),
                             hovertemplate='%{x}<br>'+name+': %{y}<br>Matches: %{customdata[0]}<br>Decided: %{customdata[1]}<extra></extra>'))
    fig.update_layout(barmode='group',title='Matches Won, Lost and Without Result by Season',yaxis_title='Matches')
    return finish(fig,accent,355)

def form_line(t,accent):
    d=t[t.is_decided.astype(bool)].sort_values(['match_date','match_id']).copy()
    d['rolling_win_pct']=d.won.astype(int).rolling(window=10,min_periods=5).mean()*100
    fig=px.line(d,x='match_date',y='rolling_win_pct',markers=False,
                labels={'match_date':'Match date','rolling_win_pct':'Win % (last 10 decided games)'},
                title='Recent Form: Win Rate Across the Last 10 Decided Matches',color_discrete_sequence=[accent])
    fig.update_traces(line_width=3,fill=None)
    fig.update_yaxes(range=[0,100],ticksuffix='%')
    return finish(fig,accent,355)

def scoring_area(t,accent):
    d=season_result_table(t)
    fig=px.area(d,x='season_year',y='avg_runs_for',markers=True,
        title='Average Runs Scored per Match, by Season',
        labels={'season_year':'Season','avg_runs_for':'Runs per selected match'},
        color_discrete_sequence=[accent])
    fig.update_traces(line_width=2,fillcolor='rgba(107,190,221,.20)')
    return finish(fig,accent,340)

def scoring_scatter(t,accent):
    d=t[t.is_decided.astype(bool)].copy()
    d['Outcome']=np.where(d.won.astype(bool),'Won','Lost')
    d['Role']=np.where(d.batted_first.astype(bool),'Batted first','Chased')
    d['Opponent']=d.opponent_code.map(ALL_TEAMS).fillna(d.opponent_code)
    fig=px.scatter(d,x='runs_for',y='runs_against',color='Outcome',symbol='Role',
        hover_name='Opponent',hover_data={'season_year':True,'match_date':True,'match_type':True,'Role':True},
        color_discrete_map={'Won':accent,'Lost':RED},opacity=.73,
        title='Team Runs Scored vs Runs Conceded (Each Dot = One Match)',
        labels={'runs_for':'Franchise score (runs)','runs_against':'Opponent score (runs)'})
    fig.add_shape(type='line',x0=0,y0=0,x1=max(1,d[['runs_for','runs_against']].max().max()),y1=max(1,d[['runs_for','runs_against']].max().max()),
                  line=dict(color=OTHER,width=1,dash='dot'))
    return finish(fig,accent,405)

def phase_grouped(s,accent,bowling=False):
    own=phase_table(s['bowl_phase'] if bowling else s['bat_phase'])
    ref=phase_table(s['all_phase'])
    name='Conceded by franchise' if bowling else 'Scored by franchise'
    d=pd.concat([own[['phase','run_rate']].assign(Series=name),
                 ref[['phase','run_rate']].assign(Series='Selected fixtures overall')])
    fig=px.bar(d,x='phase',y='run_rate',color='Series',barmode='group',category_orders={'phase':PHASE_ORDER},
        color_discrete_map={name:accent,'Selected fixtures overall':OTHER},
        labels={'run_rate':'Runs per six legal balls','phase':'Match phase'},
        title=('Runs Conceded per Over: Powerplay, Middle and Death Overs' if bowling else 'Batting Runs per Over: Powerplay, Middle and Death Overs')+' — Team vs Selected-Fixture Benchmark')
    return finish(fig,accent)

def boundary_stacked(s,accent):
    d=phase_table(s['bat_phase']).copy()
    # This is actual counts, not rates: label the differing phase lengths explicitly.
    d=d.melt(id_vars='phase',value_vars=['fours','sixes'],var_name='Boundary',value_name='Count')
    fig=px.bar(d,x='phase',y='Count',color='Boundary',barmode='stack',
      color_discrete_map={'fours':accent,'sixes':GOLD},category_orders={'phase':PHASE_ORDER},
      title='Fours and Sixes Hit During Each Innings Phase')
    return finish(fig,accent)

def bat_scatter(leaders,accent):
    d=leaders['batting'].copy()
    d=d[d.balls>=60].copy()
    if d.empty:return None
    d=d.sort_values('runs',ascending=False).head(65)
    fig=px.scatter(d,x='runs',y='strike_rate',size='matches',size_max=29,
      hover_name='player_name',hover_data=['matches','balls','fours','sixes'],
      color_discrete_sequence=[accent],opacity=.80,
      labels={'runs':'Runs in selection','strike_rate':'Strike rate','matches':'Batting matches'},
      title='Batters: Runs Scored vs Strike Rate (Minimum 60 Balls)')
    return finish(fig,accent,380)

def bat_horizontal(leaders,accent):
    d=leaders['batting'].head(12).sort_values('runs')
    if d.empty:return None
    fig=px.bar(d,x='runs',y='player_name',orientation='h',
        hover_data=['matches','balls','strike_rate'],
        color_discrete_sequence=[accent],title='Top 12 Run-Scorers for the Selected Franchise',
        labels={'runs':'Runs','player_name':''})
    return finish(fig,accent,410)

def bow_scatter(leaders,accent):
    d=leaders['bowling'].copy()
    d=d[(d.balls>=60)&np.isfinite(d.economy)].sort_values('wickets',ascending=False).head(65)
    if d.empty:return None
    fig=px.scatter(d,x='wickets',y='economy',size='balls',size_max=27,
      hover_name='player_name',hover_data=['matches','balls','runs_conceded'],
      color_discrete_sequence=[accent],opacity=.82,
      labels={'wickets':'Credited wickets','economy':'Runs conceded / over','balls':'Legal balls bowled'},
      title='Bowlers: Wickets Taken vs Runs Conceded per Over (Minimum 60 Balls)')
    return finish(fig,accent,380)

def bow_horizontal(leaders,accent):
    d=leaders['bowling'].head(12).sort_values('wickets')
    if d.empty:return None
    fig=px.bar(d,x='wickets',y='player_name',orientation='h',
       hover_data=['matches','balls','economy'],color_discrete_sequence=[accent],
       title='Top 12 Wicket-Takers for the Selected Franchise',labels={'wickets':'Credited wickets','player_name':''})
    return finish(fig,accent,410)

def bowling_wickets_by_phase(s,accent):
    d=phase_table(s['bowl_phase']).copy();d['wickets_per_120']=120*d.wickets/d.balls.replace(0,np.nan)
    fig=px.bar(d,x='phase',y='wickets_per_120',color_discrete_sequence=[accent],
      category_orders={'phase':PHASE_ORDER},
      title='Dismissals per 120 Balls, by Bowling Phase',
      labels={'wickets_per_120':'Dismissals / 120 legal balls','phase':'Phase'})
    return finish(fig,accent)

def rival_stacked(t,accent):
    d=opponents_table(t)
    if d.empty:return None
    d=d.sort_values('matches',ascending=False).head(12).copy()
    d['Losses']=d.matches-d.wins
    d=d.sort_values('matches')
    fig=go.Figure()
    for col,color in [('wins',accent),('Losses',RED)]:
        fig.add_trace(go.Bar(x=d[col],y=d.name,orientation='h',name=col.title(),marker_color=color,
            hovertemplate='%{y}<br>'+col.title()+': %{x}<extra></extra>'))
    fig.update_layout(barmode='stack',title='Matches Won and Lost Against Each Opponent',xaxis_title='Decided meetings',yaxis_title='')
    return finish(fig,accent,395)

def venue_bubbles(t,accent):
    d=venues_table(t)
    d=d[d.matches>=3].head(24).copy()
    if d.empty:return None
    # Avoid excessive unreadable labels for venues, show them only in hover.
    d['ground']=d.venue_group.astype(str).str.slice(0,24)
    fig=px.scatter(d,x='matches',y='win_pct',size='matches',size_max=30,
       hover_name='venue_group',hover_data=['wins'],color_discrete_sequence=[accent],
       title='Venue Win Rate vs Matches Played (At Least 3 Decided Games)',
       labels={'matches':'Decided matches','win_pct':'Win rate (%)'})
    fig.update_yaxes(range=[0,100],ticksuffix='%')
    return finish(fig,accent,375)

def score_distribution(s,accent):
    d=s['innings'].copy()
    if d.empty:return None
    fig=px.histogram(d,x='runs',nbins=20,
        title='How Often the Team Scored Each Innings Total',
        labels={'runs':'Runs per regulation innings'},color_discrete_sequence=[accent])
    return finish(fig,accent,345)

def season_win_pct_fig(t,accent):
    d=season_result_table(t)
    fig=px.line(d,x='season_year',y='win_pct',markers=True,color_discrete_sequence=[accent],
        labels={'season_year':'Season','win_pct':'Decided-match win rate (%)'},
        title='Season-by-Season Percentage of Decided Matches Won')
    fig.update_yaxes(range=[0,100],ticksuffix='%')
    fig.update_traces(line_width=3,marker_size=8)
    return finish(fig,accent)

def season_win_combo(t,accent):
    """Combined LINE + CLUSTERED COLUMN: season win/loss counts + win percentage."""
    from plotly.subplots import make_subplots
    d=season_result_table(t)
    fig=make_subplots(specs=[[{'secondary_y':True}]])
    for label,column,color in [('Wins','wins',accent),('Losses','losses',RED)]:
        fig.add_trace(go.Bar(x=d.season_year.astype(str),y=d[column],name=label,
                     marker_color=color,offsetgroup=label,hovertemplate='%{x}<br>'+label+': %{y}<extra></extra>'),secondary_y=False)
    fig.add_trace(go.Scatter(x=d.season_year.astype(str),y=d.win_pct,name='Win rate',mode='lines+markers',
                     line=dict(color=GOLD,width=3),marker=dict(size=7),
                     hovertemplate='%{x}<br>Win rate: %{y:.1f}%<extra></extra>'),secondary_y=True)
    fig.update_layout(title='Seasonal Wins and Losses (Bars) with Win Rate (Line)',barmode='group')
    fig.update_yaxes(title_text='Matches',secondary_y=False)
    fig.update_yaxes(title_text='Win rate (%)',range=[0,100],ticksuffix='%',secondary_y=True,showgrid=False)
    return finish(fig,accent,400)

def phase_trends(s,accent,bowling=False):
    """Changing run rate by match phase, normalized for unequal phase lengths."""
    d=s['bowl_phase' if bowling else 'bat_phase']
    if d.empty:return None
    g=d.groupby(['season_year','phase'],observed=True).agg(
        runs=('runs','sum'),balls=('legal_balls','sum')).reset_index()
    g['run_rate']=6*g.runs/g.balls.replace(0,np.nan)
    fig=px.line(g,x='season_year',y='run_rate',color='phase',markers=True,
          category_orders={'phase':PHASE_ORDER},
          color_discrete_map={PHASE_ORDER[0]:accent,PHASE_ORDER[1]:BLUE,PHASE_ORDER[2]:GOLD},
          labels={'run_rate':'Runs per six legal balls','season_year':'Season','phase':'Phase'},
          title=('Bowling' if bowling else 'Batting')+' Run Rate by Innings Phase Across Seasons')
    fig.update_traces(line_width=2,marker_size=5)
    return finish(fig,accent,380)
