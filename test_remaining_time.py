import unittest
from remaining_time import remaining_regulation_seconds as remaining


class RemainingTimeTests(unittest.TestCase):
    def calculate(self, period=3, minutes=6, seconds=21, **changes):
        options = dict(regulation_periods=4, period_seconds=600,
                       clock_semantics_verified=True, league_rules_verified=True,
                       state_alignment_verified=True,
                       clock_direction='period_countdown', overtime=False)
        options.update(changes)
        return remaining(period, minutes, seconds, **options)

    def test_explicit_period_countdown_arithmetic(self):
        self.assertEqual(self.calculate(), 981)
        self.assertEqual(self.calculate(1, 10, 0), 2400)
        self.assertEqual(self.calculate(4, 0, 0), 0)
        self.assertEqual(self.calculate(3, 12, 0, period_seconds=720), 1440)
        self.assertEqual(self.calculate(1, 20, 0, regulation_periods=2,
                                        period_seconds=1200), 2400)

    def test_no_implicit_verification_or_clock_direction(self):
        self.assertIsNone(remaining(3, 6, 21, regulation_periods=4,
                                    period_seconds=600))
        for name in ('clock_semantics_verified', 'league_rules_verified',
                     'state_alignment_verified'):
            for value in (False, None, 1, 'true'):
                with self.subTest(name=name, value=value):
                    self.assertIsNone(self.calculate(**{name:value}))
        for direction in (None, 'count_up', 'game_countdown', True):
            self.assertIsNone(self.calculate(clock_direction=direction))

    def test_overtime_and_period_ambiguity_rejected(self):
        for value in (True, None, 0, 'false'):
            self.assertIsNone(self.calculate(overtime=value))
        for period in (0, -1, 5, True, 3.0, '3', None):
            self.assertIsNone(self.calculate(period=period))

    def test_malformed_or_impossible_time_rejected(self):
        for minutes,seconds in ((-1, 0), (10, 1), (11, 0), (0, 60),
                                (0, -1), (True, 0), (6, 21.0),
                                (float('inf'), 0), (0, float('nan'))):
            self.assertIsNone(self.calculate(minutes=minutes, seconds=seconds))
        for key in ('regulation_periods', 'period_seconds'):
            for value in (0, -1, True, None, 600.0, '600'):
                self.assertIsNone(self.calculate(**{key:value}))


if __name__ == '__main__':
    unittest.main()
