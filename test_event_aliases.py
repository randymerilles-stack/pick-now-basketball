import unittest
from event_aliases import provider_aliases


class AliasTests(unittest.TestCase):
    def test_explicit_aliases_and_single_id(self):
        self.assertEqual(provider_aliases('20', {'fixture_id':'20',
            'fixture_ids':['20','10'], 'prematch_id':'10'}), ('10','20'))
        self.assertEqual(provider_aliases('20', {'fixture_id':'20',
            'fixture_ids':['20']}), ('20',))

    def test_no_guessing_from_names_or_missing_declarations(self):
        for response in (None, {}, {'fixture_id':'20'},
                         {'home':'A', 'away':'B', 'fixture_ids':['10'], 'fixture_id':'10'}):
            self.assertIsNone(provider_aliases('20', response))

    def test_invalid_or_conflicting_ids(self):
        base = {'fixture_id':'20', 'fixture_ids':['20','10']}
        for ids in ([], ['20','20'], ['20',10], ['20',True], ['20',''], ['20','２１']):
            self.assertIsNone(provider_aliases('20', dict(base, fixture_ids=ids)))
        self.assertIsNone(provider_aliases('20', dict(base, fixture_id='30')))
        self.assertIsNone(provider_aliases('20', dict(base, prematch_id='30')))
        for requested in (20, True, '', '２０'):
            self.assertIsNone(provider_aliases(requested, base))


if __name__ == '__main__':
    unittest.main()
