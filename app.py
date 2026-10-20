"""Standalone Pick Now: fail-closed live-feed inspection; picks remain locked."""
import json
import os
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.request import Request, urlopen
from validation import inspect_feed

SOURCE = 'https://moviodds.com/odds?sport=basketball&in_play=1'
ROOT = Path(__file__).resolve().parent

def now():
    return datetime.now(timezone.utc)


def check(fetch=None):
    result = {'checked_at': now().isoformat(), 'source': 'MoviOdds / bet365 reference feed',
              'source_url': SOURCE, 'status': 'no_bet', 'recommendation': 'NO BET',
              'model_status': 'not_validated', 'picks': [], 'markets': [],
              'verified_market_count': 0, 'feed_status': 'unavailable',
              'reason': 'Picks locked: verified Full Game Handicap odds and a tested probability model are required.'}
    try:
        if fetch is None:
            def fetch():
                req = Request(SOURCE, headers={'User-Agent': 'PickNowValidation/0.2'})
                with urlopen(req, timeout=10) as response:
                    if response.status != 200:
                        raise ValueError('Unexpected HTTP status')
                    raw = response.read(3_000_001)
                    if len(raw) > 3_000_000:
                        raise ValueError('Oversized feed')
                    return json.loads(raw)
        result.update(inspect_feed(fetch()))
        result['feed_status'] = 'reachable_schema_checked'
    except Exception as exc:
        result['validation_status'] = 'failed'
        result['error_type'] = type(exc).__name__
        result['http_status'] = getattr(exc, 'code', None)
    report_path = ROOT / 'model_report.json'
    result['model_report'] = json.loads(report_path.read_text()) if report_path.exists() else {'status': 'audit_in_progress'}
    if result['model_report'].get('calibration_experiment', {}).get('trained'):
        result['model_status'] = 'tested_not_approved'
    return result

class Handler(BaseHTTPRequestHandler):
    def do_HEAD(self):
        if self.path.split('?', 1)[0] not in ('/', '/health'):
            self.send_error(404)
            return
        self.send_response(200)
        self.send_header('Cache-Control', 'no-store')
        self.end_headers()

    def do_GET(self):
        path = self.path.split('?', 1)[0]
        if path == '/':
            body, mime = (ROOT / 'index.html').read_bytes(), 'text/html; charset=utf-8'
        elif path == '/health':
            body, mime = b'{"status":"ok","app":"pick-now","picks_enabled":false}', 'application/json'
        elif path == '/api/pick-now':
            body, mime = json.dumps(check(), allow_nan=False).encode(), 'application/json'
        else:
            self.send_error(404)
            return
        self.send_response(200)
        self.send_header('Content-Type', mime)
        self.send_header('Content-Length', str(len(body)))
        self.send_header('Cache-Control', 'no-store')
        self.send_header('X-Content-Type-Options', 'nosniff')
        self.end_headers()
        self.wfile.write(body)

if __name__ == '__main__':
    ThreadingHTTPServer(('0.0.0.0', int(os.environ.get('PORT', '5000'))), Handler).serve_forever()
