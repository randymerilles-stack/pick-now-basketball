"""One lifetime source-call reservation; schema must be provisioned separately.

No auto migration/reset, retry or auth-table access. Commit before returning
reserved. Ambiguous commit failures deny the source call and may burn the slot.
"""
from uuid import UUID

INSERT = """INSERT INTO picknow_oddize_probe_budget(singleton, request_id)
VALUES (true, %s) ON CONFLICT (singleton) DO NOTHING RETURNING request_id"""
SELECT = 'SELECT request_id FROM picknow_oddize_probe_budget WHERE singleton = true'


class PostgresProbeBudget:
    def __init__(self, connect):
        self.connect = connect

    def __call__(self, request_id):
        value = UUID(request_id)
        if value.version != 4 or str(value) != request_id:
            raise ValueError('Canonical UUID4 required')
        # Explicit READ COMMITTED: after a competing insert commits, the next
        # statement gets a new snapshot and observes the winning reservation.
        with self.connect() as conn:
            with conn.cursor() as cur:
                cur.execute('SET TRANSACTION ISOLATION LEVEL READ COMMITTED')
                cur.execute(INSERT, (request_id,))
                inserted = cur.fetchone()
                if inserted:
                    result = 'reserved'
                else:
                    cur.execute(SELECT)
                    row = cur.fetchone()
                    if not row:
                        raise RuntimeError('Budget invariant failed')
                    result = 'already_used' if str(row[0]) == request_id else 'exhausted'
            conn.commit()
        return result
