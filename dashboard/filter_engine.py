"""Match-grain, id-synchronized filters for V2 League EDA.
No model training feature uses these retrospective aggregates.
"""
from dataclasses import dataclass
from typing import Optional
import numpy as np
import pandas as pd

@dataclass(frozen=True)
class LeagueSelection:
    start: int = 2008
    end: int = 2026
    team: str = 'All teams'
    venue: str = 'All venues'
    stage: str = 'All stages'
    toss: str = 'Any toss decision'
    role: str = 'Either innings role'
    result: str = 'Any result'


def select_matches(m:pd.DataFrame, team_matches:pd.DataFrame, f:LeagueSelection)->pd.DataFrame:
    """A match can occur only once; filters based on a selected franchise are perspective-relative."""
    if f.start > f.end: raise ValueError('Invalid season interval')
    s=m[m.season_year.between(f.start,f.end)].copy()
    if f.venue!='All venues':s=s[s.venue_group==f.venue]
    if f.stage!='All stages':s=s[s.match_type==f.stage]
    if f.toss!='Any toss decision':s=s[s.toss_decision==f.toss]
    if f.team!='All teams':
        t=team_matches[team_matches.team_code==f.team]
        if f.role=='Batted first':t=t[t.batted_first.astype(bool)]
        elif f.role=='Chased':t=t[~t.batted_first.astype(bool)]
        if f.result=='Won':t=t[t.won.astype(bool)]
        elif f.result=='Lost':t=t[t.lost.astype(bool)]
        elif f.result=='No result':t=t[t.no_result.astype(bool)]
        s=s[s.match_id.isin(t.match_id)]
    return s.sort_values(['season_year','match_date','match_id']).reset_index(drop=True)


def scoped(df:pd.DataFrame, matches:pd.DataFrame)->pd.DataFrame:
    """Reuse the *same* selected match IDs for match-level innings, phase and player tables."""
    return df[df.match_id.isin(matches.match_id)].copy()


def season_evolution(m:pd.DataFrame, innings:pd.DataFrame)->pd.DataFrame:
    if m.empty:return pd.DataFrame(columns=['season_year','matches','decided','eligible_first_innings','mean_first_innings','total_runs'])
    s=m.groupby('season_year').agg(matches=('match_id','size'),decided=('is_decided','sum')).reset_index()
    v=innings[(innings.inning==1)&(~innings.is_dls.astype(bool))&(innings.legal_balls>=100)]
    g=v.groupby('season_year').agg(eligible_first_innings=('runs','size'),mean_first_innings=('runs','mean')).reset_index()
    totals=innings.groupby('season_year').agg(total_runs=('runs','sum')).reset_index()
    return s.merge(g,on='season_year',how='left').merge(totals,on='season_year',how='left')


def phase_evolution(phase:pd.DataFrame)->pd.DataFrame:
    cols=['phase','runs','legal_balls','wickets','fours','sixes','run_rate','boundary_per_100_balls']
    if phase.empty:return pd.DataFrame(columns=cols)
    a=phase.groupby('phase',observed=True).agg(runs=('runs','sum'),legal_balls=('legal_balls','sum'),wickets=('wickets','sum'),fours=('fours','sum'),sixes=('sixes','sum')).reset_index()
    a['run_rate'] = 6*a.runs/a.legal_balls.replace(0,np.nan)
    a['boundary_per_100_balls']=100*(a.fours+a.sixes)/a.legal_balls.replace(0,np.nan)
    return a[cols]


