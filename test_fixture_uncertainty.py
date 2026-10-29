"""Synthetic arithmetic tests only; no predictive evidence."""
from copy import deepcopy
import unittest
from fixture_uncertainty import fixture_bootstrap


def report(values):
    return dict(status='descriptive_only' if values else 'insufficient_data',
                approved_for_picks=False, independent_events=len(values),
                events=[dict(canonical_event_id=str(i), candidate_brier=.5+d/2,
                             baseline_brier=.5-d/2, paired_difference=d, decisions=1)
                        for i,d in enumerate(values)])


class BootstrapTests(unittest.TestCase):
    def test_zero_and_one_no_interval(self):
        for values in ([], [-.2]):
            result=fixture_bootstrap(report(values))
            self.assertIsNone(result['interval'])
            self.assertEqual(result['status'],'insufficient_independent_events')

    def test_two_event_interval_matches_enumerated_support(self):
        # Exhaustive size-two bootstrap support: -.25, 0, +.25 with
        # probabilities .25,.5,.25. Both percentile endpoints are extremes.
        result=fixture_bootstrap(report([-.25,.25]),resamples=2000,seed=17)
        self.assertEqual(result['interval'],[-.25,.25])
        self.assertEqual(result['paired_mean'],0)
        self.assertFalse(result['approved_for_picks'])
        self.assertFalse(result['statistical_power_established'])

    def test_seed_order_and_no_mutation(self):
        source=report([-.2,.1,.3,-.4])
        original=deepcopy(source)
        a=fixture_bootstrap(source,seed=91)
        source['events'].reverse()
        b=fixture_bootstrap(source,seed=91)
        self.assertEqual(a,b)
        source['events'].reverse()
        self.assertEqual(source,original)

    def test_ticks_do_not_change_event_weighting(self):
        source=report([-.2,.4])
        a=fixture_bootstrap(source)
        source['events'][0]['decisions']=10000
        self.assertEqual(fixture_bootstrap(source),a)
        self.assertAlmostEqual(a['paired_mean'],.1)

    def test_constant_sample_does_not_qualify(self):
        result=fixture_bootstrap(report([-.2,-.2,-.2]))
        self.assertTrue(result['degenerate_sample'])
        self.assertEqual(result['status'],'descriptive_interval_only')
        self.assertFalse(result['approved_for_picks'])

    def test_duplicate_ids_count_and_invalid_numbers(self):
        variants=[]
        source=report([.1,.2]);source['events'][1]['canonical_event_id']='0';variants.append(source)
        source=report([.1]);source['independent_events']=2;variants.append(source)
        for value in (True,float('nan'),float('inf'),2):
            source=report([.1]);source['events'][0]['candidate_brier']=value;variants.append(source)
        source=report([.1]);source['events'][0]['paired_difference']=.2;variants.append(source)
        for source in variants:
            with self.assertRaises(ValueError):fixture_bootstrap(source)

    def test_parameters_and_approval_claim_rejected(self):
        for options in (dict(resamples=True),dict(resamples=10),dict(resamples=20001),dict(seed=True)):
            with self.assertRaises(ValueError):fixture_bootstrap(report([.1,.2]),**options)
        source=report([.1,.2]);source['approved_for_picks']=True
        with self.assertRaises(ValueError):fixture_bootstrap(source)

    def test_frozen_scorer_to_bootstrap_roundtrip(self):
        from forecast_scoring import score_frozen_forecasts
        rows=[];outcomes=[]
        for event,margin in [('a',4),('b',2)]:
            rows.append(dict(canonical_event_id=event,decision_id='d',identity_verified=True,
                state_verified=True,odds_verified=True,forecast_persisted=True,
                candidate_version='synthetic-m',baseline_version='synthetic-b',
                model_frozen_at='2026-01-01T00:00:00Z',decision_at='2026-01-02T00:00:00Z',
                persisted_at='2026-01-02T00:00:01Z',home_line=-3.5,away_line=3.5,
                candidate_home=[.8,.2,0],candidate_away=[.2,.8,0],
                baseline_home=[.5,.5,0],baseline_away=[.5,.5,0]))
            outcomes.append(dict(canonical_event_id=event,settlement_verified=True,final_home_margin=margin,
                finished_at='2026-01-02T01:00:00Z',available_at='2026-01-02T01:01:00Z'))
        scored=score_frozen_forecasts(rows,outcomes,test_event_ids=['a','b'],
                                     model_versions=('synthetic-m','synthetic-b'))
        result=fixture_bootstrap(scored)
        self.assertEqual(result['independent_events'],2)
        self.assertAlmostEqual(result['paired_mean'],.09)
        self.assertFalse(result['approved_for_picks'])


if __name__=='__main__':
    unittest.main()
