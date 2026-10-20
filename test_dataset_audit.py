import copy
import unittest
from dataset_audit import audit_dataset


def capture(fi='1',decision='2026-10-20T12:00:00Z'):
    return {'received_at':decision,'observations':[{'fixture_id':fi,'home':'A','away':'B','league':'L'}]}


def outcome(fi='1',score='80-75',available='2026-10-20T14:00:00Z'):
    return {'joined':[{'fixture_id':fi,'status':'provider_labelled_research_only','final_score':score,
                       'finished_at':'2026-10-20T13:00:00Z','outcome_available_at':available}]}


class DatasetAuditTests(unittest.TestCase):
    def test_repeated_snapshots_and_sides_do_not_inflate_games(self):
        c=capture();c['observations']*=2
        r=audit_dataset([{'captures':[c,c]}],[outcome(),outcome()])
        self.assertEqual(r['observation_rows'],4)
        self.assertEqual(r['provider_labelled_independent_fixtures'],1)
        self.assertFalse(r['training_eligible'])
    def test_identity_and_outcome_conflicts_fail_closed(self):
        c=capture();c['observations'][0]['home']='Other'
        self.assertEqual(audit_dataset([capture(),c],[outcome()])['identity_conflicts'],1)
        self.assertEqual(audit_dataset([capture()],[outcome(),outcome(score='81-75')])['outcome_conflicts'],1)
    def test_train_outcome_must_be_available_before_test_decision(self):
        captures=[capture('1'),capture('2','2026-10-20T12:30:00Z')]
        r=audit_dataset(captures,[outcome('1'),outcome('2')])
        self.assertEqual(r['chronological_diagnostic_train'],0)
        self.assertEqual(r['chronological_diagnostic_test'],1)
        self.assertEqual(r['purged_unavailable_training_outcomes'],1)
    def test_unknown_missing_naive_times_and_input_preservation(self):
        c=capture();original=copy.deepcopy(c)
        self.assertEqual(audit_dataset([c],[])['unlabelled_fixtures'],1)
        self.assertEqual(c,original)
        self.assertEqual(audit_dataset([capture(decision='2026-10-20T12:00:00')],[])['invalid_observations'],1)


if __name__=='__main__':unittest.main()
