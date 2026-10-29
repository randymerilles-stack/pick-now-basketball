"""Synthetic regression cases only; never use these as training evidence."""
import unittest
from copy import deepcopy
from forecast_scoring import score_frozen_forecasts


def forecast(event='a', **changes):
    row = dict(canonical_event_id=event, decision_id='d1', identity_verified=True,
               state_verified=True, odds_verified=True, forecast_persisted=True,
               candidate_version='score-time-test', baseline_version='market-test',
               model_frozen_at='2026-01-01T00:00:00Z', decision_at='2026-01-02T00:00:00Z',
               persisted_at='2026-01-02T00:00:01Z', home_line=-3.5, away_line=3.5,
               candidate_home=[.8, .2, 0], candidate_away=[.2, .8, 0],
               baseline_home=[.5, .5, 0], baseline_away=[.5, .5, 0])
    return dict(row, **changes)


def outcome(event='a', **changes):
    return dict(dict(canonical_event_id=event, settlement_verified=True, final_home_margin=4,
                     finished_at='2026-01-02T02:00:00Z', available_at='2026-01-02T02:01:00Z'), **changes)


class ScoreTests(unittest.TestCase):
    def score(self, rows, results=None, ids=None):
        return score_frozen_forecasts(rows, [outcome()] if results is None else results,
                                      test_event_ids=['a'] if ids is None else ids,
                                      model_versions=('score-time-test', 'market-test'))

    def test_handicap_not_winner_and_known_brier(self):
        report = self.score([forecast()])
        self.assertAlmostEqual(report['mean_paired_brier_difference'], .04-.25)
        loss = self.score([forecast()], [outcome(final_home_margin=2)])
        self.assertAlmostEqual(loss['events'][0]['candidate_brier'], .64)
        self.assertFalse(report['approved_for_picks'])

    def test_push_is_separate_class(self):
        report = self.score([forecast(home_line=-4, away_line=4)])
        self.assertEqual(report['events'][0]['push_decisions'], 1)
        self.assertAlmostEqual(report['events'][0]['candidate_brier'], .84)

    def test_event_weighting_not_ticks(self):
        rows = [forecast(decision_id=str(i)) for i in range(10)]
        rows.append(forecast('b'))
        report = self.score(rows, [outcome(), outcome('b', final_home_margin=1)], ['a', 'b'])
        self.assertEqual(report['independent_events'], 2)
        self.assertAlmostEqual(report['mean_paired_brier_difference'], (.04-.25+.64-.25)/2)

    def test_duplicates_reject_whole_game(self):
        self.assertEqual(self.score([forecast(), forecast()])['independent_events'], 0)
        self.assertEqual(self.score([forecast()], [outcome(), outcome()])['independent_events'], 0)

    def test_reject_after_finish_even_before_receipt(self):
        row = forecast(persisted_at='2026-01-02T02:00:30Z')
        self.assertEqual(self.score([row])['rejected'], {'invalid_chronology': 1})

    def test_reject_invalid_or_unverified_side(self):
        for change in [dict(candidate_home=[float('nan'), .2, 0]),
                       dict(candidate_away=[.8, .2, 0]), dict(odds_verified=1),
                       dict(away_line=2.5), dict(candidate_version=''),
                       dict(candidate_version='tuned-on-test'),
                       dict(decision_at='2026-01-02')]:
            with self.subTest(change=change):
                self.assertEqual(self.score([forecast(**change)])['independent_events'], 0)

    def test_manifest_and_empty_and_no_mutation(self):
        row = forecast()
        before = deepcopy(row)
        self.score([row])
        self.assertEqual(row, before)
        self.assertEqual(self.score([])['status'], 'insufficient_data')
        self.assertEqual(self.score([forecast('other')])['rejected'], {'outside_locked_test': 1})
        with self.assertRaises(ValueError):
            self.score([], ids=['a', 'a'])


if __name__ == '__main__':
    unittest.main()
