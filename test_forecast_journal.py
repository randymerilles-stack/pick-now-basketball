"""Synthetic temporary journals only; no real forecasts or training evidence."""
from copy import deepcopy
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import sqlite3
import tempfile
import unittest
from unittest.mock import patch
from forecast_journal import append_forecast, read_forecast
from forecast_scoring import score_frozen_forecasts
from test_feature_admission import fixture


class JournalTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.path = Path(self.temp.name)/'research.sqlite'
        self.record, self.registry = fixture()
        self.prediction = dict(decision_id='d1', candidate_version='test-score-time', baseline_version='test-market',
                               model_frozen_at='2026-01-01T00:00:00Z', candidate_home=[.8,.2,0],
                               candidate_away=[.2,.8,0], baseline_home=[.5,.5,0], baseline_away=[.5,.5,0])
        self.clock = patch('forecast_journal.utc_now', return_value=datetime(2026,1,1,1,0,6,tzinfo=timezone.utc))
        self.clock.start()
        self.addCleanup(self.clock.stop)

    def append(self):
        return append_forecast(self.path, self.record, self.prediction, evidence_registry=self.registry)

    def test_reopen_and_score_roundtrip_no_mutation(self):
        original = deepcopy((self.record, self.prediction))
        receipt = self.append()
        row = read_forecast(self.path, json.loads(json.dumps(receipt)))
        outcome = dict(canonical_event_id='g', settlement_verified=True, final_home_margin=-8,
                       finished_at='2026-01-01T02:00:00Z', available_at='2026-01-01T02:01:00Z')
        report = score_frozen_forecasts([row], [outcome], test_event_ids=['g'],
                                       model_versions=('test-score-time','test-market'))
        self.assertEqual(report['independent_events'], 1)
        self.assertFalse(row['approved_for_picks'])
        self.assertEqual(original, (self.record, self.prediction))

    def test_duplicate_refuses_changed_forecast(self):
        receipt = self.append()
        self.prediction.update(candidate_home=[.7,.3,0], candidate_away=[.3,.7,0])
        with self.assertRaises(ValueError):
            self.append()
        self.assertEqual(read_forecast(self.path, receipt)['candidate_home'], [.8,.2,0])

    def test_tampered_payload_even_if_db_digest_rewritten(self):
        receipt = self.append()
        with sqlite3.connect(self.path) as db:
            payload = db.execute('SELECT payload FROM forecasts').fetchone()[0]
            changed = payload.replace('test-score-time', 'rewritten-model')
            db.execute('UPDATE forecasts SET payload=?, digest=?',
                       (changed, hashlib.sha256(changed.encode()).hexdigest()))
        with self.assertRaisesRegex(ValueError, 'digest mismatch'):
            read_forecast(self.path, receipt)

    def test_missing_evidence_and_outcome_injection(self):
        with self.assertRaises(ValueError):
            append_forecast(self.path, self.record, self.prediction)
        self.prediction['final_home_margin'] = 1
        with self.assertRaisesRegex(ValueError, 'Forecast-only'):
            self.append()

    def test_stale_or_future_local_decision(self):
        for now in (datetime(2026,1,1,1,1,0,tzinfo=timezone.utc),
                    datetime(2026,1,1,1,0,4,tzinfo=timezone.utc)):
            with patch('forecast_journal.utc_now', return_value=now):
                with self.assertRaisesRegex(ValueError, 'future or stale'):
                    self.append()

    def test_concurrent_writers_cannot_duplicate_decision(self):
        from concurrent.futures import ThreadPoolExecutor
        def attempt():
            try:
                self.append()
                return 'saved'
            except ValueError:
                return 'duplicate'
        with ThreadPoolExecutor(max_workers=2) as pool:
            results = list(pool.map(lambda _: attempt(), range(2)))
        self.assertEqual(sorted(results), ['duplicate', 'saved'])

    def test_receipt_must_match_and_follow_insertion(self):
        receipt = self.append()
        with self.assertRaises(ValueError):
            read_forecast(self.path, dict(receipt, sha256='0'*64))
        with self.assertRaises(ValueError):
            read_forecast(self.path, dict(receipt, persisted_at='2026-01-01T01:00:04Z'))

    def test_future_model_and_asymmetric_forecast(self):
        for change in (dict(model_frozen_at='2026-01-02T00:00:00Z'), dict(candidate_away=[.8,.2,0])):
            original = self.prediction.copy()
            self.prediction.update(change)
            with self.assertRaises(ValueError):
                self.append()
            self.prediction = original


if __name__ == '__main__':
    unittest.main()
