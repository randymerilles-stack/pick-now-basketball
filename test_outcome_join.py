import copy
import unittest
from outcome_join import join_outcome


class OutcomeTests(unittest.TestCase):
    def setUp(self):
        self.o={'fixture_id':'1','home':'A','away':'B','league':'L',
                'quotes':[{'team':'A','line':-2.5,'odds':1.9},{'team':'B','line':2.5,'odds':1.9}]}
        self.r={'fixture_id':'1','home':'A','away':'B','league':'L','sport':'basketball',
                'status':'finished','final_score':'80-75','finished_at':'2026-10-20T14:00:00Z'}
    def run_join(self,results=None):
        return join_outcome(self.o,'2026-10-20T13:00:00Z',[self.r] if results is None else results,'2026-10-20T14:10:00Z')
    def test_both_sides_and_actual_availability(self):
        r=self.run_join();self.assertEqual([v['covered'] for v in r['labels']],[1,0])
        self.assertEqual(r['outcome_available_at'],'2026-10-20T14:10:00+00:00')
        self.assertFalse(r['training_eligible']);self.assertFalse(r['approved_for_picks'])
    def test_duplicate_and_missing_results_are_unlabelled(self):
        for rows in [[],[self.r,self.r]]:self.assertEqual(self.run_join(rows)['labels'],[])
    def test_identity_status_and_tied_score(self):
        for key,value in [('home','B'),('league','Other'),('sport','ebasketball'),('status','unknown'),('final_score','75-75')]:
            original=copy.deepcopy(self.r);self.r[key]=value
            self.assertEqual(self.run_join()['labels'],[]);self.r=original
    def test_chronology_naive_future_and_predecision(self):
        for key,value in [('finished_at','2026-10-20T12:00:00Z'),('finished_at','2026-10-20T15:00:00Z'),('finished_at','2026-10-20T14:00:00'),('updated_at','2026-10-20T15:00:00Z')]:
            original=copy.deepcopy(self.r);self.r[key]=value
            self.assertEqual(self.run_join()['labels'],[]);self.r=original
    def test_push_is_not_a_binary_loss(self):
        self.o['quotes'][0]['line']=-5;self.o['quotes'][1]['line']=5
        labels=self.run_join()['labels'];self.assertEqual([v['cover_result'] for v in labels],['push','push'])
        self.assertTrue(all(v['covered'] is None for v in labels))
    def test_bad_lines_and_nonfinite_odds_fail_closed(self):
        for key,value in [('line',float('nan')),('line',True),('odds',float('inf')),('odds',1)]:
            original=copy.deepcopy(self.o);self.o['quotes'][0][key]=value
            self.assertEqual(self.run_join()['labels'],[]);self.o=original
    def test_inputs_not_mutated(self):
        before=copy.deepcopy((self.o,self.r));self.run_join();self.assertEqual((self.o,self.r),before)


if __name__=='__main__':unittest.main()
