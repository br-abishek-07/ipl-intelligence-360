"""V2-H: evidence-first Team DNA and season-matched peer analytics.

Descriptive metrics only; never mix future players/models into historical features.
Team filters determine *observed team matches*. Benchmark consists of OTHER current
franchises' independent fixtures during identical selected seasons, venues and
stages; opponent filters apply to focal team only (clearly disclosed in UI).
"""
from __future__ import annotations
from dataclasses import dataclass
import numpy as np
import pandas as pd
from dashboard.analytics import TEAMS, PHASE_ORDER

CURRENT = tuple(TEAMS.keys())
PHASES = tuple(PHASE_ORDER)
DIMENSIONS = (
    ('Powerplay Batting', 'bat_pp_rr', True, 'Runs scored per over in overs 1–6', 'bat_pp_balls', 120),
    ('Middle-Over Batting', 'bat_mid_rr', True, 'Runs scored per over in overs 7–15', 'bat_mid_balls', 120),
    ('Death-Over Batting', 'bat_death_rr', True, 'Runs scored per over in overs 16–20', 'bat_death_balls', 120),
    ('Bowling Run Prevention', 'bowl_rr', False, 'Runs conceded per over; lower is better', 'bowl_balls', 120),
    ('Wicket-Taking Pressure', 'wickets_120', True, 'Opposition dismissals per 120 legal balls', 'bowl_balls', 120),
    ('Chasing Win Rate', 'chase_win_pct', True, 'Wins from decided matches while chasing', 'chases', 8),
)

@dataclass(frozen=True)
class DNASelection:
    team: str
    first: int = 2022
    last: int = 2026
    opponents: tuple[str, ...] = ()
    venues: tuple[str, ...] = ()
    stages: tuple[str, ...] = ()


def validated(selection: DNASelection):
    if selection.team not in CURRENT:raise ValueError('Select one of the ten current IPL teams')
    if selection.first > selection.last:raise ValueError('Starting season cannot exceed ending season')


def scope_frames(tm:pd.DataFrame,phase:pd.DataFrame,s:DNASelection):
    """Cohort selection, with independent peers and non-leaking fixture-level scopes."""
    validated(s)
    base = tm[tm.season_year.between(s.first,s.last)].copy()
    pids = phase.match_id.unique()
    base = base[base.match_id.isin(pids)]
    if s.venues:base=base[base.venue_group.isin(s.venues)]
    if s.stages:base=base[base.match_type.isin(s.stages)]
    focus=base[base.team_code.eq(s.team)].copy()
    if s.opponents:focus=focus[focus.opponent_code.isin(s.opponents)]
    reference=base[base.team_code.isin(CURRENT) & base.team_code.ne(s.team) & ~base.match_id.isin(focus.match_id)].copy()
    # Reference may contain both sides of peer-versus-peer matches. Each team gets
    # its own appearances for chasing; phase rows are deduplicated by delivery/inning.
    return focus,reference,base


def _ratio(n,d,mul=1.):return float(mul*n/d) if d>0 else float('nan')


