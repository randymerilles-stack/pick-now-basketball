"""Session backend for an explicitly provisioned durable SQLite mount.

Not wired to the live app. An ephemeral path does not provide deploy durability.
Database files and production identifiers must never be committed to GitHub.
"""
import hashlib
from contextlib import contextmanager
from pathlib import Path
import secrets
import sqlite3

TTL = 30 * 24 * 60 * 60


class DurableSessions:
    def __init__(self, path):
        self.path = str(Path(path))
        with self.connect() as db:
            db.execute('CREATE TABLE IF NOT EXISTS sessions '
                       '(token_hash TEXT PRIMARY KEY, generation TEXT NOT NULL, expires REAL NOT NULL)')

    @contextmanager
    def connect(self):
        db = sqlite3.connect(self.path, timeout=5)
        try:
            with db:
                yield db
        finally:
            db.close()

    @staticmethod
    def token_hash(token):
        if not isinstance(token, str) or not 20 <= len(token) <= 100:
            return None
        return hashlib.sha256(token.encode()).hexdigest()

    def create(self, generation, now):
        if not isinstance(generation, str) or not generation:
            raise ValueError('Credential generation required')
        token = secrets.token_urlsafe(32)
        with self.connect() as db:
            db.execute('BEGIN IMMEDIATE')
            db.execute('DELETE FROM sessions WHERE expires <= ? OR generation != ?', (now, generation))
            # Retain the existing single-owner limit of 128 sessions.
            db.execute('DELETE FROM sessions WHERE token_hash IN '
                       '(SELECT token_hash FROM sessions ORDER BY expires DESC LIMIT -1 OFFSET 127)')
            db.execute('INSERT INTO sessions VALUES (?, ?, ?)',
                       (self.token_hash(token), generation, now + TTL))
        return token

    def authenticated(self, token, generation, now):
        digest = self.token_hash(token)
        if digest is None or not isinstance(generation, str) or not generation:
            return False
        with self.connect() as db:
            row = db.execute('SELECT 1 FROM sessions WHERE token_hash = ? '
                             'AND generation = ? AND expires > ?',
                             (digest, generation, now)).fetchone()
        return row is not None

    def revoke(self, token):
        digest = self.token_hash(token)
        if digest is not None:
            with self.connect() as db:
                db.execute('DELETE FROM sessions WHERE token_hash = ?', (digest,))
