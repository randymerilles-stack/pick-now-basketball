"""Synthetic software checks only; these records are not training evidence."""
import unittest
from evaluation_split import plan_splits


def row(event, decision, outcome, **changes):
    result = dict(canonical_event_id=event, decision_at=decision,
                  outcome_available_at=outcome, identity_verified=True,
                  state_verified=True, odds_verified=True)
    result.update(changes)
    return result


class SplitTests(unittest.TestCase):
    def plan(self, rows):
        return plan_splits(rows, validation_start='2026-01-03T00:00:00Z',
                           test_start='2026-01-05T00:00:00Z')

    def test_event_grouping_and_boundaries(self):
        a = row('a', '2026-01-01T00:00:00Z', '2026-01-02T00:00:00Z')
        report = self.plan([a, a.copy(),
            row('b', '2026-01-03T00:00:00Z', '2026-01-04T00:00:00Z'),
            row('c', '2026-01-05T00:00:00Z', '2026-01-06T00:00:00Z')])
        self.assertEqual(report['event_counts'], dict(development=1, validation=1, test=1))
        self.assertFalse(report['approved_for_picks'])

    def test_straddler_purged_entirely(self):
        report = self.plan([row('a', '2026-01-02T00:00:00Z', '2026-01-04T00:00:00Z'),
                            row('a', '2026-01-03T00:00:00Z', '2026-01-04T00:00:00Z')])
        self.assertEqual(report['rejected'], {'event_straddles_cutoff': 1})
        self.assertEqual(sum(report['event_counts'].values()), 0)

    def test_late_label_purged_at_equality(self):
        report = self.plan([row('a', '2026-01-01T00:00:00Z', '2026-01-03T00:00:00Z')])
        self.assertEqual(report['rejected'], {'label_unavailable_at_next_block': 1})

    def test_unverified_side_invalidates_game(self):
        a = row('a', '2026-01-01T00:00:00Z', '2026-01-02T00:00:00Z')
        self.assertEqual(self.plan([a, dict(a, odds_verified=1)])['rejected'], {'unverified_event': 1})

    def test_bad_time_and_identity(self):
        report = self.plan([{}, row('a', '2026-01-01', '2026-01-02T00:00:00Z'),
            row('b', '2026-01-02T00:00:00Z', '2026-01-01T00:00:00Z')])
        self.assertEqual(report['status'], 'insufficient_data')
        self.assertEqual(len(report['rejected']), 3)

    def test_invalid_cutoffs_raise(self):
        with self.assertRaises(ValueError):
            plan_splits([], validation_start='2026-01-05T00:00:00Z', test_start='2026-01-03T00:00:00Z')


if __name__ == '__main__':
    unittest.main()
