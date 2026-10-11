"""V2-E pure evidence-based IPL records, legends and match awards.

All batting/bowling records come from per-player match contributions; awards from
Cricsheet's info.player_of_match with stable person ID and team membership.
No guesswork concerning captains or unsourced player achievements.
"""
from __future__ import annotations
import pandas as pd
from dashboard.franchise_analytics import playoff_history


def limit_awards(awards: pd.DataFrame, match_ids, team: str | None = None) -> pd.DataFrame:
    result = awards[awards.match_id.isin(set(match_ids)) & awards.identity_status.eq('verified_unique_match_participant')].copy()
    if team and team != 'All teams':
        result = result[result.team_code.eq(team)]
    return result


def player_award_leaders(awards: pd.DataFrame) -> pd.DataFrame:
    if awards.empty:
        return pd.DataFrame(columns=['player_id','player_name','team_code','awards','first_season','last_season'])
    return (awards.groupby(['player_id','player_name','team_code'],as_index=False)
            .agg(awards=('match_id','nunique'),first_season=('season_year','min'),last_season=('season_year','max'))
            .sort_values(['awards','player_name'],ascending=[False,True]).reset_index(drop=True))


def batting_records(batting: pd.DataFrame, match_ids, team: str | None = None) -> pd.DataFrame:
    d=batting[batting.match_id.isin(set(match_ids))].copy()
    if team and team!='All teams':d=d[d.team_code.eq(team)]
    if d.empty:return pd.DataFrame(columns=['player_id','player_name','team_code','innings','runs','highest_score','fifties','centuries','sixes','strike_rate'])
    result=d.groupby(['player_id','team_code'],as_index=False).agg(
        player_name=('player_name','last'),innings=('match_id','nunique'),runs=('runs','sum'),
        highest_score=('runs','max'),fifties=('runs',lambda x:int(((x>=50)&(x<100)).sum())),
        centuries=('runs',lambda x:int((x>=100).sum())),sixes=('sixes','sum'),balls=('balls','sum'))
    result['strike_rate']=100*result.runs/result.balls.replace(0,float('nan'))
    return result.drop(columns='balls').sort_values(['runs','highest_score'],ascending=False).reset_index(drop=True)


def bowling_records(bowling: pd.DataFrame, match_ids, team: str | None = None) -> pd.DataFrame:
    d=bowling[bowling.match_id.isin(set(match_ids))].copy()
    if team and team!='All teams':d=d[d.team_code.eq(team)]
    if d.empty:return pd.DataFrame(columns=['player_id','player_name','team_code','matches','wickets','best_match_wickets','four_wicket_hauls','five_wicket_hauls','economy'])
    result=d.groupby(['player_id','team_code'],as_index=False).agg(
        player_name=('player_name','last'),matches=('match_id','nunique'),wickets=('wickets','sum'),
        best_match_wickets=('wickets','max'),
        four_wicket_hauls=('wickets',lambda x:int(((x>=4)&(x<5)).sum())),
        five_wicket_hauls=('wickets',lambda x:int((x>=5).sum())),
        balls=('balls','sum'),runs_conceded=('runs_conceded','sum'))
    result['economy']=6*result.runs_conceded/result.balls.replace(0,float('nan'))
    return result.drop(columns=['balls','runs_conceded']).sort_values(['wickets','economy'],ascending=[False,True]).reset_index(drop=True)


def trophy_table(matches: pd.DataFrame, franchises: list[str]) -> pd.DataFrame:
    finals=matches[matches.match_type.eq('Final') & matches.winner_final_code.notna()].copy()
    rows=[]
    for team in franchises:
        history=playoff_history(matches,team)
        seasons=history[history.champion].season.tolist() if len(history) else []
        rows.append(dict(team_code=team, championships=len(seasons),championship_seasons=', '.join(map(str,seasons)),
                         finals=int(history.finalist.sum()) if len(history) else 0,
                         playoff_seasons=len(history)))
    return pd.DataFrame(rows).sort_values(['championships','finals','team_code'],ascending=[False,False,True]).reset_index(drop=True)


def verify_award_integrity(awards:pd.DataFrame,matches:pd.DataFrame)->dict:
    unknown_ids=set(awards.match_id)-set(matches.match_id)
    repeated=bool(awards.duplicated(['match_id','player_id']).any())
    unresolved=int((awards.identity_status!='verified_unique_match_participant').sum())
    return {'awards':int(len(awards)),'matches_with_award':int(awards.match_id.nunique()),
            'unknown_match_ids':len(unknown_ids),'duplicate_player_awards':repeated,
            'unresolved_identities':unresolved,
            'matches_without_award':int(matches.match_id.nunique()-awards.match_id.nunique())}
