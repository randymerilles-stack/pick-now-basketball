"""Postgres session storage. Schema must be migrated before serving traffic."""
from contextlib import contextmanager
import hashlib
import secrets
import psycopg

TTL = 30 * 24 * 60 * 60
SCHEMA = '''CREATE TABLE IF NOT EXISTS picknow_sessions (
 token_hash TEXT PRIMARY KEY,
 generation TEXT NOT NULL,
 expires DOUBLE PRECISION NOT NULL
)'''


class SessionStoreUnavailable(RuntimeError):
    pass


class PostgresSessions:
    def __init__(self, dsn):
        self.dsn = dsn

    @contextmanager
    def connect(self):
        try:
            with psycopg.connect(self.dsn, connect_timeout=10) as db:
                # PgBouncer rejects startup 'options'; set a transaction-local limit.
                db.execute('SET LOCAL statement_timeout = 5000')
                yield db
        except psycopg.Error as exc:
            # Whitelist categories only; never log raw driver text or a DSN.
            detail=str(exc).lower()
            category='database_error'
            for needle,label in [('unsupported startup parameter','startup_parameter'),
                                 ('options','startup_options'), ('password authentication','credentials'),
                                 ('channel binding','channel_binding'), ('resolve','dns'),
                                 ('timeout','timeout'), ('ssl','tls')]:
                if needle in detail:
                    category=label
                    break
            state=exc.sqlstate if exc.sqlstate and exc.sqlstate.isalnum() else 'none'
            raise SessionStoreUnavailable(f'Session storage unavailable ({category}; SQLSTATE={state})') from None

    def migrate(self):
        with self.connect() as db:
            db.execute(SCHEMA)

    @staticmethod
    def digest(token):
        if not isinstance(token, str) or not 20 <= len(token) <= 100:
            return None
        return hashlib.sha256(token.encode()).hexdigest()

    def create(self, generation, now):
        if not isinstance(generation, str) or not generation:
            raise ValueError('Credential generation required')
        token = secrets.token_urlsafe(32)
        with self.connect() as db:
            # Transaction lock serializes capacity enforcement across instances.
            db.execute('SELECT pg_advisory_xact_lock(7069636)')
            db.execute('DELETE FROM picknow_sessions WHERE expires <= %s OR generation != %s',
                       (now, generation))
            db.execute('DELETE FROM picknow_sessions WHERE token_hash IN '
                       '(SELECT token_hash FROM picknow_sessions ORDER BY expires DESC OFFSET 127)')
            db.execute('INSERT INTO picknow_sessions VALUES (%s, %s, %s)',
                       (self.digest(token), generation, now + TTL))
        return token

    def authenticated(self, token, generation, now):
        digest = self.digest(token)
        if digest is None or not isinstance(generation, str) or not generation:
            return False
        with self.connect() as db:
            row = db.execute('SELECT 1 FROM picknow_sessions WHERE token_hash=%s '
                             'AND generation=%s AND expires>%s',
                             (digest, generation, now)).fetchone()
        return row is not None

    def revoke(self, token):
        digest = self.digest(token)
        if digest is not None:
            with self.connect() as db:
                db.execute('DELETE FROM picknow_sessions WHERE token_hash=%s', (digest,))
