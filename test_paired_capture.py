import unittest
from paired_capture import collect, project, source_urls


class PairedTests(unittest.TestCase):
    def test_calendar_validation(self):
        self.assertIn('20261023', source_urls('2026-10-23')['espn_nba'])
        with self.assertRaises(ValueError): source_urls('2026-02-30')

    def test_preserves_raw_state_without_inferred_period(self):
        r = project({'name': 'provider', 'sha256': 'abc', 'received_at': 'now', 'response': {'matches': [{'id': 1, 'clock': '3:00', 'score': '10-9', 'quotes': [{'group_id': '112'}]}]}})
        self.assertIsNone(r['fixtures'][0]['period'])
        self.assertEqual(r['fixtures'][0]['quotes'], [{'group_id': '112'}])
        self.assertEqual(r['sha256'], 'abc')

    def test_partial_failure_never_promoted(self):
        def reader(item):
            return {'name': item[0], 'url': item[1], 'error_type': 'TimeoutError'}
        r = collect('2026-10-23', reader)
        self.assertEqual(len(r['sources']), 3)
        self.assertFalse(r['training_eligible'])
        self.assertFalse(r['approved_for_picks'])
        self.assertFalse(r['identity_mapping_verified'])
