"""Portable research-only V3E player-context logistic inference. No pickle or sklearn runtime dependency."""
from pathlib import Path
from functools import lru_cache
import json,math
import pandas as pd
from dashboard.predict import chase_features
ROOT=Path(__file__).resolve().parents[1]

@lru_cache(maxsize=3)
def player_model(balls):
    if balls not in (60,90,108):raise ValueError('Supported checkpoints: 60, 90, 108 balls')
    model=json.loads((ROOT/'data/research'/f'player_chase_after_{balls}_balls.json').read_text())
    if model['status']!='RESEARCH_NOT_DEPLOYED' or model['fit_end_season']!=2024:
        raise ValueError('Invalid research model')
    return model

@lru_cache(maxsize=1)
def prior_registry_2026():
    d=pd.read_csv(ROOT/'data/research/player_priors_asof_2026.csv').dropna(subset=['player_id'])
    result={}
    for r in d.itertuples(index=False):result[(str(r.player_id),str(r.role))]=(int(r.past_runs),int(r.past_balls))
    return result

def player_input_features(last_batter_id,non_striker_id,last_bowler_id):
    registry=prior_registry_2026()
    feats={}
    for pid,label in [(last_batter_id,'last_batter'),(non_striker_id,'last_non_striker')]:
        runs,balls=registry.get((str(pid),'batter'),(0,0))
        feats[label+'_prior_sr']=(runs*100+130*100)/(balls+100)
        feats[label+'_prior_balls_log']=math.log1p(balls)
    runs,balls=registry.get((str(last_bowler_id),'bowler'),(0,0))
    feats['last_bowler_prior_runs_per_over']=(runs*6+8.7*120)/(balls+120)
    feats['last_bowler_prior_overs_log']=math.log1p(balls/6)
    return feats

def player_probability(balls,score,target,wickets,batting,bowling,venue,last_batter_id,non_striker_id,last_bowler_id):
    m=player_model(balls)
    values=chase_features(int(score),int(target),int(wickets),int(balls))
    values.update(player_input_features(last_batter_id,non_striker_id,last_bowler_id))
    v=[(float(values[k])-float(mu))/float(sd) for k,mu,sd in zip(m['numeric_features'],m['means'],m['scales'])]
    for choice,cats in zip([batting,bowling,venue],m['category_values']):
        v.extend(float(str(choice)==cat) for cat in cats)
    if len(v)!=len(m['coefficients']):raise ValueError('V3E predictor coefficient count mismatch')
    z=m['intercept']+sum(float(a)*float(b) for a,b in zip(v,m['coefficients']))
    return 1/(1+math.exp(-max(-700,min(700,z))))
