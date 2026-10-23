"""Bounded concurrent prospective capture; no automatic event mapping or picks."""
from concurrent.futures import ThreadPoolExecutor
from datetime import date
from copy import deepcopy
from audit_dual_scoreboard import fetch


def source_urls(day):
    parsed = date.fromisoformat(day)
    compact = parsed.strftime('%Y%m%d')
    return {
        'provider': 'https://moviodds.com/odds?sport=basketball&in_play=1&stats=1',
        'espn_nba': f'https://site.api.espn.com/apis/site/v2/sports/basketball/nba/scoreboard?dates={compact}',
        'espn_nbl': f'https://site.api.espn.com/apis/site/v2/sports/basketball/nbl/scoreboard?dates={compact}',
    }


def project(row):
    # Projections are independently mutable; retain the original capture intact.
    row = deepcopy(row)
    result = {k: v for k, v in row.items() if k != 'response'}
    payload = row.get('response', {})
    if row['name'] == 'provider':
        fields = ('id', 'home', 'away', 'league', 'kickoff_utc', 'score', 'clock',
                  'period', 'stats', 'polled_at', 'group_status', 'quotes', 'sport', 'in_play')
        result['fixtures'] = [{k: m.get(k) for k in fields} for m in payload.get('matches', [])]
        for fixture in result['fixtures']:
            fixture['quotes'] = [q for q in (fixture['quotes'] or []) if str(q.get('group_id')) == '112']
        result['server_time'] = payload.get('server_time')
    else:
        result['events'] = [{k: e.get(k) for k in ('id', 'date', 'name', 'status', 'competitions')}
                            for e in payload.get('events', [])]
        for event in result['events']:
            event['competitions'] = [{k: c.get(k) for k in ('id', 'date', 'status', 'competitors')}
                                     for c in (event['competitions'] or [])]
            for competition in event['competitions']:
                competition['competitors'] = [
                    {'id': c.get('id'), 'homeAway': c.get('homeAway'), 'score': c.get('score'),
                     'team': {'id': c.get('team', {}).get('id'), 'displayName': c.get('team', {}).get('displayName')}}
                    for c in (competition['competitors'] or [])]
    return result


def collect(day, reader=fetch):
    with ThreadPoolExecutor(max_workers=3) as pool:
        sources = list(pool.map(reader, source_urls(day).items()))
    return {'requested_date': day, 'sources': [project(r) for r in sources],
            'identity_mapping_verified': False, 'independently_aligned': False,
            'training_eligible': False, 'approved_for_picks': False,
            'limitation': 'Concurrent request receipts are not atomic source timestamps. Exact fixture mapping, quote verification and state alignment remain required.'}


if __name__ == '__main__':
    import argparse
    import json
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--date', required=True, help='ISO calendar date of scoreboard schedule')
    p.add_argument('--output', required=True)
    args = p.parse_args()
    result = collect(args.date)
    with open(args.output, 'x') as f:
        json.dump(result, f, indent=2, allow_nan=False)
    print(json.dumps({'sources': [{k: r.get(k) for k in ('name', 'received_at', 'error_type')} for r in result['sources']], 'approved_for_picks': False}))