def player_leaders(table:pd.DataFrame, matches:pd.DataFrame, team:Optional[str]=None, role='bat',limit=12)->pd.DataFrame:
    t=scoped(table,matches)
    if team and team!='All teams':t=t[t.team_code==team]
    if t.empty:return t
    if role=='bat':
        g=t.groupby('player_id').agg(player_name=('player_name','last'),runs=('runs','sum'),balls=('balls','sum'),fours=('fours','sum'),sixes=('sixes','sum'),matches=('match_id','nunique')).reset_index()
        g['strike_rate']=100*g.runs/g.balls.replace(0,np.nan)
        return g.sort_values(['runs','balls'],ascending=[False,True]).head(limit)
    if role=='bowl':
        g=t.groupby('player_id').agg(player_name=('player_name','last'),wickets=('wickets','sum'),balls=('balls','sum'),runs_conceded=('runs_conceded','sum'),matches=('match_id','nunique')).reset_index()
        g['economy']=6*g.runs_conceded/g.balls.replace(0,np.nan)
        return g.sort_values(['wickets','runs_conceded'],ascending=[False,True]).head(limit)
    raise ValueError('role must be bat or bowl')


def league_kpis(m:pd.DataFrame, innings:pd.DataFrame, phases:pd.DataFrame)->dict:
    decided=m[m.is_decided.astype(bool)]
    eligible=innings[(innings.inning==1)&(~innings.is_dls.astype(bool))&(innings.legal_balls>=100)]
    chase=innings[(innings.inning==2)&(~innings.is_dls.astype(bool))][['match_id','batting_team_code']].drop_duplicates('match_id')
    c=decided[~decided.is_dls.astype(bool)].merge(chase,on='match_id',how='inner',validate='one_to_one')
    toss=decided[decided.toss_winner_code.notna()]
    total_balls=phases.legal_balls.sum() if not phases.empty else 0
    return dict(
        matches=len(m),decided=len(decided),unresolved=int(len(m)-len(decided)),
        venues=int(m.venue_group.nunique()),runs=int(innings.runs.sum()),
        wickets=int(innings.wickets.sum()),
        average_first_innings=(float(eligible.runs.mean()) if not eligible.empty else np.nan),
        eligible_first_innings=len(eligible),
        chase_win_pct=(float((c.winner_final_code==c.batting_team_code).mean()*100) if len(c) else np.nan),
        chase_sample=len(c),
        toss_win_pct=(float((toss.winner_final_code==toss.toss_winner_code).mean()*100) if len(toss) else np.nan),
        toss_sample=len(toss),
        fours=int(phases.fours.sum()),sixes=int(phases.sixes.sum()),
        boundary_per_100_balls=(float(100*(phases.fours.sum()+phases.sixes.sum())/total_balls) if total_balls else np.nan),
        run_rate=(float(6*phases.runs.sum()/total_balls) if total_balls else np.nan),
        super_overs=int((m.winner_resolution=='super_over').sum()),
        dls=int(m.is_dls.astype(bool).sum()),
        highest_innings=(int(innings.runs.max()) if len(innings) else None),
    )


def evidence_notes(m:pd.DataFrame, innings:pd.DataFrame, phases:pd.DataFrame,k:dict)->list[str]:
    if m.empty:return ['No matches found. Broaden the filters to generate analysis.']
    notes=[]
    n=k['eligible_first_innings']
    if n>=10:
        notes.append(f"**Scoring environment:** {k['average_first_innings']:.1f} runs in {n} qualifying first innings (≥100 legal balls and no DLS). This is not a full-20-over par estimate.")
    else:notes.append(f"**Scoring sample warning:** Only {n} eligible first innings. A stable scoring benchmark cannot be inferred.")
    if k['chase_sample']>=10:
        notes.append(f"**Chasing:** {k['chase_win_pct']:.1f}% of {k['chase_sample']} decided, non-DLS matches with a recorded second innings were won by the chasing side. Venue and opposition may affect this association.")
    else: notes.append('**Chasing:** Too few eligible decided matches for a reliable aggregate.')
    p=phase_evolution(phases)
    if len(p):
        p=p[p.legal_balls>=60].sort_values('run_rate',ascending=False)
        if len(p):
            r=p.iloc[0];notes.append(f"**Match-phase pattern:** {r.phase} has the highest observed scoring rate at {r.run_rate:.2f} runs/over over {int(r.legal_balls):,} legal balls in this selection. Not an opponent-adjusted rating.")
    if len(m)<20:notes.append(f'**Uncertainty:** Only {len(m)} matches meet all selected filters; rankings may be unstable.')
    return notes
