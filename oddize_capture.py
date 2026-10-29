"""One bounded research-only NBA spread request. No retries or pagination.

Key is read from PICKNOW_ODDIZE_API_KEY, never URL/output. Reject redirects to
avoid forwarding credentials. Captures are not source verification or picks.
"""
from datetime import datetime, timezone
import hashlib
import json
import os
from urllib.error import HTTPError
from urllib.request import Request, HTTPRedirectHandler, build_opener

URL = 'https://oddize.com/api/v1/odds/latest?sport=nba&books=b365&offer_types=s&include_past=true&limit=1'


class NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


def capture():
    result = dict(source='oddize', url=URL, training_eligible=False, approved_for_picks=False)
    key = os.environ.get('PICKNOW_ODDIZE_API_KEY', '').strip()
    if not key:
        return dict(result, status='missing_api_key')
    if '\n' in key or '\r' in key:
        return dict(result, status='invalid_api_key_format')
    result['started_at'] = datetime.now(timezone.utc).isoformat()
    stage = 'request'
    try:
        request = Request(URL, headers={'X-API-Key': key, 'User-Agent': 'PickNowResearch/1.0'})
        with build_opener(NoRedirect()).open(request, timeout=20) as response:
            result['http_status'] = response.status
            if response.status != 200:
                return dict(result, status='unexpected_http_status')
            stage = 'payload_size'
            raw = response.read(3_000_001)
            if len(raw) > 3_000_000:
                return dict(result, status='oversized_payload')
            result['received_at'] = datetime.now(timezone.utc).isoformat()
            result['sha256'] = hashlib.sha256(raw).hexdigest()
            result['quota_headers'] = {k: response.headers.get(k) for k in
                                      ('X-Credits-Cost', 'X-Credits-Remaining', 'X-Cache')}
            stage = 'json_decode'
            payload = json.loads(raw)
            if not isinstance(payload, dict) or not isinstance(payload.get('events'), list):
                return dict(result, status='unsupported_payload')
            # Keep only documented sports fields; never persist error/account blobs.
            events = []
            for event in payload['events']:
                if not isinstance(event, dict) or not isinstance(event.get('odds'), list):
                    return dict(result, status='unsupported_payload')
                projected = {k: event.get(k) for k in ('event_id', 'sport', 'team1', 'team2', 'start_date')}
                projected['odds'] = [{k: price.get(k) for k in
                                      ('book', 'offer_type', 'team', 'line', 'american_odds', 'ts', 'timestamp')}
                                     for price in event['odds'] if isinstance(price, dict)]
                events.append(projected)
            return dict(result, status='captured_research_only', events=events)
    except HTTPError as exc:
        result.update(status='http_error', http_status=exc.code)
        exc.close()
    except Exception as exc:
        result.update(status='capture_error', error_type=type(exc).__name__, error_stage=stage)
    result['received_at'] = datetime.now(timezone.utc).isoformat()
    return result


if __name__ == '__main__':
    import argparse
    from pathlib import Path
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    # Exclusive output prevents accidental replacement of earlier evidence.
    with args.output.open('x') as output:
        report = capture()
        json.dump(report, output, indent=2, allow_nan=False)
    print(json.dumps({k: report.get(k) for k in ('status', 'http_status', 'approved_for_picks')}))
