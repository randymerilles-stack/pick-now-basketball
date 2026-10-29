"""Synthetic frozen-forecast software cases, never predictive evidence."""
from copy import deepcopy
import json
import math
import unittest
from probability_diagnostics import diagnose_probabilities
from test_forecast_scoring import forecast, outcome


def diagnostics(rows, outcomes=None, ids=None):
    return diagnose_probabilities(rows, [outcome()] if outcomes is None else outcomes,
        test_event_ids=['a'] if ids is None else ids, model_versions=('score-time-test','market-test'))


class DiagnosticTests(unittest.TestCase):
    def test_known_log_loss_and_class_reliability(self):
        result=diagnostics([forecast()])
        candidate=result['models']['candidate']
        self.assertAlmostEqual(candidate['mean_event_log_loss'],-math.log(.8))
        self.assertAlmostEqual(candidate['fixed_bin_macro_ece'],(.2+.2+0)/3)
        bins=candidate['reliability']['home_win']
        self.assertEqual(bins[8]['mean_probability'],.8)
        self.assertEqual(bins[8]['observed_frequency'],1)
        self.assertFalse(result['approved_for_picks'])

    def test_event_weighting_does_not_count_ticks_as_games(self):
        rows=[forecast(decision_id=str(i)) for i in range(20)]+[forecast('b')]
        result=diagnostics(rows,[outcome(),outcome('b',final_home_margin=2)],['a','b'])
        model=result['models']['candidate']
        self.assertAlmostEqual(model['mean_event_log_loss'],(-math.log(.8)-math.log(.2))/2)
        self.assertEqual(model['reliability']['home_win'][8]['participating_events'],2)
        self.assertAlmostEqual(model['reliability']['home_win'][8]['observed_frequency'],.5)

    def test_push_zero_probability_is_infinite_not_clipped(self):
        result=diagnostics([forecast(home_line=-4,away_line=4)])
        model=result['models']['candidate']
        self.assertEqual(model['log_loss_status'],'infinite')
        self.assertIsNone(model['mean_event_log_loss'])
        self.assertEqual(model['zero_target_probability_events'],1)
        self.assertEqual(model['reliability']['push'][0]['observed_frequency'],1)
        json.dumps(result,allow_nan=False)

    def test_one_infinite_event_not_dropped_from_pooled_loss(self):
        result=diagnostics([forecast(),forecast('b',home_line=-4,away_line=4)],
                           [outcome(),outcome('b')],['a','b'])
        self.assertEqual(result['independent_events'],2)
        self.assertEqual(result['models']['candidate']['log_loss_status'],'infinite')
        self.assertIsNone(result['models']['candidate']['mean_event_log_loss'])

    def test_exact_bin_endpoints_and_perfect_prediction(self):
        row=forecast(candidate_home=[1,0,0],candidate_away=[0,1,0])
        model=diagnostics([row])['models']['candidate']
        self.assertEqual(model['mean_event_log_loss'],0)
        self.assertEqual(model['fixed_bin_macro_ece'],0)
        self.assertEqual(model['reliability']['home_win'][9]['mean_probability'],1)
        model=diagnostics([forecast(candidate_home=[.1,.9,0],candidate_away=[.9,.1,0])])['models']['candidate']
        self.assertEqual(model['reliability']['home_win'][1]['decision_count'],1)

    def test_validation_rejects_whole_event_and_empty_bins_stay_null(self):
        result=diagnostics([forecast(),forecast(decision_id='bad',odds_verified=False)])
        self.assertEqual(result['status'],'insufficient_data')
        self.assertEqual(result['scoring_rejected'],{'unverified_forecast':1})
        self.assertIsNone(result['models']['candidate']['reliability']['home_win'][0]['observed_frequency'])
        self.assertEqual(result['models']['candidate']['log_loss_status'],'no_data')

    def test_no_input_mutation_and_generator_inputs(self):
        rows=[forecast()]; outcomes=[outcome()]
        original=deepcopy((rows,outcomes))
        result=diagnostics(iter(rows),iter(outcomes))
        self.assertEqual(result['independent_events'],1)
        self.assertEqual((rows,outcomes),original)


if __name__=='__main__':
    unittest.main()
