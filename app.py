"""Standalone Pick Now: fail-closed live-feed inspection; picks remain locked."""
import json
import os
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.request import Request, urlopen
from validation import inspect_feed
from urllib.parse import parse_qs
import access

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
    try:
        report = json.loads(report_path.read_text())
        if not isinstance(report, dict):
            raise ValueError('Invalid model report')
        result['model_report'] = report
    except (OSError, ValueError):
        result['model_report'] = {'status': 'unavailable', 'reason': 'Model audit report unavailable; picks remain disabled.'}
    experiment = result['model_report'].get('calibration_experiment')
    if isinstance(experiment, dict) and experiment.get('trained') is True:
        result['model_status'] = 'tested_not_approved'
    return result

class Handler(BaseHTTPRequestHandler):
    def reply(self, code, body=b'', mime='text/plain; charset=utf-8', extra=None, head=False):
        self.send_response(code)
        self.send_header('Content-Type', mime)
        self.send_header('Content-Length', str(len(body)))
        self.send_header('Cache-Control', 'no-store')
        self.send_header('X-Content-Type-Options', 'nosniff')
        self.send_header('X-Frame-Options', 'DENY')
        self.send_header('Referrer-Policy', 'same-origin')
        self.send_header('Content-Security-Policy', "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'; base-uri 'none'; frame-ancestors 'none'; form-action 'self'")
        for key,value in (extra or {}).items():self.send_header(key,value)
        self.end_headers()
        if not head:self.wfile.write(body)

    def login_page(self, message='', code=200, head=False):
        self.reply(code, access.LOGIN.replace('MESSAGE',message).encode(), 'text/html; charset=utf-8', head=head)

    def route(self, head=False):
        path=self.path.split('?',1)[0]
        if path=='/health':
            self.reply(200,b'{"status":"ok"}','application/json',head=head)
            return
        if not access.configured():
            self.reply(503,b'Private access is not configured. Public data access is disabled.',head=head)
            return
        if path=='/login':
            self.login_page(head=head)
            return
        if not access.authenticated(self.headers.get('Cookie')):
            if path.startswith('/api/'):
                self.reply(401,b'{"error":"authentication_required"}','application/json',head=head)
            else:self.reply(303,extra={'Location':'/login'},head=head)
            return
        if path=='/':
            self.reply(200,(ROOT/'index.html').read_bytes(),'text/html; charset=utf-8',head=head)
        elif path=='/api/pick-now':
            if head:self.reply(200,head=True)
            else:self.reply(200,json.dumps(check(),allow_nan=False).encode(),'application/json')
        else:self.reply(404,b'Not found',head=head)

    def do_HEAD(self):self.route(head=True)
    def do_GET(self):self.route()

    def do_POST(self):
        origin=os.environ.get('PICKNOW_ORIGIN','https://pick-now-basketball.onrender.com')
        if self.headers.get('Origin')!=origin:
            self.reply(403,b'Invalid request origin')
            return
        path=self.path.split('?',1)[0]
        if path=='/logout':
            access.logout(self.headers.get('Cookie'))
            self.reply(303,extra={'Location':'/login','Set-Cookie':access.clear_cookie()})
            return
        if path!='/login':self.reply(404,b'Not found');return
        if not access.configured():self.reply(503,b'Private access unavailable');return
        try:size=int(self.headers.get('Content-Length','0'))
        except ValueError:self.reply(400,b'Invalid request');return
        if not 0<size<=2048:self.reply(400,b'Invalid request');return
        if self.headers.get('Content-Type','').split(';')[0]!='application/x-www-form-urlencoded':
            self.reply(415,b'Unsupported form type');return
        if not access.allow_attempt():
            self.reply(429,b'Too many attempts. Try again in one minute.',extra={'Retry-After':'60'})
            return
        try:
            fields=parse_qs(self.rfile.read(size).decode('utf-8'),max_num_fields=4)
            password=fields.get('password',[''])[0]
        except (ValueError,UnicodeDecodeError):self.reply(400,b'Invalid request');return
        if not access.verify_password(password):self.login_page('Incorrect password.',401);return
        self.reply(303,extra={'Location':'/','Set-Cookie':access.session_cookie(access.new_session())})

if __name__ == '__main__':
    ThreadingHTTPServer(('0.0.0.0', int(os.environ.get('PORT', '5000'))), Handler).serve_forever()
