import unittest
from paired_capture import collect, project, source_urls


class PairedTests(unittest.TestCase):
    def test_explicit_different_schedule_dates_and_metadata(self):
        urls = source_urls('2026-10-23', '2026-10-24')
        self.assertTrue(urls['espn_nba'].endswith('20261023'))
        self.assertTrue(urls['espn_nbl'].endswith('20261024'))
        def reader(item): return {'name':item[0],'url':item[1]}
        result = collect('2026-10-23', reader, nbl_day='2026-10-24')
        self.assertEqual(result['requested_nbl_date'], '2026-10-24')
        self.assertFalse(result['approved_for_picks'])
        with self.assertRaises(ValueError): source_urls('2026-10-23','2026-02-30')

    def test_provider_projection_cannot_mutate_source_evidence(self):
        row = {'name':'provider','response':{'matches':[{'stats':{'period':2},'group_status':{'112':{'stale':False}},'quotes':[{'group_id':'112','odds_dec':1.9},{'group_id':'1'}]}]}}
        from copy import deepcopy
        original = deepcopy(row)
        result = project(row)
        result['fixtures'][0]['stats']['period'] = 4
        result['fixtures'][0]['quotes'][0]['odds_dec'] = 9
        result['fixtures'][0]['group_status']['112']['stale'] = True
        self.assertEqual(row, original)
        self.assertEqual(len(result['fixtures'][0]['quotes']),1)

    def test_scoreboard_projection_cannot_mutate_source_evidence(self):
        row = {'name':'espn_nba','response':{'events':[{'status':{'period':2},'competitions':[{'competitors':[{'team':{'id':'t','displayName':'A'},'score':'10'}]}]}]}}
        from copy import deepcopy
        original = deepcopy(row)
        result = project(row)
        result['events'][0]['status']['period'] = 4
        result['events'][0]['competitions'][0]['competitors'][0]['team']['displayName'] = 'B'
        self.assertEqual(row,original)

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
