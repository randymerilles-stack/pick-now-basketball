import copy
import math
import unittest
from paper_model import APPROACH, paper_forecasts


def report(offset=.04):
    return {'calibration_experiment': {'approach': APPROACH, 'trained': True,
            'training_fixtures': 221, 'heldout_fixtures': 108, 'offset': offset}}


def market():
    return {'fixture_id': 'game1', 'home': 'Home', 'away': 'Away', 'league': 'Test',
            'poll_age_seconds': 1, 'data_checks': 'passed', 'quotes': [
                {'team': 'Home', 'line': -4.5, 'odds': 1.9},
                {'team': 'Away', 'line': 4.5, 'odds': 1.9}]}


class PaperTests(unittest.TestCase):
    def test_computed_estimate_negative_ev_and_never_approved(self):
        pick = paper_forecasts([market()], report())[0]
        self.assertEqual(pick['team'], 'Home')
        self.assertAlmostEqual(pick['model_probability'], 1 / (1 + math.exp(-.04)))
        self.assertAlmostEqual(pick['estimated_ev'], pick['model_probability'] * 1.9 - 1)
        self.assertFalse(pick['positive_estimated_ev'])
        self.assertFalse(pick['approved_for_betting'])
        self.assertFalse(pick['independently_verified'])
    def test_stale_unchecked_or_push_lines_are_not_paper_picks(self):
        for key, value in [('poll_age_seconds', 30), ('poll_age_seconds', -1), ('data_checks', 'failed')]:
            m = market(); m[key] = value
            self.assertEqual(paper_forecasts([m], report()), [])
        m = market(); m['quotes'][0]['line'] = -4; m['quotes'][1]['line'] = 4
        self.assertEqual(paper_forecasts([m], report()), [])
    def test_missing_untested_or_corrupt_model_fails_closed(self):
        for field, value in [('trained', False), ('offset', float('nan')),
                             ('training_fixtures', None), ('heldout_fixtures', 99),
                             ('approach', 'different')]:
            r = report(); r['calibration_experiment'][field] = value
            self.assertEqual(paper_forecasts([market()], r), [])
        self.assertEqual(paper_forecasts([market()], {}), [])
    def test_one_candidate_per_fixture_even_when_multiple_lines(self):
        m = market(); other = copy.deepcopy(m)
        other['quotes'][0]['line'] = -5.5; other['quotes'][1]['line'] = 5.5
        picks = paper_forecasts([m, other], report(.3))
        self.assertEqual(len(picks), 1)
        self.assertTrue(picks[0]['positive_estimated_ev'])
        self.assertFalse(picks[0]['approved_for_betting'])

if __name__ == '__main__': unittest.main()
