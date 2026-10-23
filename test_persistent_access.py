"""HTTP persistence routing with real disk storage; Postgres transport separate."""
import hashlib
import os
from pathlib import Path
import tempfile
from unittest.mock import patch
from durable_sessions import DurableSessions
import test_access
import access


class PersistentAccessTests(test_access.AccessTests):
    def setUp(self):
        super().setUp()
        self.temp=tempfile.TemporaryDirectory()
        self.store=DurableSessions(Path(self.temp.name)/'sessions.sqlite')
        self.storage_patch=patch('access.persistent_store',return_value=self.store)
        self.storage_patch.start()

    def tearDown(self):
        self.storage_patch.stop()
        self.temp.cleanup()
        super().tearDown()

    def test_expired_session_cannot_authenticate(self):
        with patch('access.time.time',return_value=1000):token=access.new_session()
        with patch('access.time.time',return_value=1000+access.TTL):
            self.assertFalse(access.authenticated(access.COOKIE+'='+token))

    def test_persistent_token_survives_memory_loss_and_password_change_rejects_it(self):
        code,heads,_=self.login()
        self.assertEqual(code,303)
        auth={'Cookie':heads['Set-Cookie'].split(';')[0]}
        with access.LOCK:access.SESSIONS.clear()
        self.assertEqual(self.request('/',headers=auth)[0],200)
        salt='33'*16
        changed=salt+'$'+hashlib.pbkdf2_hmac('sha256',b'new-test-password',bytes.fromhex(salt),200_000).hex()
        with patch.dict(os.environ,{'PICKNOW_PASSWORD_HASH':changed}):
            self.assertEqual(self.request('/',headers=auth)[0],303)

    def test_unavailable_store_denies_home_api_login_and_logout_without_cookie(self):
        _,heads,_=self.login()
        auth={'Cookie':heads['Set-Cookie'].split(';')[0],'Origin':'https://test.invalid'}
        with patch('access.persistent_store',side_effect=access.SessionStoreUnavailable('unavailable')):
            for path in ('/','/api/pick-now'):
                code,headers,body=self.request(path,headers=auth)
                self.assertEqual(code,503)
                self.assertNotIn('Set-Cookie',headers)
                self.assertNotIn(b'PAPER ONLY',body)
            self.assertEqual(self.request('/health')[0],200)
            self.assertEqual(self.login()[0],503)
            code,headers,_=self.request('/logout','POST',headers=auth)
            self.assertEqual(code,503)
            self.assertNotIn('Set-Cookie',headers)

    def test_configured_database_never_silently_uses_memory(self):
        self.storage_patch.stop()
        try:
            with patch.dict(os.environ,{'PICKNOW_DATABASE_URL':'synthetic-invalid-dsn'}):
                with self.assertRaises(access.SessionStoreUnavailable):access.new_session()
        finally:self.storage_patch.start()
