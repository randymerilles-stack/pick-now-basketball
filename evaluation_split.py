"""Offline explicit-cutoff split planning; never trains or qualifies a model.

Input flags require external evidence. canonical_event_id must already resolve
provider aliases. All observations of a game stay together; straddlers purge.
Cutoffs must be frozen before inspecting outcomes.
"""
from collections import Counter, defaultdict
from datetime import datetime


def timestamp(value):
    if not isinstance(value, str):
        raise ValueError('Timestamp required')
    result = datetime.fromisoformat(value.replace('Z', '+00:00'))
    if result.tzinfo is None:
        raise ValueError('Timezone required')
    return result


def plan_splits(rows, *, validation_start, test_start):
    validation, test = map(timestamp, (validation_start, test_start))
    if validation >= test:
        raise ValueError('Cutoffs must increase')
    groups = defaultdict(list)
    rejected = Counter()
    for row in rows:
        event = row.get('canonical_event_id')
        if not isinstance(event, str) or not event.strip():
            rejected['missing_canonical_identity'] += 1
            continue
        groups[event].append(row)
    blocks = {'development': [], 'validation': [], 'test': []}
    for event, group in sorted(groups.items()):
        # One bad observation invalidates its whole event, not just one side.
        try:
            if any(any(r.get(k) is not True for k in
                       ('identity_verified', 'state_verified', 'odds_verified'))
                   for r in group):
                raise ValueError('unverified_event')
            decisions = [timestamp(r.get('decision_at')) for r in group]
            available = [timestamp(r.get('outcome_available_at')) for r in group]
            if any(d >= a for d, a in zip(decisions, available)):
                raise ValueError('invalid_label_chronology')
            bucket = lambda d: ('development' if d < validation else
                                'validation' if d < test else 'test')
            memberships = {bucket(d) for d in decisions}
            if len(memberships) != 1:
                raise ValueError('event_straddles_cutoff')
            block = memberships.pop()
            boundary = validation if block == 'development' else test
            if block != 'test' and max(available) >= boundary:
                raise ValueError('label_unavailable_at_next_block')
            blocks[block].append(event)
        except (ValueError, TypeError) as exc:
            known = {'unverified_event', 'invalid_label_chronology',
                     'event_straddles_cutoff', 'label_unavailable_at_next_block'}
            rejected[str(exc) if str(exc) in known else 'invalid_timestamp'] += 1
    return {'schema_version': 1, 'event_ids': blocks,
            'event_counts': {k: len(v) for k, v in blocks.items()},
            'rejected': dict(rejected),
            'status': ('split_plan_only' if all(blocks.values()) else 'insufficient_data'),
            'model_trained': False, 'approved_for_picks': False,
            'limitations': ['Flags are preconditions, not verification evidence.',
                           'No power, forecasts, timing selection or efficacy evaluated.']}
