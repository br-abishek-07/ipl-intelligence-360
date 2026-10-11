"""Portable, version-independent, exact inference for qualified Phase 3D models.

Models were exported *unchanged* from their fitted sklearn pipelines and checked
against the trusted originals. No sklearn object deserialization is performed when
users interact with Streamlit; this works with Python 3.14 as well as 3.11–3.13.
"""
from pathlib import Path
from functools import lru_cache
import json
import math

ROOT=Path(__file__).resolve().parents[1]


def chase_features(score,target,wickets,balls):
    left=120-balls;needed=max(0,target-score);current_rr=6*score/max(1,balls);rrr=6*needed/max(1,left)
    return dict(target_runs=target,runs_before_ball=score,wickets_before_ball=wickets,legal_balls_before=balls,
      runs_needed=needed,balls_left=left,wickets_left=10-wickets,run_rate=current_rr,required_rr=rrr,
      required_minus_current_rr=rrr-current_rr,target_per_over=(target-1)/20,
      required_run_fraction=needed/max(1,target))


def total_features(score,wickets):
    balls=60;left=120-balls;rr=6*score/balls;to_180=max(0,180-score)
    return dict(runs_before_ball=score,wickets_before_ball=wickets,legal_balls_before=balls,balls_left=left,
      current_rr=rr,projected_total=score+rr*left/6,runs_to_180=to_180,
      needed_rate_180=6*to_180/max(left,1))


@lru_cache(maxsize=1)
def _qualified():
    return frozenset(json.loads((ROOT/'model_reports/qualified_model_names.json').read_text(encoding='utf-8')))


@lru_cache(maxsize=4)
def _load_model(name):
    if name not in _qualified():
        raise ValueError('Only historically qualified candidate models may be shown.')
    path=ROOT/'models_portable'/f'{name}.json'
    if not path.is_file():
        raise FileNotFoundError(f'Portable model {name} is missing. Restore models_portable from the ZIP.')
    doc=json.loads(path.read_text(encoding='utf-8'))
    if doc.get('name')!=name or doc.get('format_version')!=1:
        raise ValueError(f'Invalid portable model identity/format: {name}')
    return doc


def _sigmoid(x):
    if x >= 0:
        return 1.0/(1.0+math.exp(-x))
    t=math.exp(x)
    return t/(1.0+t)


def predict(name,features):
    model=_load_model(name)
    values=[]
    for feature,median in zip(model['features'],model['impute_medians']):
        value=features.get(feature)
        try:
            value=float(value) if value is not None else float('nan')
        except (ValueError,TypeError):
            value=float('nan')
        values.append(value if math.isfinite(value) else median)
    if model['type']=='logistic_regression':
        xs=[(value-mu)/scale for value,mu,scale in zip(values,model['means'],model['scales'])]
        raw=model['intercept']+sum(v*w for v,w in zip(xs,model['coefficients']))
    elif model['type']=='hist_gradient_boosting':
        raw=model['baseline_raw']
        for tree in model['trees']:
            index=0
            while not tree[index]['leaf']:
                node=tree[index]
                value=values[node['feature']]
                go_left=(node['missing_left'] if math.isnan(value) else value<=node['threshold'])
                index=node['left'] if go_left else node['right']
            raw+=tree[index]['value']
    else:
        raise ValueError('Unsupported portable prediction algorithm: '+str(model['type']))
    return _sigmoid(raw)
