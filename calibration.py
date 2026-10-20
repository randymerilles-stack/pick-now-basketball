"""Offline, fixture-level odds calibration experiment. Never enables app picks."""
import json
import math
import random
from collections import Counter
from datetime import datetime
from pathlib import Path

MIN_TRAIN, MIN_TEST = 200, 100

def stamp(value):
    return datetime.fromisoformat(value.replace('Z','+00:00'))

def split(rows):
    if len({r['fixture_id'] for r in rows}) != len(rows):
        raise ValueError('Multiple observations from the same fixture are not independent')
    known_ids=set()
    for r in rows:
        family=set(r.get('fixture_family') or [r['fixture_id']])
        if known_ids.intersection(family):
            raise ValueError('Overlapping fixture aliases')
        known_ids.update(family)
        if not stamp(r['decision_at']) < stamp(r['finished_at']):
            raise ValueError('Decision must precede outcome')
    ordered = sorted(rows, key=lambda r: stamp(r['decision_at']))
    if not ordered:
        return [], []
    test = ordered[max(1, int(len(ordered)*.7)):]
    if not test:
        return [], []
    cutoff = stamp(test[0]['decision_at'])
    train = [r for r in ordered[:len(ordered)-len(test)]
             if stamp(r.get('outcome_available_at',r['finished_at'])) < cutoff]
    return train, test

def sigmoid(z):
    return 1 / (1 + math.exp(-max(-30,min(30,z))))

def fit_offset(train):
    offset=0.
    for _ in range(30):
        gradient,curvature=-offset,1.
        for r in train:
            p=r['market_home_probability']
            pred=sigmoid(math.log(p/(1-p))+offset)
            gradient += r['home_covered']-pred
            curvature += pred*(1-pred)
        step=gradient/curvature;offset+=step
        if abs(step)<1e-8:break
    return offset

def audit(rows):
    train,test=split(rows)
    report={'approach':'Market probability calibration with regularized logistic offset',
            'independent_fixtures':len(rows),'training_fixtures':len(train),
            'heldout_fixtures':len(test),'minimum_train':MIN_TRAIN,'minimum_test':MIN_TEST,
            'split':'Chronological by decision time; training outcome-record timestamps must predate first evaluation decision.',
            'status':'insufficient_sample','trained':False,'approved_for_picks':False}
    if len(train)<MIN_TRAIN or len(test)<MIN_TEST:return report
    offset=fit_offset(train)
    raw=[r['market_home_probability'] for r in test]
    pred=[sigmoid(math.log(p/(1-p))+offset) for p in raw]
    outcomes=[r['home_covered'] for r in test]
    def brier(ps):return sum((p-y)**2 for p,y in zip(ps,outcomes))/len(outcomes)
    def logloss(ps):
        return -sum(y*math.log(max(1e-9,p))+(1-y)*math.log(max(1e-9,1-p)) for p,y in zip(ps,outcomes))/len(outcomes)
    gains=[(p-y)**2-(q-y)**2 for p,q,y in zip(raw,pred,outcomes)]
    rng=random.Random(42)
    draws=sorted(sum(rng.choices(gains,k=len(gains)))/len(gains) for _ in range(1000))
    leagues=Counter(r['league'] for r in test)
    report.update(status='research_only_requires_further_validation',trained=True,
                  offset=offset,market_brier=brier(raw),model_brier=brier(pred),
                  market_log_loss=logloss(raw),model_log_loss=logloss(pred),
                  brier_improvement_95pct_fixture_bootstrap=[draws[24],draws[974]],
                  heldout_league_counts=dict(leagues),
                  beats_market_brier=brier(pred)<brier(raw),
                  positive_edge_lower_confidence_bound=draws[24]>0,
                  leagues_with_at_least_50_heldout_games=[k for k,v in leagues.items() if v>=50],
                  calibration_gap=abs(sum(pred)/len(pred)-sum(outcomes)/len(outcomes)))
    # A single split and pooled metric cannot approve a live betting model.
    # League-level evaluation and uncertainty/robustness checks remain required.
    if not report['positive_edge_lower_confidence_bound']:
        report['status']='no_reliable_improvement_over_market'
    return report

if __name__=='__main__':
    root=Path(__file__).resolve().parent
    report=audit(json.loads((root/'calibration_sample.json').read_text()))
    (root/'calibration_report.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report,indent=2))
