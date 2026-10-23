"""Process-boundary acceptance check for remembered owner login.

Memory-only fallback intentionally loses sessions; Postgres acceptance is
covered separately and must opt into an isolated test database.
Uses an isolated synthetic password hash; never reads production credentials.
"""
import hashlib
import os
from pathlib import Path
import subprocess
import sys
import unittest


class RestartAcceptanceTests(unittest.TestCase):
    def run_process(self, code, token=None):
        salt = '22' * 16
        digest = hashlib.pbkdf2_hmac(
            'sha256', b'synthetic-restart-test-password', bytes.fromhex(salt), 200_000
        ).hex()
        env = dict(os.environ, PICKNOW_PASSWORD_HASH=salt + '
        if token is not None:
            env['TEST_SESSION_TOKEN'] = token
        result = subprocess.run(
            [sys.executable, '-c', code], cwd=Path(__file__).resolve().parent,
            env=env, capture_output=True, text=True, timeout=10, check=True,
        )
        return result.stdout.strip()

    def test_new_session_authenticates_in_original_process(self):
        self.assertEqual(self.run_process(
            "import access; t=access.new_session(); "
            "print(access.authenticated(access.COOKIE+'='+t))"
        ), 'True')

    def test_memory_fallback_does_not_claim_restart_persistence(self):
        token = self.run_process('import access; print(access.new_session())')
        accepted = self.run_process(
            "import access,os; print(access.authenticated("
            "access.COOKIE+'='+os.environ['TEST_SESSION_TOKEN']))", token
        )
        self.assertEqual(accepted, 'False',
                         'Memory-only fallback must not masquerade as durable storage')


if __name__ == '__main__':
    unittest.main()
 + digest,
                   PICKNOW_DATABASE_URL='')
        if token is not None:
            env['TEST_SESSION_TOKEN'] = token
        result = subprocess.run(
            [sys.executable, '-c', code], cwd=Path(__file__).resolve().parent,
            env=env, capture_output=True, text=True, timeout=10, check=True,
        )
        return result.stdout.strip()

    def test_new_session_authenticates_in_original_process(self):
        self.assertEqual(self.run_process(
            "import access; t=access.new_session(); "
            "print(access.authenticated(access.COOKIE+'='+t))"
        ), 'True')

    @unittest.expectedFailure
    def test_remembered_session_must_survive_fresh_server_process(self):
        token = self.run_process('import access; print(access.new_session())')
        accepted = self.run_process(
            "import access,os; print(access.authenticated("
            "access.COOKIE+'='+os.environ['TEST_SESSION_TOKEN']))", token
        )
        self.assertEqual(accepted, 'True',
                         '30-day cookie is rejected by a fresh server process')


if __name__ == '__main__':
    unittest.main()
