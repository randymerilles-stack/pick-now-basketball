"""Count independent research events and enforce chronological separation."""
from collections import Counter, defaultdict
from datetime import datetime
import argparse
import json
from pathlib import Path


def stamp(value):
    if not isinstance(value,str):raise ValueError('Missing timestamp')
    dt=datetime.fromisoformat(value.replace('Z','+00:00'))
    if dt.tzinfo is None:raise ValueError('Timezone required')
    return dt


def audit_dataset(capture_reports, outcome_reports):
    observations=defaultdict(list)
    rows_seen=0
    invalid_rows=0
    for report in capture_reports:
        for capture in report.get('captures',[report]):
            for observation in capture.get('observations',[]):
                rows_seen+=1
                try:
                    decision=stamp(capture.get('received_at'))
                    if not observation.get('fixture_id'):raise ValueError('Missing event')
                    identity=tuple(observation.get(k) for k in ('home','away','league'))
                    if not all(isinstance(x,str) and x for x in identity):raise ValueError('Missing identity')
                    observations[str(observation['fixture_id'])].append((decision,identity,observation))
                except (ValueError,TypeError):invalid_rows+=1
    outcomes=defaultdict(list)
    for report in outcome_reports:
        for joined in report.get('joined',[]):
            if joined.get('status')=='provider_labelled_research_only':
                outcomes[str(joined.get('fixture_id'))].append(joined)
    rows=[];identity_conflicts=0;outcome_conflicts=0;unlabelled=0
    for fixture_id,group in observations.items():
        if len({g[1] for g in group})!=1:
            identity_conflicts+=1;continue
        # Selection depends on observation time only, never on final outcome.
        decision,identity,observation=min(group,key=lambda x:x[0])
        matches=outcomes.get(fixture_id,[])
        if not matches:unlabelled+=1;continue
        if len({r.get('final_score') for r in matches})!=1:
            outcome_conflicts+=1;continue
        try:
            finished=max(stamp(r.get('finished_at')) for r in matches)
            available=max(stamp(r.get('outcome_available_at')) for r in matches)
            if not decision<finished<=available:raise ValueError('Bad chronology')
        except (ValueError,TypeError):
            outcome_conflicts+=1;continue
        rows.append({'fixture_id':fixture_id,'league':identity[2],
                     'decision_at':decision.isoformat(),'finished_at':finished.isoformat(),
                     'outcome_available_at':available.isoformat(),
                     'observation_count':len(group),'training_eligible':False})
    rows.sort(key=lambda r:stamp(r['decision_at']))
    split=max(1,int(len(rows)*0.7))
    test=rows[split:]
    cutoff=stamp(test[0]['decision_at']) if test else None
    train=[r for r in rows[:split] if cutoff is not None and stamp(r['outcome_available_at'])<cutoff]
    return {'observation_rows':rows_seen,'unique_fixture_ids':len(observations),
            'invalid_observations':invalid_rows,'identity_conflicts':identity_conflicts,
            'outcome_conflicts':outcome_conflicts,'unlabelled_fixtures':unlabelled,
            'provider_labelled_independent_fixtures':len(rows),
            'league_counts':dict(Counter(r['league'] for r in rows)),
            'chronological_diagnostic_train':len(train),'chronological_diagnostic_test':len(test),
            'purged_unavailable_training_outcomes':len(rows[:split])-len(train),
            'fixtures':rows,'training_eligible':False,'approved_for_picks':False,
            'blockers':['Score/time features and source semantics are not validated.',
                        'Cross-ID event aliases are not yet independently resolved.',
                        'Counts and a split diagnostic do not establish adequate statistical power.',
                        'No model was trained or accuracy measured.']}


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--capture',type=Path,action='append',required=True)
    parser.add_argument('--outcome',type=Path,action='append',default=[])
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    report=audit_dataset([json.loads(p.read_text()) for p in args.capture],
                         [json.loads(p.read_text()) for p in args.outcome])
    with args.output.open('x',encoding='utf-8') as output:json.dump(report,output,indent=2,allow_nan=False)
    print(json.dumps({k:v for k,v in report.items() if k not in ('fixtures','blockers')}))
