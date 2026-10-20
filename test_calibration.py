import unittest
from datetime import datetime, timedelta, timezone
from calibration import audit, split

class CalibrationTests(unittest.TestCase):
    def test_overlapping_outcomes_not_used_to_train(self):
        rows=[{'fixture_id':str(i),'decision_at':f'2026-10-19T{10+i:02}:00:00Z',
               'finished_at':'2026-10-19T23:00:00Z'} for i in range(10)]
        train,test=split(rows)
        self.assertEqual(train,[])
        self.assertEqual(len(test),3)
        self.assertFalse(audit(rows)['trained'])
    def test_good_research_fit_does_not_approve_live_picks(self):
        base=datetime(2024,1,1,tzinfo=timezone.utc)
        rows=[dict(fixture_id=str(i),league='Synthetic software test',
                   decision_at=(base+timedelta(days=i)).isoformat(),
                   finished_at=(base+timedelta(days=i,hours=2)).isoformat(),
                   market_home_probability=.5,home_covered=int(i%10<7))
              for i in range(500)]
        result=audit(rows)
        self.assertTrue(result['trained'])
        self.assertLess(result['model_brier'],result['market_brier'])
        self.assertFalse(result['approved_for_picks'])
    def test_duplicate_fixture_is_rejected(self):
        row={'fixture_id':'same','decision_at':'2026-10-19T10:00:00Z','finished_at':'2026-10-19T11:00:00Z'}
        with self.assertRaises(ValueError):split([row,row])

if __name__=='__main__':unittest.main()
