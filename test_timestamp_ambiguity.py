import unittest
from timestamp_ambiguity import reversal_intervals


class AmbiguityTests(unittest.TestCase):
    def play(self, ts, score=10):
        return dict(id=ts, wallclock=ts, period={'number': 2},
                    clock={'displayValue': '5:00'}, homeScore=score, awayScore=9)

    def test_reversal_retains_exact_interval_without_approval(self):
        result = reversal_intervals([self.play('2026-10-23T01:02:00Z'), self.play('2026-10-23T01:00:00Z')])
        self.assertEqual(result['intervals'][0]['backward_seconds'], 120)
        self.assertTrue(result['intervals'][0]['same_game_state'])
        self.assertFalse(result['training_eligible'])
        self.assertFalse(result['approved_for_picks'])

    def test_changed_score_is_not_same_state(self):
        r = reversal_intervals([self.play('2026-10-23T01:02:00Z'), self.play('2026-10-23T01:00:00Z', 12)])
        self.assertFalse(r['intervals'][0]['same_game_state'])

    def test_equal_ordered_missing_and_invalid_are_not_reversals(self):
        self.assertEqual(reversal_intervals([{}, self.play('bad'), self.play('2026-10-23T01:00:00Z'), self.play('2026-10-23T01:00:00Z')])['reversal_count'], 0)

    def test_input_is_not_sorted_or_changed(self):
        p = [self.play('2026-10-23T01:02:00Z'), self.play('2026-10-23T01:00:00Z')]
        original = repr(p)
        reversal_intervals(p)
        self.assertEqual(repr(p), original)
