"""Read-only next acquisition targets, never a claim a game is live."""
from datetime import datetime


def aware(value):
    dt = datetime.fromisoformat(value.replace('Z', '+00:00'))
    if dt.tzinfo is None:
        raise ValueError('Timezone required')
    return dt


def plan(sources, now):
    now = aware(now)
    targets = []
    rejected = 0
    for source in sources:
        if source.get('error_type'):
            continue
        for event in source.get('events', []):
            state = event.get('status', {}).get('type', {}).get('state')
            try:
                start = aware(event['date'])
            except (ValueError, TypeError, KeyError, AttributeError):
                rejected += 1
                continue
            if state == 'in' or (state == 'pre' and start >= now):
                targets.append({'source': source['name'], 'event_id': event['id'],
                                'scheduled_start': start.isoformat(), 'observed_state': state,
                                'name': event.get('name')})
    targets.sort(key=lambda x: aware(x['scheduled_start']))
    return {'as_of': now.isoformat(), 'targets': targets, 'invalid_dates': rejected,
            'training_eligible': False, 'approved_for_picks': False,
            'limitation': 'Schedule targets only; recheck live status, source calendar date and provider fixture coverage at capture time.'}
