import copy
import unittest
from clock_audit import compare_snapshots, clock_seconds


def sample(period=2,minute=4,second=30):
    return {'matches':[{'id':'1','home':'A','away':'B','league':'Example',
                       'score':'20-18','clock':{'min':minute,'sec':second,'ref':'2026-10-20T13:00:00Z'},
                       'stats':{'sport':'basketball','period':period}}]}


class ClockAuditTests(unittest.TestCase):
    def test_decreasing_observation_is_not_semantic_verification(self):
        result=compare_snapshots(sample(),sample(second=20))[0]
        self.assertEqual(result['same_period_clock_delta'],-10)
        self.assertEqual(result['direction_observed'],'decreasing')
        self.assertFalse(result['semantics_verified'])

    def test_period_change_never_looks_like_clock_direction(self):
        result=compare_snapshots(sample(),sample(period=3,minute=10,second=0))[0]
        self.assertIsNone(result['same_period_clock_delta'])
        self.assertEqual(result['direction_observed'],'not_comparable')

    def test_missing_and_conflicting_periods_are_not_comparable(self):
        after=sample();after['matches'][0]['period']=3
        self.assertEqual(compare_snapshots(sample(),after)[0]['direction_observed'],'not_comparable')

    def test_id_cannot_override_team_identity_or_real_sport(self):
        for key,value in [('home','Different'),('league','Other')]:
            after=sample();after['matches'][0][key]=value
            self.assertEqual(compare_snapshots(sample(),after),[])
        after=sample();after['matches'][0]['stats']['sport']='ebasketball'
        self.assertEqual(compare_snapshots(sample(),after),[])

    def test_invalid_clock_and_unchanged_state(self):
        self.assertIsNone(clock_seconds({'clock':{'min':True,'sec':1}}))
        self.assertIsNone(clock_seconds({'clock':{'min':2,'sec':60}}))
        before=sample();original=copy.deepcopy(before)
        self.assertEqual(compare_snapshots(before,sample())[0]['direction_observed'],'unchanged')
        self.assertEqual(before,original)


if __name__=='__main__':unittest.main()
