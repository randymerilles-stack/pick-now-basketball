import unittest
from live_state import assess_live_state, observed_period, stats_diagnostics

class LiveStateTests(unittest.TestCase):
    def test_documented_basketball_stats_period_is_explicit(self):
        f={'stats':{'sport':'basketball','period':3}}
        self.assertEqual(observed_period(f),3)
        self.assertFalse(assess_live_state(f)['priority_ready'])

    def test_conflicting_or_virtual_period_is_not_accepted(self):
        self.assertIsNone(observed_period({'period':2,'stats':{'sport':'basketball','period':3}}))
        self.assertIsNone(observed_period({'stats':{'sport':'ebasketball','period':3}}))
        for p in [True,0,-1,'3']:
            self.assertIsNone(observed_period({'stats':{'sport':'basketball','period':p}}))

    def test_stats_score_and_time_are_checked_separately(self):
        f={'score':'70-60','stats':{'sport':'basketball','period':3,
           'home':{'points':70},'away':{'points':60},'updated_at':'2026-10-20T12:00:00Z'}}
        r=stats_diagnostics(f,'2026-10-20T12:00:20Z')
        self.assertTrue(r['stats_score_matches']);self.assertEqual(r['blockers'],[])
        f['stats']['away']['points']=61
        self.assertIn('stats_score_mismatch_or_missing',stats_diagnostics(f)['blockers'])
        for stamp in ['2026-10-20T12:00:30Z','2026-10-20T11:59:59Z']:
            self.assertIn('stats_observation_outside_30s_window',stats_diagnostics(f,stamp)['blockers'])
        f['stats']['updated_at']='2026-10-20T12:00:00'
        self.assertIn('stats_observation_time_unverified',stats_diagnostics(f,'2026-10-20T12:00:20Z')['blockers'])

    def test_clock_and_score_never_imply_quarter(self):
        r=assess_live_state({'score':'99-98','clock':{'min':0,'sec':14}})
        self.assertIn('explicit_period_missing',r['blockers'])
        self.assertIsNone(r['remaining_regulation_seconds'])
        self.assertFalse(r['priority_ready'])

    def test_explicit_period_presence_does_not_validate_semantics(self):
        r=assess_live_state({'score':'70-70','clock':{'min':4,'sec':12},'period':4})
        self.assertTrue(r['explicit_period_present'])
        self.assertIn('period_and_clock_semantics_unverified',r['blockers'])
        self.assertFalse(r['priority_ready'])

    def test_invalid_values_cannot_pass_presence_checks(self):
        for clock in [None,{}, {'min':True,'sec':2},{'min':-1,'sec':0},{'min':1,'sec':60}]:
            self.assertFalse(assess_live_state({'clock':clock})['clock_present'])
        for score in [None,False,'unknown','70-x']:
            self.assertFalse(assess_live_state({'score':score})['score_present'])
        for period in [None,False,0,-1,'']:
            self.assertFalse(assess_live_state({'period':period})['explicit_period_present'])

    def test_input_is_not_modified(self):
        f={'score':'1-2','clock':{'min':1,'sec':2}}
        import copy
        before=copy.deepcopy(f);assess_live_state(f);self.assertEqual(f,before)

if __name__=='__main__':unittest.main()
