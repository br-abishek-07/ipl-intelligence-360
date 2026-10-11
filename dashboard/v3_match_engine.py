"""IPL replay and rivalry metrics computed solely from recorded deliveries.
Super overs are segregated; non-legal deliveries do not add balls to innings.
All momentum summaries are descriptive, not predictive win probabilities.
"""
from pathlib import Path
import pandas as pd
ROOT=Path(__file__).resolve().parents[1]

def match_index():
    d=pd.read_csv(ROOT/'data/analytics/matches_enriched.csv')
    d['match_date']=pd.to_datetime(d['match_date'],errors='coerce')
    return d.sort_values(['match_date','match_id'],ascending=[False,False])

def match_deliveries(match_id,include_super_over=False):
    d=pd.read_csv(ROOT/'data/raw/deliveries.csv.gz')
    d=d[d.match_id==int(match_id)].copy()
    if not include_super_over:d=d[~d.super_over.fillna(False).astype(bool)].copy()
    # Source CSV carries original delivery order; mergesort is stable for extras.
    d=d.sort_values(['inning','over_index','ball_in_over'],kind='mergesort').reset_index(drop=True)
    d['runs_at_ball']=d.total_runs.astype(int)
    d['wickets_at_ball']=d.wickets_count.fillna(0).astype(int)
    d['legal_delivery']=d.legal_ball.fillna(False).astype(bool)
    d['legal_balls_completed']=d.groupby('inning').legal_delivery.cumsum()
    d['cumulative_runs']=d.groupby('inning').runs_at_ball.cumsum()
    d['cumulative_wickets']=d.groupby('inning').wickets_at_ball.cumsum()
    d['delivery_number']=d.groupby('inning').cumcount()+1
    d['over_elapsed']=d['legal_balls_completed']/6.0
    return d

def innings_summary(d):
    if d.empty:return pd.DataFrame()
    return d.groupby(['inning','batting_team_code'],as_index=False).agg(
        runs=('runs_at_ball','sum'),wickets=('wickets_at_ball','sum'),legal_balls=('legal_delivery','sum'),
        deliveries=('delivery_number','count'),fours=('batsman_runs',lambda s:int((s==4).sum())),
        sixes=('batsman_runs',lambda s:int((s==6).sum()))
    )

def over_summary(d):
    if d.empty:return pd.DataFrame()
    return d.groupby(['inning','batting_team_code','over_index'],as_index=False).agg(
        runs=('runs_at_ball','sum'),wickets=('wickets_at_ball','sum'),legal_balls=('legal_delivery','sum')).assign(
        over_number=lambda s:s.over_index+1)

def wicket_events(d):
    if d.empty:return pd.DataFrame()
    w=d[d.wickets_at_ball>0].copy()
    return w[['inning','batting_team_code','over_index','ball_in_over','batter','bowler','cumulative_runs','cumulative_wickets','over_elapsed','wickets_at_ball']]

def runs_between_wickets(d):
    """Segment scoring between wickets, NOT audited batter-pair partnerships."""
    if d.empty:return pd.DataFrame()
    rows=[]
    for innings,group in d.groupby('inning',sort=True):
        segment_runs=0;segment_balls=0;seq=1
        for r in group.itertuples():
            segment_runs+=int(r.runs_at_ball)
            segment_balls+=int(r.legal_delivery)
            if r.wickets_at_ball:
                rows.append(dict(inning=int(innings),segment=f'Wicket {seq}',runs_between_wickets=segment_runs,
                    legal_balls=segment_balls,ends_with_wicket=True))
                segment_runs=0;segment_balls=0;seq+=int(r.wickets_at_ball)
        if segment_balls or segment_runs:
            rows.append(dict(inning=int(innings),segment=f'After wicket {seq-1}' if seq>1 else 'Opening stand',
                runs_between_wickets=segment_runs,legal_balls=segment_balls,ends_with_wicket=False))
    return pd.DataFrame(rows)

def descriptive_turning_points(d):
    """Observed high-scoring/wicket overs, not estimated causal win-probability changes."""
    o=over_summary(d)
    if o.empty:return []
    notes=[]
    for inning,sub in o.groupby('inning'):
        highest=sub.sort_values(['runs','wickets','over_number'],ascending=[False,True,True]).iloc[0]
        notes.append(f'Innings {inning}: over {int(highest.over_number)} produced {int(highest.runs)} runs, the highest-scoring over recorded for this innings.')
        w=sub[sub.wickets>0].sort_values(['wickets','runs','over_number'],ascending=[False,True,True])
        if len(w):
            top=w.iloc[0]
            notes.append(f'Innings {inning}: over {int(top.over_number)} had {int(top.wickets)} wicket(s) for {int(top.runs)} runs.')
    return notes

def rivalry_table(team_a,team_b,years=None):
    df=pd.read_csv(ROOT/'data/analytics/matches_enriched.csv')
    df=df[((df.team1_code==team_a)&(df.team2_code==team_b))|((df.team1_code==team_b)&(df.team2_code==team_a))].copy()
    if years is not None:df=df[df.season_year.between(int(years[0]),int(years[1]))]
    df=df.sort_values(['season_year','match_date','match_id'])
    return df

def rivalry_metrics(df,a,b):
    decisive=df[df.winner_final_code.isin([a,b])].copy()
    return dict(matches=len(df),decided=len(decisive),wins_a=int((decisive.winner_final_code==a).sum()),
        wins_b=int((decisive.winner_final_code==b).sum()),unresolved=int(len(df)-len(decisive)))
