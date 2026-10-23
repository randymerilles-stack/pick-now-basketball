from copy import deepcopy
import unittest
from scoreboard_alignment import compare_nbl


def sample():
    f={'id':'1','sport':'basketball','league':'Australia NBL','home':'Home',
       'away':'Away','kickoff_utc':'2026-10-23T10:30:00Z','score':'54-59',
       'stats':{'period':3,'sport':'basketball','home':{'points':54},'away':{'points':59}},
       'clock':{'min':6,'sec':35}}
    e={'id':'2','date':'2026-10-23T10:30Z','status':{'clock':390.0,'period':3,
       'type':{'state':'in','completed':False}},'competitions':[{'id':'2',
       'competitors':[{'homeAway':s,'team':{'displayName':name},'score':score}
       for s,name,score in [('home','Home','54'),('away','Away','59')]]}]}
    return f,e


class AlignmentTests(unittest.TestCase):
    def test_matching_identity_score_period_but_clock_disagreement(self):
        f,e=sample();r=compare_nbl(f,e)
        self.assertTrue(r['identity_matches']);self.assertTrue(r['score_matches'])
        self.assertTrue(r['period_matches']);self.assertEqual(r['clock_delta_seconds'],5)
        self.assertFalse(r['clock_matches']);self.assertFalse(r['training_eligible'])

    def test_even_matching_clocks_never_approve_model_or_data(self):
        f,e=sample();e['status']['clock']=395
        r=compare_nbl(f,e)
        self.assertTrue(r['clock_matches']);self.assertFalse(r['approved_for_picks'])
        self.assertFalse(r['training_eligible'])

    def test_wrong_orientation_time_and_duplicate_competitors_rejected(self):
        f,e=sample()
        for changed in (dict(f,home='Away',away='Home'),dict(f,kickoff_utc='2026-10-24T10:30Z'),
                        dict(f,league='Club Friendlies')):
            self.assertFalse(compare_nbl(changed,e)['identity_matches'])
        e['competitions'][0]['competitors']*=2
        self.assertFalse(compare_nbl(f,e)['identity_matches'])

    def test_period_change_and_malformed_clock_not_compared(self):
        f,e=sample()
        for value in (4,True,None):
            c=deepcopy(e);c['status']['period']=value
            self.assertIsNone(compare_nbl(f,c)['clock_delta_seconds'])
        for value in (True,float('nan'),-1,'390'):
            c=deepcopy(e);c['status']['clock']=value
            self.assertIsNone(compare_nbl(f,c)['clock_delta_seconds'])

    def test_finished_or_score_mismatch_not_synchronized(self):
        f,e=sample();e['competitions'][0]['competitors'][0]['score']='56'
        self.assertFalse(compare_nbl(f,e)['score_matches'])
        e['status']['type']['completed']=True
        self.assertFalse(compare_nbl(f,e)['clock_matches'])

    def test_provider_internal_score_disagreement_preserved(self):
        f,e=sample();f['stats']['home']['points']=56
        result=compare_nbl(f,e)
        self.assertTrue(result['score_matches'])
        self.assertFalse(result['provider_stats_score_matches'])
        self.assertFalse(result['training_eligible'])


if __name__=='__main__':unittest.main()
