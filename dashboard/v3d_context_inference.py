"""Portable numeric inference for experimental V3-D team/venue chase model.
No pickle or scikit-learn is required at dashboard runtime.
Not a qualified production predictor.
"""
from pathlib import Path
from functools import lru_cache
import json
import math
from dashboard.predict import chase_features
ROOT=Path(__file__).resolve().parents[1]

@lru_cache(maxsize=3)
def context_model(balls):
    if balls not in (60,90,108):raise ValueError('Unsupported context checkpoint')
    obj=json.loads((ROOT/'data/research'/f'context_chase_after_{balls}_balls.json').read_text(encoding='utf-8'))
    if obj.get('status')!='RESEARCH_NOT_DEPLOYED':raise ValueError('Invalid model research designation')
    return obj

def context_probability(balls,score,target,wickets,batting_team,bowling_team,venue):
    model=context_model(balls)
    features=chase_features(int(score),int(target),int(wickets),balls)
    values=[(features[f]-mu)/sd for f,mu,sd in zip(model['numeric_features'],model['means'],model['scales'])]
    for choice,cats in zip([batting_team,bowling_team,venue],model['category_values']):
        values.extend(float(str(choice)==cat) for cat in cats)
    if len(values)!=len(model['coefficients']):raise ValueError('Model coefficient count mismatch')
    logit=float(model['intercept']+sum(x*c for x,c in zip(values,model['coefficients'])))
    return 1/(1+math.exp(-max(-700,min(700,logit))))
