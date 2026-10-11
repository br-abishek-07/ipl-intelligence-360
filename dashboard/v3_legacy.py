"""V3 captaincy: rigorously finals-only, with verified source and IPL ID joins.
The captain file is NOT a full match-by-match captain record.
"""
from pathlib import Path
import pandas as pd
ROOT=Path(__file__).resolve().parents[1]
REGISTRY=ROOT/'data/metadata/verified_finals_captains_2008_2026.csv'

def finals_registry():
    return pd.read_csv(REGISTRY,keep_default_na=False)

def finals_by_team(team=None):
    d=finals_registry()
    return d if team is None else d[d.team_code==team].copy()

def winning_captains(team=None):
    d=finals_by_team(team)
    d=d[d.role_in_final=='Winner']
    return (d.groupby('captain_name',as_index=False).agg(titles=('season_year','count'),years=('season_year',lambda s:', '.join(map(str,sorted(s))))).sort_values(['titles','captain_name'],ascending=[False,True]))

def validate_registry():
    m=pd.read_csv(ROOT/'data/analytics/matches_enriched.csv')
    l=pd.read_csv(ROOT/'data/raw/lineups.csv.gz')
    d=finals_registry()
    assert len(d)==38 and d.groupby('season_year').size().eq(2).all()
    mm=m.set_index('match_id')
    check=0
    for x in d.itertuples():
        match=mm.loc[int(x.match_id)]
        assert match.season_year==x.season_year
        assert x.team_code in [match.team1_code,match.team2_code]
        if x.role_in_final=='Winner':assert match.winner_final_code==x.team_code
        else:assert match.winner_final_code!=x.team_code
        lookup=l[(l.match_id==x.match_id)&(l.team_code==x.team_code)&(l.cricsheet_player_id==x.captain_player_id)]
        assert len(lookup)==1 and lookup.player_name.iloc[0]==x.cricsheet_name
        check+=1
    return {'finals':19,'captain_entries':check,'identity_confirmed':check}
