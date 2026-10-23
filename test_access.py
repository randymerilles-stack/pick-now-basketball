import hashlib
from http.server import ThreadingHTTPServer
import http.client
import os
import threading
import unittest
from unittest.mock import patch
from urllib.parse import urlencode
import access
from app import Handler

TEST_PASSWORD='test-password-only-not-a-live-secret'
SALT='11'*16
HASH=SALT+'$'+hashlib.pbkdf2_hmac('sha256',TEST_PASSWORD.encode(),bytes.fromhex(SALT),200_000).hex()

class AccessTests(unittest.TestCase):
    def setUp(self):
        self.env=patch.dict(os.environ,{'PICKNOW_PASSWORD_HASH':HASH,'PICKNOW_ORIGIN':'https://test.invalid',
                                      'PICKNOW_DATABASE_URL':''})
        self.env.start()
        with access.LOCK:access.SESSIONS.clear();access.ATTEMPTS.clear()
        self.server=ThreadingHTTPServer(('127.0.0.1',0),Handler)
        self.thread=threading.Thread(target=self.server.serve_forever,daemon=True);self.thread.start()
    def tearDown(self):
        self.server.shutdown();self.server.server_close();self.env.stop()
    def request(self,path='/',method='GET',body=None,headers=None):
        c=http.client.HTTPConnection('127.0.0.1',self.server.server_port)
        c.request(method,path,body,headers or {})
        r=c.getresponse();code=r.status;heads=dict(r.getheaders());data=r.read();c.close()
        return code,heads,data
    def login(self,password=TEST_PASSWORD,origin='https://test.invalid'):
        return self.request('/login','POST',urlencode({'password':password}),
            {'Origin':origin,'Content-Type':'application/x-www-form-urlencoded'})
    def test_anonymous_home_api_and_head_cannot_read_data(self):
        self.assertEqual(self.request('/')[0],303)
        self.assertEqual(self.request('/api/pick-now')[0],401)
        self.assertEqual(self.request('/api/pick-now','HEAD')[0],401)
        self.assertEqual(self.request('/health')[2],b'{"status":"ok"}')
    def test_browser_login_policy_preserves_origin_and_rejects_missing_origin(self):
        code,heads,body=self.request('/login')
        self.assertEqual(code,200)
        self.assertEqual(heads['Referrer-Policy'],'same-origin')
        self.assertEqual(heads['Cache-Control'],'no-store')
        self.assertIn(b'action="/login"',body)
        for origin in ('null',''):
            self.assertEqual(self.login(origin=origin)[0],403)
        self.assertEqual(self.request('/login','POST','password=test',
            {'Content-Type':'application/x-www-form-urlencoded'})[0],403)
    def test_login_throttle_and_retry_after(self):
        with patch('access.time.time',return_value=100):
            with access.LOCK:access.ATTEMPTS.extend([100]*20)
            code,heads,_=self.login()
            self.assertEqual(code,429)
            self.assertEqual(heads['Retry-After'],'60')
        with patch('access.time.time',return_value=161):
            self.assertEqual(self.login()[0],303)
    def test_owner_session_secure_cookie_and_logout(self):
        code,heads,_=self.login();self.assertEqual(code,303)
        cookie=heads['Set-Cookie']
        for attribute in ['Secure','HttpOnly','SameSite=Strict','Path=/']:self.assertIn(attribute,cookie)
        auth={'Cookie':cookie.split(';')[0]}
        self.assertEqual(self.request('/',headers=auth)[0],200)
        auth['Origin']='https://test.invalid'
        self.assertEqual(self.request('/logout','POST',headers=auth)[0],303)
        self.assertEqual(self.request('/',headers=auth)[0],303)
    def test_bad_password_forged_cookie_and_wrong_origin_rejected(self):
        self.assertEqual(self.login('incorrect')[0],401)
        self.assertEqual(self.login(origin='https://attacker.invalid')[0],403)
        self.assertEqual(self.request('/',headers={'Cookie':access.COOKIE+'=forged'})[0],303)
    def test_unconfigured_access_fails_closed(self):
        with patch.dict(os.environ,{'PICKNOW_PASSWORD_HASH':''}):
            self.assertEqual(self.request('/')[0],503)
            self.assertEqual(self.request('/api/pick-now')[0],503)
    def test_expired_session_cannot_authenticate(self):
        token=access.new_session()
        with access.LOCK:access.SESSIONS[hashlib.sha256(token.encode()).digest()]=0
        self.assertFalse(access.authenticated(access.COOKIE+'='+token))
    def test_remembered_session_survives_next_day_but_expires_after_30_days(self):
        with patch('access.time.time',return_value=1000):
            token=access.new_session()
        header=access.COOKIE+'='+token
        self.assertIn('Max-Age=2592000',access.session_cookie(token))
        with patch('access.time.time',return_value=1000+24*60*60):
            self.assertTrue(access.authenticated(header))
        with patch('access.time.time',return_value=1000+30*24*60*60):
            self.assertFalse(access.authenticated(header))

if __name__=='__main__':unittest.main()

