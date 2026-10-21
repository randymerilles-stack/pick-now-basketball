import unittest
from timing_windows import timing_window


class TimingWindowTests(unittest.TestCase):
    def test_boundaries_are_nonoverlapping(self):
        expected = {0:'remaining_0_25', 599:'remaining_0_25',
                    600:'remaining_25_50', 1199:'remaining_25_50',
                    1200:'remaining_50_75', 1799:'remaining_50_75',
                    1800:'remaining_75_100', 2400:'remaining_75_100'}
        for remaining, window in expected.items():
            self.assertEqual(timing_window(remaining,2400,semantics_verified=True),window)

    def test_unknown_semantics_and_overtime_are_excluded(self):
        self.assertIsNone(timing_window(600,2400))
        self.assertIsNone(timing_window(600,2400,semantics_verified=1))
        self.assertIsNone(timing_window(600,2400,semantics_verified=True,overtime=True))

    def test_invalid_numbers_fail_closed(self):
        for remaining,total in [(True,2400),('600',2400),(None,2400),
                                (float('nan'),2400),(600,float('inf')),
                                (-1,2400),(2401,2400),(0,0),(0,-1)]:
            self.assertIsNone(timing_window(remaining,total,semantics_verified=True))

    def test_normalization_supports_distinct_regulation_lengths(self):
        self.assertEqual(timing_window(720,2880,semantics_verified=True),
                         timing_window(600,2400,semantics_verified=True))


if __name__ == '__main__':
    unittest.main()
