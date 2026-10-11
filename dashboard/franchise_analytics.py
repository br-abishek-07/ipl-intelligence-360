"""IPL Intelligence 360 V2-C — match-scoped, team-specific sports intelligence.

Rules
-----
* Every scoped metric shares the same filtered TEAM match IDs.
* Team batting and bowling records are filtered by team and match ID, not merely year.
* All-time trophy history is intentionally NOT affected by active page filters.
* Match-list participants in Cricsheet are NOT verified starting XIs/captains.
* Aggregations are descriptive, not predictive or causal.
"""
from __future__ import annotations
from dataclasses import dataclass
from typing import Optional
import numpy as np
import pandas as pd
from dashboard.analytics import TEAMS, ALL_TEAMS, PHASE_ORDER

PLAYOFF_STAGES={'Qualifier 1','Qualifier 2','Eliminator','Final','Semi Final','Elimination Final'}

@dataclass(frozen=True)
class TeamSelection:
    team: str
    year_min: int=2008
    year_max: int=2026
    opponents: tuple[str,...]=()
    venues: tuple[str,...]=()
    stages: tuple[str,...]=()
    outcome: str='All results'
    innings: str='Both innings roles'
    toss: str='All toss outcomes'
    player_id: Optional[str]=None


def select_team_matches(tm:pd.DataFrame, selection:TeamSelection, lineups:pd.DataFrame|None=None)->pd.DataFrame:
    """Single match-universe generator. All filters are intersections."""
    if selection.year_min>selection.year_max:raise ValueError('Invalid season interval')
    t=tm[(tm.team_code==selection.team)&tm.season_year.between(selection.year_min,selection.year_max)].copy()
    if selection.opponents:t=t[t.opponent_code.isin(selection.opponents)]
    if selection.venues:t=t[t.venue_group.isin(selection.venues)]
    if selection.stages:t=t[t.match_type.isin(selection.stages)]
    if selection.outcome=='Won':t=t[t.won.astype(bool)]
    elif selection.outcome=='Lost':t=t[t.lost.astype(bool)]
    elif selection.outcome=='No result':t=t[t.no_result.astype(bool)]
    if selection.innings=='Batted first':t=t[t.batted_first.astype(bool)]
    elif selection.innings=='Chased':t=t[~t.batted_first.astype(bool)]
    if selection.toss=='Won toss':t=t[t.toss_won.astype(bool)]
    elif selection.toss=='Lost toss':t=t[~t.toss_won.astype(bool)]
    if selection.player_id is not None:
        if lineups is None:raise ValueError('Player filter requires match participant records')
        seen=lineups[(lineups.team_code==selection.team)&(lineups.cricsheet_player_id==selection.player_id)].match_id.unique()
        t=t[t.match_id.isin(seen)]
    assert t.match_id.is_unique,'Expected one team appearance per match'
    return t.sort_values(['match_date','match_id']).reset_index(drop=True)


def team_scope(match_ids, code:str, innings:pd.DataFrame, phase:pd.DataFrame, bat:pd.DataFrame,bowl:pd.DataFrame)->dict[str,pd.DataFrame]:
    ids=set(match_ids)
    def sub(frame):return frame[frame.match_id.isin(ids)].copy()
    i=sub(innings);p=sub(phase);b=sub(bat);w=sub(bowl)
    return {'innings':i[i.batting_team_code==code],
            'bat_phase':p[p.batting_team==code],
            'bowl_phase':p[p.bowling_team==code],
            'bat':b[b.team_code==code], 'bowl':w[w.team_code==code],
            'all_phase':p}


def rate(n,d,scale=100):return float(scale*n/d) if d else float('nan')


def count_stats(t:pd.DataFrame,scoped:dict)->dict:
    decided=t[t.is_decided.astype(bool)]
    p=scoped['bat_phase']; b=scoped['bowl_phase'];inn=scoped['innings']
    wins=int(decided.won.sum()); n=len(t)
    finals=t[t.match_type=='Final']
    titles=int(((finals.winner_final_code==t.team_code.iloc[0]) if n else pd.Series(dtype=bool)).sum())
    return dict(matches=n,decided=len(decided),wins=wins,losses=int(decided.lost.sum()),
        no_result=n-len(decided),win_pct=rate(wins,len(decided)),
        runs_scored=int(p.runs.sum()),runs_conceded=int(b.runs.sum()),
        wickets_taken=int(b.wickets.sum()),wickets_lost=int(p.wickets.sum()),
        batting_rr=rate(p.runs.sum(),p.legal_balls.sum(),6),
        bowling_rr=rate(b.runs.sum(),b.legal_balls.sum(),6),
        batting_boundary_rate=rate(p.fours.sum()+p.sixes.sum(),p.legal_balls.sum()),
        batting_sixes=int(p.sixes.sum()),
        first_innings_matches=int(t.batted_first.sum()) if n else 0,
        chase_wins=int(decided.loc[~decided.batted_first.astype(bool),'won'].sum()) if n else 0,
        finals=len(finals),titles=titles,
        highest_total=int(inn.runs.max()) if not inn.empty else None,
        batting_innings=len(inn),
        batting_run_average=rate(p.runs.sum(),len(inn),1))


