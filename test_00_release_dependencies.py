"""Explicit Render release gate for the existing unittest-only build command.

Enabled only by PICKNOW_RELEASE_ACCEPTANCE=1. Installs pinned requirements
before opt-in Postgres acceptance tests execute. Ordinary local runs skip it.
"""
import os
from pathlib import Path
import subprocess
import sys
import unittest


@unittest.skipUnless(os.environ.get('PICKNOW_RELEASE_ACCEPTANCE') == '1',
                     'Release dependency gate not enabled')
class ReleaseDependencies(unittest.TestCase):
    def test_install_pinned_release_requirements(self):
        result = subprocess.run([sys.executable, '-m', 'pip', 'install', '-r',
                                 str(Path(__file__).with_name('requirements.txt'))],
                                capture_output=True, text=True, timeout=180)
        # Avoid logging environment/index credentials in subprocess output.
        self.assertEqual(result.returncode, 0, 'Pinned dependency installation failed')
        import psycopg
        self.assertEqual(psycopg.__version__, '3.2.13')
