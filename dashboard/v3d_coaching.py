"""Verified, deliberately partial, historical CLT20 and coaching sources."""
from pathlib import Path
import pandas as pd
ROOT=Path(__file__).resolve().parents[1]
M=ROOT/'data/metadata'

def clt20():return pd.read_csv(M/'clt20_champions_2009_2014.csv').fillna('')
def coaching_2026():return pd.read_csv(M/'coaches_2026_source_snapshots.csv')
def coaching_eras():return pd.read_csv(M/'verified_coaching_eras_partial.csv')

def coach_era_stats(team,match_table=None):
    """Only attach seasons whose head-coach designation has been individually sourced."""
    if match_table is None:match_table=pd.read_csv(ROOT/'data/analytics/team_match_summary.csv')
    d=match_table[match_table.team_code==team].copy()
    eras=coaching_eras().query('team_code == @team')
    finals=pd.read_csv(ROOT/'data/metadata/verified_finals_captains_2008_2026.csv')
    rows=[]
    for row in eras.itertuples(index=False):
        part=d[d.season_year.between(row.start_season,row.end_season)].copy()
        decided=part[part.is_decided==True].copy()
        era_titles=finals[(finals.team_code==team)&(finals.season_year.between(row.start_season,row.end_season))&(finals.role_in_final=='Winner')]
        rows.append(dict(team_code=team,coach=row.head_coach,start=row.start_season,end=row.end_season,titles=int(len(era_titles)),
                         played=int(len(part)),decided=int(len(decided)),wins=int(decided.won.sum()),
                         win_rate=(float(decided.won.mean()) if len(decided) else None),source_url=row.source_url))
    return pd.DataFrame(rows)
