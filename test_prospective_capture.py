import unittest
from datetime import datetime,timezone
from prospective_capture import capture
from test_validation import sample

class CaptureTests(unittest.TestCase):
    def test_group_provenance_is_detached_from_input(self):
        data=sample()
        record=capture(data,datetime(2026,10,20,3,0,tzinfo=timezone.utc))
        o=record['observations'][0]
        self.assertEqual(o['handicap_group_id'],'112')
        self.assertEqual(o['handicap_group_status_observed'],data['matches'][0]['group_status']['112'])
        data['matches'][0]['group_status']['112']['polled_at']='changed'
        self.assertEqual(o['handicap_group_status_observed']['polled_at'],'2026-10-20T02:59:55Z')
    def test_opt_in_stats_period_is_preserved_without_approval(self):
        data=sample();fixture=data['matches'][0]
        fixture['score']='55-51';fixture['clock']={'min':4,'sec':12}
        fixture['stats']={'sport':'basketball','period':3,'home':{'points':55},
                          'away':{'points':51},'updated_at':'2026-10-20T03:00:00Z'}
        record=capture(data,datetime(2026,10,20,3,0,tzinfo=timezone.utc))
        o=record['observations'][0]
        self.assertEqual(record['schema_version'],3)
        self.assertIn('stats=1',record['source'])
        self.assertEqual(o['period_observed'],3)
        self.assertEqual(o['stats_observed'],fixture['stats'])
        self.assertTrue(o['live_state_readiness']['explicit_period_present'])
        self.assertFalse(o['live_state_readiness']['priority_ready'])

    def test_capture_preserves_observed_state_without_fabricating_period_or_outcome(self):
        data=sample();fixture=data['matches'][0]
        fixture['score']='55-51';fixture['clock']={'min':4,'sec':12}
        record=capture(data,datetime(2026,10,20,3,0,tzinfo=timezone.utc))
        self.assertEqual(len(record['observations']),1)
        observation=record['observations'][0]
        self.assertEqual(observation['score_observed'],'55-51')
        self.assertEqual(observation['clock_observed'],{'min':4,'sec':12})
        self.assertIsNone(observation['period_observed'])
        self.assertIsNone(observation['outcome'])
        self.assertFalse(observation['independently_verified'])
        self.assertFalse(record['approved_for_picks'])
    def test_stale_feed_cannot_become_a_training_observation(self):
        record=capture(sample(),datetime(2026,10,20,3,2,tzinfo=timezone.utc))
        self.assertEqual(record['observations'],[])
        self.assertFalse(record['approved_for_picks'])

if __name__=='__main__':unittest.main()
