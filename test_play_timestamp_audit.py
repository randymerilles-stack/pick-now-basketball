import unittest
from play_timestamp_audit import audit_play_timestamps as audit


class TimestampTests(unittest.TestCase):
    def sample(self):
        return {'header':{'id':'event'},'wallclockAvailable':True,
                'plays':[{'wallclock':'2026-10-23T10:00:00Z'},
                         {'wallclock':'2026-10-23T10:00:02Z'}]}

    def run_audit(self,s):return audit(s,'event','2026-10-23T11:00:00Z')

    def test_complete_coverage_retains_actual_availability_and_no_approval(self):
        r=self.run_audit(self.sample())
        self.assertTrue(r['complete_ordered_timestamp_coverage'])
        self.assertEqual(r['data_available_no_earlier_than'],'2026-10-23T11:00:00+00:00')
        self.assertFalse(r['training_eligible']);self.assertFalse(r['approved_for_picks'])

    def test_flag_alone_is_not_timestamp_evidence(self):
        s=self.sample();s['plays']=[{},{}]
        r=self.run_audit(s);self.assertEqual(r['missing_timestamp_count'],2)
        self.assertFalse(r['complete_ordered_timestamp_coverage'])

    def test_naive_invalid_future_and_missing_time_are_separate(self):
        s=self.sample();s['plays']=[{'wallclock':v} for v in (
            '2026-10-23T10:00:00','invalid','2026-10-23T12:00:00Z',None)]
        r=self.run_audit(s)
        self.assertEqual(r['invalid_timestamp_count'],2)
        self.assertEqual(r['future_timestamp_count'],1)
        self.assertEqual(r['missing_timestamp_count'],1)

    def test_out_of_order_timestamps_not_silently_sorted(self):
        s=self.sample();s['plays'].reverse()
        r=self.run_audit(s);self.assertEqual(r['backward_timestamp_transitions'],1)
        self.assertFalse(r['complete_ordered_timestamp_coverage'])

    def test_wrong_identity_undeclared_and_empty_rejected(self):
        s=self.sample();s['header']['id']='another'
        self.assertFalse(self.run_audit(s)['complete_ordered_timestamp_coverage'])
        s=self.sample();s['wallclockAvailable']=1
        self.assertFalse(self.run_audit(s)['complete_ordered_timestamp_coverage'])
        s=self.sample();s['plays']=[]
        self.assertFalse(self.run_audit(s)['complete_ordered_timestamp_coverage'])


if __name__=='__main__':unittest.main()
