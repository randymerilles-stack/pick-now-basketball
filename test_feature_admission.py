"""All observations and evidence below are synthetic software fixtures only."""
from copy import deepcopy
import unittest
from feature_admission import admit_features


def fixture():
    state = dict(canonical_event_id='g', source='s1', observed_at='2026-01-01T01:00:00Z',
                 phase='in',
                 received_at='2026-01-01T01:00:01Z',
                 home_score=50, away_score=60, period=3, minutes=6, seconds=0, overtime=False)
    quote = dict(canonical_event_id='g', source='q1', observed_at=state['observed_at'], bookmaker='book',
                 received_at=state['received_at'],
                 scope='full_game_handicap', includes_overtime=True, home_line=9.5, away_line=-9.5,
                 home_odds=2.0, away_odds=2.0)
    record = dict(evidence_id='synthetic', canonical_event_id='g', league='test', bookmaker='book',
                  decision_at='2026-01-01T01:00:05Z', state=state, independent_state=dict(state, source='s2'),
                  quote=quote, independent_quote=dict(quote, source='q2'))
    evidence = dict(reviewed=True, identity=True, clock_semantics=True, league_rules=True, settlement=True,
                    independent_provenance=True, references=['synthetic-test-only'], canonical_event_id='g',
                    league='test', bookmaker='book', reviewed_at='2025-12-31T00:00:00Z',
                    regulation_periods=4, period_seconds=720, clock_direction='period_countdown')
    evidence.update(state_sources=['s1', 's2'], quote_sources=['q1', 'q2'])
    return record, {'synthetic': evidence}


class AdmissionTests(unittest.TestCase):
    def test_verified_synthetic_math_and_both_sides(self):
        record, registry = fixture()
        original = deepcopy((record, registry))
        result = admit_features(record, evidence_registry=registry)
        self.assertEqual(result['remaining_seconds'], 1080)
        self.assertEqual(result['sides']['home']['score_margin'], -10)
        self.assertEqual(result['sides']['away']['score_margin'], 10)
        self.assertEqual(result['timing_window'], 'remaining_25_50')
        self.assertFalse(result['training_eligible'])
        self.assertFalse(result['approved_for_picks'])
        self.assertEqual((record, registry), original)

    def test_default_registry_accepts_nothing(self):
        record, _ = fixture()
        self.assertEqual(admit_features(record)['reason'], 'unreviewed_evidence')

    def test_review_must_precede_decision_and_match_identity(self):
        for key, value in [('reviewed_at', '2026-01-02T00:00:00Z'), ('canonical_event_id', 'other'),
                           ('independent_provenance', 1), ('references', [])]:
            record, registry = fixture()
            registry['synthetic'][key] = value
            self.assertEqual(admit_features(record, evidence_registry=registry)['status'], 'rejected')

    def test_freshness_and_skew(self):
        for ts in ['2026-01-01T00:59:34Z', '2026-01-01T01:00:06Z', '2026-01-01T00:59:54Z', '2026-01-01']:
            record, registry = fixture()
            record['quote']['observed_at'] = ts
            self.assertEqual(admit_features(record, evidence_registry=registry)['status'], 'rejected')

    def test_state_quarter_clock_and_score_disagree(self):
        for key, value in [('period', 2), ('seconds', 1), ('home_score', 51), ('overtime', True)]:
            record, registry = fixture()
            record['independent_state'][key] = value
            self.assertEqual(admit_features(record, evidence_registry=registry)['status'], 'rejected')

    def test_quote_scope_price_and_source(self):
        for key, value in [('scope', 'q3'), ('includes_overtime', False), ('home_odds', 1.9),
                           ('source', 'q1'), ('bookmaker', 'other'), ('home_line', 8.5)]:
            record, registry = fixture()
            record['independent_quote'][key] = value
            self.assertEqual(admit_features(record, evidence_registry=registry)['status'], 'rejected')

    def test_invalid_numbers_no_period_inference(self):
        for field, key, value in [('state', 'period', None), ('state', 'home_score', True),
                                  ('quote', 'home_odds', float('nan')), ('quote', 'away_odds', 1)]:
            record, registry = fixture()
            record[field][key] = value
            self.assertEqual(admit_features(record, evidence_registry=registry)['status'], 'rejected')

    def test_unknown_clock_semantics(self):
        record, registry = fixture()
        registry['synthetic']['clock_direction'] = 'unknown'
        self.assertEqual(admit_features(record, evidence_registry=registry)['reason'], 'invalid_regulation_clock')

    def test_final_or_unknown_phase_rejected_despite_nonzero_clock(self):
        for side in ('state', 'independent_state'):
            for phase in ('post', 'pre', None):
                record, registry = fixture()
                record[side].update(phase=phase, period=4, minutes=12, seconds=0)
                other = 'independent_state' if side == 'state' else 'state'
                record[other].update(period=4, minutes=12, seconds=0)
                self.assertEqual(admit_features(record, evidence_registry=registry)['reason'],
                                 'not_explicitly_in_play')

    def test_receipts_and_reviewed_sources(self):
        for key, value in [('received_at', '2026-01-01T01:00:06Z'),
                           ('received_at', '2026-01-01T00:59:59Z'), ('source', 'unreviewed')]:
            record, registry = fixture()
            record['quote'][key] = value
            self.assertEqual(admit_features(record, evidence_registry=registry)['status'], 'rejected')


if __name__ == '__main__':
    unittest.main()
