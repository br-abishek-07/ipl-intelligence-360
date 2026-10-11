"""Pure, match-scoped player analytics. No Streamlit/UI dependencies.

Cricsheet IDs, not player names, are the join keys. Historical splits are
conditional descriptions rather than predictions or causal claims.
"""
from __future__ import annotations
import numpy as np
import pandas as pd

PHASES=['Powerplay (1–6)','Middle (7–15)','Death (16–20)']

def player_filter(frame:pd.DataFrame,player_id:str,year_min=None,year_max=None,
                  team='All franchises',opponent='All opponents',venue='All venues',
                  stage='All stages',role='All innings roles') -> pd.DataFrame:
    x=frame.loc[frame.player_id.eq(player_id)].copy()
    if year_min is not None:x=x.loc[x.season_year.between(year_min,year_max)]
    if team!='All franchises':x=x.loc[x.team_code.eq(team)]
    if opponent!='All opponents':x=x.loc[x.opponent_code.eq(opponent)]
    if venue!='All venues':x=x.loc[x.venue_group.eq(venue)]
    if stage!='All stages':x=x.loc[x.match_type.eq(stage)]
    if role=='Batting first':x=x.loc[x.batted_first.eq(True)]
    elif role=='Chasing':x=x.loc[x.batted_first.eq(False)]
    return x

def _safe_div(n,d):return float(n/d) if d else float('nan')

def summary(x:pd.DataFrame)->dict:
    if x.empty:return dict(matches=0,innings=0,runs=0,balls=0,bat_average=float('nan'),strike_rate=float('nan'),
                          fifties=0,hundreds=0,highest=0,fours=0,sixes=0,dismissals=0,not_outs=0,
                          bowl_innings=0,wickets=0,bowl_balls=0,conceded=0,economy=float('nan'),
                          pom=0,team_count=0,win_rate=float('nan'),won=0,decided=0)
    sums=x[['bat_runs','bat_balls','bat_dismissals','bowl_wickets','bowl_balls','bowl_runs_conceded','bat_fours','bat_sixes']].sum()
    runs=int(sums.bat_runs); balls=int(sums.bat_balls); outs=int(sums.bat_dismissals)
    bowlruns=int(sums.bowl_runs_conceded);bowballs=int(sums.bowl_balls)
    d=x[x.is_decided.astype(bool)]
    bi=x[x.batting_innings>0]
    return dict(matches=int(x.match_id.nunique()),innings=int(x.batting_innings.sum()),runs=runs,
       balls=balls,bat_average=_safe_div(runs,outs),strike_rate=_safe_div(runs*100,balls),
       fifties=int(bi.bat_runs.between(50,99).sum()),hundreds=int((bi.bat_runs>=100).sum()),
       highest=int(bi.bat_runs.max()) if len(bi) else 0,
       fours=int(sums.bat_fours),sixes=int(sums.bat_sixes),dismissals=outs,
       not_outs=int(x.is_not_out.sum()),bowl_innings=int(x.bowling_innings.sum()),
       wickets=int(sums.bowl_wickets),bowl_balls=bowballs,conceded=bowlruns,
       economy=_safe_div(bowlruns*6,bowballs),pom=int(x.pom_awards.sum()),
       team_count=int(x.team_code.nunique()),
       win_rate=_safe_div(d.won.astype(int).sum()*100,len(d)),won=int(d.won.astype(int).sum()),decided=len(d))

def seasons(x):
    if x.empty:return pd.DataFrame(columns=['season_year','matches','bat_runs','bat_balls','bowl_wickets','bowl_balls','bowl_runs_conceded','bat_fours','bat_sixes','batting_innings','bowling_innings','pom_awards','strike_rate','economy'])
    d=x.groupby('season_year',as_index=False).agg(matches=('match_id','nunique'),bat_runs=('bat_runs','sum'),bat_balls=('bat_balls','sum'),
        bat_fours=('bat_fours','sum'),bat_sixes=('bat_sixes','sum'),bowl_wickets=('bowl_wickets','sum'),
        bowl_balls=('bowl_balls','sum'),bowl_runs_conceded=('bowl_runs_conceded','sum'),
        batting_innings=('batting_innings','sum'),bowling_innings=('bowling_innings','sum'),pom_awards=('pom_awards','sum'))
    d['strike_rate']=d.bat_runs*100/d.bat_balls.replace(0,np.nan)
    d['economy']=6*d.bowl_runs_conceded/d.bowl_balls.replace(0,np.nan)
    return d.sort_values('season_year')

def by_category(x,col):
    if x.empty:return pd.DataFrame(columns=[col,'matches','runs','wickets','strike_rate','economy'])
    d=x.groupby(col,as_index=False).agg(matches=('match_id','nunique'),runs=('bat_runs','sum'),balls=('bat_balls','sum'),
                    wickets=('bowl_wickets','sum'),bowl_balls=('bowl_balls','sum'),conceded=('bowl_runs_conceded','sum'),
                    pom=('pom_awards','sum'))
    d['strike_rate']=100*d.runs/d.balls.replace(0,np.nan)
    d['economy']=6*d.conceded/d.bowl_balls.replace(0,np.nan)
    return d.sort_values(['runs','matches'],ascending=False)

def phase_breakdown(x,bat_phase,bowl_phase):
    mids=set(x.match_id.astype(str))
    # Match ID filter *and* player+team identity; avoid mixing former clubs in a season.
    index=x[['match_id','team_code','player_id']].drop_duplicates()
    b=bat_phase.merge(index,on=['match_id','team_code','player_id'],how='inner')
    w=bowl_phase.merge(index,on=['match_id','team_code','player_id'],how='inner')
    if len(b):
        b=b.groupby('phase',as_index=False)[['bat_runs','balls_faced','dots','fours','sixes']].sum()
        b['strike_rate']=100*b.bat_runs/b.balls_faced.replace(0,np.nan)
        b['dot_pct']=100*b.dots/b.balls_faced.replace(0,np.nan)
    if len(w):
        w=w.groupby('phase',as_index=False)[['legal_balls','wickets']].sum()
    return b,w

def matchup_scope(player_rows,matchup_match,selected_player_id,mode='As batter',phase='All phases'):
    ids=set(player_rows.match_id.tolist())
    d=matchup_match[matchup_match.match_id.isin(ids)].copy()
    d=d[d.batter_id.eq(selected_player_id) if mode=='As batter' else d.bowler_id.eq(selected_player_id)]
    if phase!='All phases':d=d[d.phase.eq(phase)]
    return d

def matchup_leaders(d,mode='As batter'):
    if d.empty:return pd.DataFrame(columns=['other_id','runs','balls','dismissals','fours','sixes','strike_rate','dot_pct','matches'])
    key='bowler_id' if mode=='As batter' else 'batter_id'
    a=d.groupby(key,as_index=False).agg(runs=('runs','sum'),balls=('balls','sum'),dismissals=('dismissals','sum'),
                  fours=('fours','sum'),sixes=('sixes','sum'),dots=('dots','sum'),matches=('match_id','nunique'))
    a=a.rename(columns={key:'other_id'})
    a['strike_rate']=100*a.runs/a.balls.replace(0,np.nan)
    a['dot_pct']=100*a.dots/a.balls.replace(0,np.nan)
    return a.sort_values('balls',ascending=False)

def compare_players(first,second):
    """Comparison respects filters independently for both selected players."""
    return summary(first),summary(second)

def sample_note(rows,min_matches=5):
    return ('Small sample: only %s recorded matches; conclusions may be unstable.'%len(rows)) if len(rows)<min_matches else ''
