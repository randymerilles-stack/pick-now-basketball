"""Bounded read-only alias evidence for the latest schema-v3 capture IDs."""
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
import hashlib
import json
from urllib.request import Request, urlopen
from event_aliases import provider_aliases

IDS = ('202562243', '202560895', '203169631', '203192934')


def fetch(fixture_id):
    url = 'https://moviodds.com/closing?fi=' + fixture_id
    row = {'requested_id':fixture_id, 'url':url}
    try:
        with urlopen(Request(url, headers={'User-Agent':'PickNowAliasAudit/1.0'}),
                     timeout=20) as response:
            if response.status != 200:
                raise ValueError('Unexpected HTTP status')
            raw = response.read(3_000_001)
            if len(raw) > 3_000_000:
                raise ValueError('Oversized response')
        row['received_at'] = datetime.now(timezone.utc).isoformat()
        row['source_sha256'] = hashlib.sha256(raw).hexdigest()
        row['response'] = json.loads(raw)
        row['declared_aliases'] = provider_aliases(fixture_id, row['response'])
        row['status'] = 'provider_declaration_only' if row['declared_aliases'] else 'unresolved'
    except Exception as exc:
        row['received_at'] = datetime.now(timezone.utc).isoformat()
        row['status'] = 'unresolved'
        row['error_type'] = type(exc).__name__
    return row


if __name__ == '__main__':
    import argparse
    from pathlib import Path
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    with ThreadPoolExecutor(max_workers=4) as pool:
        records = list(pool.map(fetch, IDS))
    report = {'records':records, 'independently_verified':False,
              'training_eligible':False, 'approved_for_picks':False,
              'scope':'Four recent capture IDs only; not a full-dataset alias audit.'}
    with args.output.open('x', encoding='utf-8') as output:
        json.dump(report, output, indent=2, allow_nan=False)
    print(json.dumps([{'id':r['requested_id'], 'status':r['status'],
                       'aliases':r.get('declared_aliases')} for r in records]))
