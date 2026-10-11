"""Load generated tables; Streamlit caching is supplied by the view layer."""
from pathlib import Path
import json
import pandas as pd
ROOT=Path(__file__).resolve().parents[1]
D=ROOT/'data/analytics'
FILES={
'matches':'matches_enriched.csv', 'team_matches':'team_match_summary.csv',
'innings':'innings_summary.csv','season':'league_season_summary.csv',
'phase':'team_phase_season.csv','bat':'batting_player_season.csv','bowl':'bowling_player_season.csv',
'bat_match':'batting_player_match.csv','bowl_match':'bowling_player_match.csv',
'phase_match':'team_phase_match.csv'
}
def load(name):
    if name not in FILES:raise ValueError(f'Unknown table: {name}')
    return pd.read_csv(D/FILES[name],low_memory=False)
def audit():return json.loads((ROOT/'reports/data_quality_audit.json').read_text())