def playoff_history(full_matches:pd.DataFrame,code:str)->pd.DataFrame:
    """Actual finals and playoff presence (not an inferred points-table qualification)."""
    mask=(full_matches.team1_code==code)|(full_matches.team2_code==code)
    matches=full_matches[mask].copy()
    active=matches[matches.match_type.isin(PLAYOFF_STAGES)]
    finals=matches[matches.match_type=='Final']
    seasons=sorted(set(active.season_year.astype(int)))
    rows=[]
    for y in seasons:
        fin=finals[finals.season_year==y]
        won=not fin.empty and bool((fin.winner_final_code==code).any())
        rows.append({'season':int(y),'outcome':'Champion' if won else ('Runner-up' if len(fin) else 'Playoffs'),
          'champion':bool(won),'finalist':bool(len(fin))})
    return pd.DataFrame(rows,columns=['season','outcome','champion','finalist'])


def player_leaders(bat:pd.DataFrame,bowl:pd.DataFrame)->dict[str,pd.DataFrame]:
    if not bat.empty:
        b=bat.groupby('player_id',dropna=False).agg(player_name=('player_name','last'),
           matches=('match_id','nunique'),runs=('runs','sum'),balls=('balls','sum'),
           fours=('fours','sum'),sixes=('sixes','sum')).reset_index()
        b['strike_rate']=100*b.runs/b.balls.replace(0,np.nan)
        b=b.sort_values(['runs','balls'],ascending=[False,True])
    else:b=pd.DataFrame(columns=['player_id','player_name','matches','runs','balls','fours','sixes','strike_rate'])
    if not bowl.empty:
        w=bowl.groupby('player_id',dropna=False).agg(player_name=('player_name','last'),
           matches=('match_id','nunique'),wickets=('wickets','sum'),balls=('balls','sum'),runs_conceded=('runs_conceded','sum')).reset_index()
        w['economy']=6*w.runs_conceded/w.balls.replace(0,np.nan)
        w=w.sort_values(['wickets','economy'],ascending=[False,True])
    else:w=pd.DataFrame(columns=['player_id','player_name','matches','wickets','balls','runs_conceded','economy'])
    return {'batting':b,'bowling':w}


def phase_table(phase:pd.DataFrame)->pd.DataFrame:
    if phase.empty:return pd.DataFrame(columns=['phase','runs','balls','wickets','fours','sixes','run_rate','boundary_pct'])
    p=phase.groupby('phase',observed=True).agg(runs=('runs','sum'),balls=('legal_balls','sum'),wickets=('wickets','sum'),fours=('fours','sum'),sixes=('sixes','sum')).reindex(PHASE_ORDER).reset_index()
    p['run_rate']=6*p.runs/p.balls.replace(0,np.nan)
    p['boundary_pct']=100*(p.fours+p.sixes)/p.balls.replace(0,np.nan)
    return p


def opponents_table(t:pd.DataFrame)->pd.DataFrame:
    t=t[t.is_decided.astype(bool)]
    if t.empty:return pd.DataFrame(columns=['opponent_code','matches','wins','win_pct'])
    x=t.groupby('opponent_code').agg(matches=('match_id','size'),wins=('won','sum')).reset_index()
    x['win_pct']=100*x.wins/x.matches
    x['name']=x.opponent_code.map(ALL_TEAMS).fillna(x.opponent_code)
    return x.sort_values(['matches','wins'],ascending=False)


def venues_table(t:pd.DataFrame)->pd.DataFrame:
    t=t[t.is_decided.astype(bool)]
    if t.empty:return pd.DataFrame(columns=['venue_group','matches','wins','win_pct'])
    x=t.groupby('venue_group').agg(matches=('match_id','size'),wins=('won','sum')).reset_index()
    x['win_pct']=100*x.wins/x.matches
    return x.sort_values('matches',ascending=False)


