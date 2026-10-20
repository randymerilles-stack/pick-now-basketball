import unittest
from datetime import datetime,timezone
from prospective_capture import capture
from test_validation import sample

class CaptureTests(unittest.TestCase):
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
