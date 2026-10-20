import unittest
from app import check

class FailClosedTests(unittest.TestCase):
    def test_unknown_period_and_forged_model_never_unlock(self):
        data = {'model_status': 'validated', 'matches': [{'in_play': True, 'quotes': [
            {'market_name': label, 'handicap': -4.5, 'odds_dec': 1.9}
            for label in ['Handicap', 'Full Game Handicap', '1Q Spread', 'Half Spread']]}]}
        result = check(lambda: data)
        self.assertEqual(result['quotes_seen'], 4)
        self.assertEqual(result['verified_market_count'], 0)
        self.assertEqual(result['picks'], [])
        self.assertEqual(result['model_status'], 'not_validated')

    def test_bad_schema_and_feed_failure(self):
        for data in [None, [], {'matches': None}, {'matches': 'wrong'}]:
            result = check(lambda: data)
            self.assertEqual(result['validation_status'], 'failed')
            self.assertEqual(result['recommendation'], 'NO BET')
        def fail():
            raise TimeoutError()
        self.assertEqual(check(fail)['picks'], [])

if __name__ == '__main__':
    unittest.main()
