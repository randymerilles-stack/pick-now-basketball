import unittest
from live_state import assess_live_state

class LiveStateTests(unittest.TestCase):
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
