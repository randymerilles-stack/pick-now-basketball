"""Opt-in real Postgres acceptance tests. Only use an isolated test branch."""
import json
import os
from pathlib import Path
import subprocess
import sys
import time
import unittest


@unittest.skipUnless(os.environ.get('PICKNOW_TEST_DATABASE_URL'),
                     'Isolated Postgres test database not configured')
class PostgresSessionTests(unittest.TestCase):
    def test_restart_logout_expiry_credentials_and_tampering(self):
        from pg_sessions import PostgresSessions, TTL
        dsn = os.environ['PICKNOW_TEST_DATABASE_URL']
        store = PostgresSessions(dsn)
        store.migrate()
        now = time.time()
        token = store.create('synthetic-test-generation', now)
        self.assertTrue(store.authenticated(token, 'synthetic-test-generation', now+TTL-1))
        self.assertFalse(store.authenticated(token, 'synthetic-test-generation', now+TTL))
        self.assertFalse(store.authenticated(token, 'different-generation', now+1))
        self.assertFalse(store.authenticated(token+'x', 'synthetic-test-generation', now+1))
        code = '''import json,os,sys,time
from pg_sessions import PostgresSessions
s=PostgresSessions(os.environ['PICKNOW_TEST_DATABASE_URL'])
t=sys.stdin.read()
accepted=s.authenticated(t,'synthetic-test-generation',time.time())
s.revoke(t)
print(json.dumps({'accepted_after_process_restart':accepted}))
'''
        result = subprocess.run([sys.executable, '-c', code], input=token,
                                capture_output=True, text=True, timeout=40,
                                cwd=Path(__file__).resolve().parent)
        # Never print stderr/DSN: connection errors can contain sensitive context.
        self.assertEqual(result.returncode, 0, 'Postgres subprocess failed')
        self.assertTrue(json.loads(result.stdout)['accepted_after_process_restart'])
        self.assertFalse(PostgresSessions(dsn).authenticated(token, 'synthetic-test-generation', now+2))
        with store.connect() as db:
            self.assertEqual(db.execute('SELECT COUNT(*) FROM picknow_sessions WHERE token_hash=%s',
                                        (store.digest(token),)).fetchone()[0], 0)


if __name__ == '__main__':
    unittest.main()
