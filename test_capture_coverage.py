import unittest
from capture_coverage import coverage

class CoverageTests(unittest.TestCase):
    def sample(self, state='in', home='A', away='B'):
        return {'sources': [{'name':'provider','fixtures':[{'id':'p','home':'A','away':'B','in_play':True}]}, {'name':'espn','events':[{'id':'e','status':{'type':{'state':state}},'competitions':[{'competitors':[{'homeAway':'home','team':{'displayName':home}},{'homeAway':'away','team':{'displayName':away}}]}]}]}]}
    def test_exact_live_candidate_never_promoted(self):
        r=coverage(self.sample());self.assertEqual(len(r['exact_name_candidates']),1);self.assertFalse(r['training_eligible'])
    def test_pre_post_and_reversed_teams_rejected(self):
        for s in [self.sample('pre'),self.sample('post'),self.sample(home='B',away='A'),self.sample(home='a')]:
            self.assertEqual(coverage(s)['exact_name_candidates'],[])
    def test_duplicate_provider_identity_is_ambiguous(self):
        s=self.sample();s['sources'][0]['fixtures']*=2
        self.assertEqual(coverage(s)['exact_name_candidates'],[])
    def test_error_retained(self):
        self.assertEqual(coverage({'sources':[{'name':'espn','error_type':'TimeoutError'}]})['source_errors'],['espn'])