def extract_metrics(t:pd.DataFrame,phase:pd.DataFrame)->dict:
    ids=t.match_id.drop_duplicates().tolist()
    codes=t.team_code.drop_duplicates().tolist()
    if not len(t) or len(codes)!=1:
        raise ValueError('Metrics require a nonempty single-franchise team appearance table')
    code=codes[0]
    p=phase[phase.match_id.isin(ids)].copy()
    bats=p[p.batting_team.eq(code)];bowls=p[p.bowling_team.eq(code)]
    out={'team':code,'matches':int(t.match_id.nunique()),'decided':int(t.is_decided.sum()),
         'wins':int(t.loc[t.is_decided,'won'].sum())}
    out['win_pct']=_ratio(out['wins'],out['decided'],100)
    chasing=t[t.is_decided & ~t.batted_first]
    out['chases']=len(chasing)
    out['chase_wins']=int(chasing.won.sum())
    out['chase_win_pct']=_ratio(out['chase_wins'],out['chases'],100)
    first=t[t.is_decided & t.batted_first]
    out['defences']=len(first);out['defence_wins']=int(first.won.sum())
    out['defence_win_pct']=_ratio(out['defence_wins'],len(first),100)
    out['bat_balls']=int(bats.legal_balls.sum());out['bowl_balls']=int(bowls.legal_balls.sum())
    out['bat_runs']=int(bats.runs.sum());out['bowl_runs']=int(bowls.runs.sum())
    out['bat_rr']=_ratio(out['bat_runs'],out['bat_balls'],6)
    out['bowl_rr']=_ratio(out['bowl_runs'],out['bowl_balls'],6)
    out['wickets']=int(bowls.wickets.sum())
    out['wickets_120']=_ratio(out['wickets'],out['bowl_balls'],120)
    out['boundary_balls']=int((bats.fours+bats.sixes).sum())
    out['boundary_pct']=_ratio(out['boundary_balls'],out['bat_balls'],100)
    for phase_name,prefix in zip(PHASES,('pp','mid','death')):
        bp=bats[bats.phase.eq(phase_name)];op=bowls[bowls.phase.eq(phase_name)]
        out[f'bat_{prefix}_balls']=int(bp.legal_balls.sum())
        out[f'bat_{prefix}_rr']=_ratio(bp.runs.sum(),bp.legal_balls.sum(),6)
        out[f'bowl_{prefix}_balls']=int(op.legal_balls.sum())
        out[f'bowl_{prefix}_rr']=_ratio(op.runs.sum(),op.legal_balls.sum(),6)
        out[f'bowl_{prefix}_wickets']=int(op.wickets.sum())
    return out


def _peer_metrics(ref:pd.DataFrame,p:pd.DataFrame):
    return pd.DataFrame([extract_metrics(g,p) for _,g in ref.groupby('team_code')]) if len(ref) else pd.DataFrame()


def peer_benchmark(ref:pd.DataFrame, phase:pd.DataFrame):
    """Independent peer aggregation weighted by balls/matches, never mean of team RR."""
    if len(ref)==0:return {}
    # Explicitly include all peer match ids for phase extraction; individual
    # bowling/batting team codes yield precisely one side per match/inning.
    peers=_peer_metrics(ref,phase)
    # Sum numerators and denominators rather than averaging peer ratios.
    def weigh(a,b,scale=1):return _ratio(peers[a].sum(),peers[b].sum(),scale)
    d={'teams':int(len(peers)),'matches':int(ref.match_id.nunique()),
       'bat_rr':weigh('bat_runs','bat_balls',6),
       'bowl_rr':weigh('bowl_runs','bowl_balls',6),
       'wickets_120':weigh('wickets','bowl_balls',120),
       'boundary_pct':weigh('boundary_balls','bat_balls',100),
       'chase_win_pct':weigh('chase_wins','chases',100),
       'defence_win_pct':weigh('defence_wins','defences',100),
       'chases':int(peers.chases.sum()),'defences':int(peers.defences.sum()),'bowl_balls':int(peers.bowl_balls.sum())}
    for x in ('pp','mid','death'):
        # Ratios only; approximate weighted averages by team legal-ball counts
        # (the exact runs recovered from RR * balls / 6).
        for pre in ('bat','bowl'):
            key=f'{pre}_{x}'
            mask=peers[f'{key}_balls']>0
            nums=(peers.loc[mask,f'{key}_rr']*peers.loc[mask,f'{key}_balls']/6).sum()
            d[f'{key}_rr']=_ratio(nums,peers.loc[mask,f'{key}_balls'].sum(),6)
    return d


