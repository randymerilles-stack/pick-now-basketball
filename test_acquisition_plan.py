import unittest
from acquisition_plan import plan

class PlanTests(unittest.TestCase):
    def test_future_schedule_does_not_claim_live(self):
        e={'id':'1','date':'2026-10-24T01:00:00Z','status':{'type':{'state':'pre'}}}
        r=plan([{'name':'nba','events':[e]}],'2026-10-23T17:00:00Z')
        self.assertEqual(r['targets'][0]['observed_state'],'pre')
        self.assertFalse(r['training_eligible'])
    def test_completed_past_pregame_and_invalid_rejected(self):
        events=[{'id':str(i),'date':d,'status':{'type':{'state':s}}} for i,(d,s) in enumerate([('2026-10-22T01:00:00Z','pre'),('2026-10-25T01:00:00Z','post'),('2026-10-24T01:00:00','pre')])]
        r=plan([{'name':'nbl','events':events}],'2026-10-23T17:00:00Z')
        self.assertEqual(r['targets'],[]);self.assertEqual(r['invalid_dates'],1)