def analyst_brief(t:pd.DataFrame,scoped:dict,all_scope:dict,code:str)->list[str]:
    notes=[];dec=t[t.is_decided.astype(bool)];n=len(dec)
    if n==0:return ['No completed matches in this selection. Expand your filters to obtain a meaningful analysis.']
    wins=int(dec.won.sum())
    notes.append(f'**Results:** {wins} wins from {n} decided matches ({100*wins/n:.1f}%). Results are descriptive, not a forecast.')
    innings=dec.groupby('batted_first').agg(matches=('match_id','size'),wins=('won','sum'))
    if set(innings.index)=={True,False} and innings.matches.min()>=5:
        first=innings.loc[True,'wins']/innings.loc[True,'matches'];chase=innings.loc[False,'wins']/innings.loc[False,'matches']
        notes.append(f'**Match approach:** chasing win rate {chase:.1%} in {int(innings.loc[False,"matches"])} games versus {first:.1%} when batting first in {int(innings.loc[True,"matches"])}. Opponent and ground effects are uncontrolled.')
    bp=phase_table(scoped['bat_phase']);lg=phase_table(all_scope['all_phase'])
    x=bp.merge(lg[['phase','run_rate']],on='phase',suffixes=('_team','_league'))
    x=x[(x.balls>=120)&(x.run_rate_league.notna())]
    if len(x):
        x=x.assign(gap=x.run_rate_team-x.run_rate_league)
        best=x.sort_values('gap',ascending=False).iloc[0]
        notes.append(f'**Batting identity:** strongest relative scoring phase was {best.phase}, at {best.run_rate_team:.2f} runs/over versus {best.run_rate_league:.2f} across the same selected matches (sample: {int(best.balls)} legal balls).')
    bow=phase_table(scoped['bowl_phase']);y=bow.merge(lg[['phase','run_rate']],on='phase',suffixes=('_team','_league'))
    y=y[(y.balls>=120)&(y.run_rate_league.notna())]
    if len(y):
        y=y.assign(gap=y.run_rate_team-y.run_rate_league)
        best=y.sort_values('gap').iloc[0]
        notes.append(f'**Bowling pressure:** best relative run prevention occurred in {best.phase}: {best.run_rate_team:.2f} conceded runs/over against {best.run_rate_league:.2f} across the selected fixtures.')
    opp=opponents_table(t);opp=opp[opp.matches>=5]
    if len(opp):
        strongest=opp.sort_values(['win_pct','matches'],ascending=[False,False]).iloc[0]
        notes.append(f'**Rivalry record:** highest win rate against opponents with at least five decided games was versus {strongest["name"]}: {strongest.wins}/{strongest.matches} ({strongest.win_pct:.1f}%).')
    if n<20:notes.append(f'**Sample warning:** only {n} decided matches pass the current filters; avoid treating rankings as stable strengths.')
    return notes



def verified_captain_stats(t:pd.DataFrame, registry:pd.DataFrame, lineups:pd.DataFrame)->pd.DataFrame:
    """Captain records are opt-in and strict: cited, unique, observed player/team/match.

    This checks structure; researchers must independently verify cited source content.
    No records are inferred from IPL lineups.
    """
    cols=['captain_player_id','captain_player_name','matches','decided','wins','win_pct','finals_won']
    if t.empty or registry is None or registry.empty:return pd.DataFrame(columns=cols)
    required={'match_id','team_code','captain_player_id','captain_player_name','source_url'}
    if not required.issubset(registry.columns):raise ValueError('Captain registry lacks required columns')
    team=t.team_code.iloc[0]
    rows=registry[(registry.team_code==team)&registry.match_id.isin(t.match_id)].copy()
    if rows.empty:return pd.DataFrame(columns=cols)
    if rows.duplicated(['match_id','team_code']).any():raise ValueError('Multiple captains recorded for one franchise-match')
    if not rows.source_url.fillna('').astype(str).str.match(r'^https?://').all():
        raise ValueError('Every captain entry requires an attributable web source')
    if rows[['captain_player_id','captain_player_name']].isna().any().any():
        raise ValueError('Captain identity cannot be blank')
    participants=lineups[lineups.team_code==team][['match_id','cricsheet_player_id']].drop_duplicates()
    valid=rows.merge(participants,left_on=['match_id','captain_player_id'],right_on=['match_id','cricsheet_player_id'],how='left',indicator=True)
    if not valid['_merge'].eq('both').all():raise ValueError('Captain record fails match/player registry membership check')
    linked=rows.merge(t[['match_id','is_decided','won','match_type']],on='match_id',validate='one_to_one')
    linked['wins_verified']=linked.won.astype(bool)&linked.is_decided.astype(bool)
    linked['final_won']=linked.wins_verified&(linked.match_type=='Final')
    x=linked.groupby(['captain_player_id','captain_player_name'],dropna=False).agg(
        matches=('match_id','nunique'),decided=('is_decided','sum'),wins=('wins_verified','sum'),
        finals_won=('final_won','sum')).reset_index()
    x['win_pct']=100*x.wins/x.decided.replace(0,np.nan)
    return x[cols].sort_values(['finals_won','wins','win_pct'],ascending=[False,False,False])