def scores(focal:dict,peers:pd.DataFrame)->pd.DataFrame:
    """Percentile standing among nine independent *peer teams*. At least 5 eligible."""
    rows=[]
    for name,col,higher,desc,den,min_sample in DIMENSIONS:
        val=focal.get(col,float('nan'))
        sample=focal.get(den,0)
        qualified=(peers[peers[den]>=min_sample] if len(peers) else pd.DataFrame())
        candidates=qualified[col].replace([np.inf,-np.inf],np.nan).dropna() if len(qualified) else pd.Series(dtype=float)
        ok=sample>=min_sample and pd.notna(val) and len(candidates)>=5
        if ok:
            better=((candidates < val).sum() if higher else (candidates > val).sum())
            ties=(candidates == val).sum()
            grade=100*(better+.5*ties)/len(candidates)
        else:grade=float('nan')
        rows.append(dict(dimension=name,metric=col,measured=val,eligible=bool(ok),score=grade,
                         unit='percent' if col.endswith('_pct') else 'runs/over' if col.endswith('_rr') else 'wickets/120',
                         comparison_teams=len(candidates),sample=int(sample),required=min_sample,
                         definition=desc,preference='Higher is better' if higher else 'Lower is better'))
    return pd.DataFrame(rows)


def build_dna(tm:pd.DataFrame,phase:pd.DataFrame,s:DNASelection):
    focus,ref,base=scope_frames(tm,phase,s)
    if focus.empty:return {'focus':focus,'reference':ref,'base':base,'metrics':{},'peers':pd.DataFrame(),
                           'benchmark':{},'scores':pd.DataFrame(),'insights':['No franchise matches match the filters.']}
    metrics=extract_metrics(focus,phase)
    peers=_peer_metrics(ref,phase)
    bench=peer_benchmark(ref,phase)
    grading=scores(metrics,peers)
    return {'focus':focus,'reference':ref,'base':base,'metrics':metrics,'peers':peers,
            'benchmark':bench,'scores':grading,'insights':strategic_notes(metrics,bench,grading,focus,ref)}


def strategic_notes(metrics:dict,benchmark:dict,grading:pd.DataFrame,focus:pd.DataFrame,ref:pd.DataFrame)->list[str]:
    notes=[]
    notes.append(f"**Performance:** {metrics['wins']} wins in {metrics['decided']} decided games "
                 f"({metrics['win_pct']:.1f}%). All rates use selected fixtures, not an expected future win probability." if metrics['decided'] else
                 '**Performance:** No decided fixtures in the selected sample.')
    q=grading[grading.eligible].copy()
    if len(q):
        good=q.sort_values('score',ascending=False).iloc[0];weak=q.sort_values('score').iloc[0]
        notes.append(f"**Relative strength:** {good.dimension} ranks at the {good.score:.0f}th percentile "
                     f"among {good.comparison_teams} qualified peer franchises, based on {good.sample} observations "
                     f"({'legal balls' if good.required==120 else 'decided chase matches'}).")
        if len(q)>1:
            notes.append(f"**Area to investigate:** {weak.dimension} ranks at the {weak.score:.0f}th percentile "
                         f"against eligible peers. This is an observed gap, not proof of a tactical cause.")
    else:notes.append('**Unscored sample:** Not enough independent peer teams or balls/chases to assign a credible percentile DNA profile.')
    for phase_name,key,den in [('powerplay','bat_pp_rr','bat_pp_balls'),('middle overs','bat_mid_rr','bat_mid_balls'),('death overs','bat_death_rr','bat_death_balls')]:
        comp=benchmark.get(key,float('nan'))
        if metrics.get(den,0)>=120 and pd.notna(comp) and metrics.get(key)==metrics.get(key):
            gap=metrics[key]-comp
            if abs(gap)>=.5:notes.append(f"**Batting {phase_name}:** {metrics[key]:.2f} runs/over "
                f"vs independent peer benchmark {comp:.2f} ({gap:+.2f} runs/over). "
                f"Check opponent quality and ground conditions before acting on this difference.")
    if metrics['chases']<8:notes.append(f"**Chase evidence:** Only {metrics['chases']} decided chases; avoid strong conclusions.")
    if focus.match_id.nunique()<10:notes.append('**Small sample warning:** Fewer than 10 selected games; comparisons may be unstable.')
    notes.append(f"**Peer definition:** {len(ref):,} team appearances from {ref.match_id.nunique():,} independent games "
                 f"restricted to selected seasons" +
                 (', grounds' if 'venue_group' in focus and len(focus.venue_group.unique())==1 else '')+
                 '. Opponent filters do not narrow the peer benchmark; team-match results are not adjusted for opposition strength.')
    return notes
