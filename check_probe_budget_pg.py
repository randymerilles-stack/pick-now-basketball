"""Explicit isolated-ledger integration check; no schema writes or resets."""
import os
import json
from concurrent.futures import ThreadPoolExecutor
import psycopg
from probe_budget import PostgresProbeBudget


def check(url):
    store = PostgresProbeBudget(lambda: psycopg.connect(url, connect_timeout=15))
    ids = ['151f046a-6621-4bb2-9f8a-9bfb6ff08400',
           '951f046a-6621-4bb2-9f8a-9bfb6ff08400'] * 3
    with ThreadPoolExecutor(max_workers=3) as pool:
        results = list(pool.map(store, ids))
    assert results == ['already_used', 'exhausted'] * 3
    with psycopg.connect(url, connect_timeout=15) as conn:
        count = conn.execute('SELECT count(*) FROM picknow_oddize_probe_budget').fetchone()[0]
    assert count == 1
    return dict(driver='psycopg', attempts=6, replay_rejected=3,
                exhausted_rejected=3, reservations=count, approved_for_picks=False)


if __name__ == '__main__':
    try:
        print(json.dumps(check(os.environ['PICKNOW_ISOLATED_TEST_DATABASE_URL'])))
    except Exception as error:
        # Never print database URLs or driver exception messages.
        print(json.dumps(dict(status='failed', error_type=type(error).__name__)))
        raise SystemExit(1)
