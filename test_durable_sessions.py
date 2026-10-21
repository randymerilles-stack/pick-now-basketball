import sqlite3
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from durable_sessions import DurableSessions, TTL


class DurableSessionTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.path = str(Path(self.temp.name) / 'sessions.sqlite')
        self.store = DurableSessions(self.path)

    def test_process_restart_and_durable_logout_revocation(self):
        token = self.store.create('synthetic-generation', 1000)
        code = ('import sys; from durable_sessions import DurableSessions; '
                's=DurableSessions(sys.argv[1]); t=sys.stdin.read(); '
                'print(s.authenticated(t,"synthetic-generation",2000)); s.revoke(t)')
        result = subprocess.run([sys.executable, '-c', code, self.path], input=token,
                                capture_output=True, text=True, check=True, timeout=10,
                                cwd=Path(__file__).resolve().parent)
        self.assertEqual(result.stdout.strip(), 'True')
        self.assertFalse(DurableSessions(self.path).authenticated(token, 'synthetic-generation', 2001))

    def test_expiry_generation_and_tampering(self):
        token = self.store.create('first', 1000)
        self.assertTrue(self.store.authenticated(token, 'first', 1000 + TTL - 1))
        self.assertFalse(self.store.authenticated(token, 'first', 1000 + TTL))
        self.assertFalse(self.store.authenticated(token, 'changed', 1001))
        self.assertFalse(self.store.authenticated(token + 'x', 'first', 1001))
        self.assertFalse(self.store.authenticated(None, 'first', 1001))

    def test_raw_token_not_stored_and_capacity_bounded(self):
        token = self.store.create('first', 1000)
        with sqlite3.connect(self.path) as db:
            row = db.execute('SELECT token_hash FROM sessions').fetchone()
        self.assertNotEqual(row[0], token)
        self.assertEqual(len(row[0]), 64)
        for i in range(130):
            self.store.create('first', 1001 + i)
        with sqlite3.connect(self.path) as db:
            self.assertEqual(db.execute('SELECT COUNT(*) FROM sessions').fetchone()[0], 128)
        self.assertFalse(self.store.authenticated(token, 'first', 1200))


if __name__ == '__main__':
    unittest.main()
