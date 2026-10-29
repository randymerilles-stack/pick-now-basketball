import unittest
from unittest.mock import MagicMock
from probe_budget import PostgresProbeBudget, INSERT

ID = 'a51f046a-6621-4bb2-9f8a-9bfb6ff08400'
OTHER = 'b51f046a-6621-4bb2-9f8a-9bfb6ff08400'


class BudgetTests(unittest.TestCase):
    def setup_store(self, rows):
        connect = MagicMock()
        conn = connect.return_value.__enter__.return_value
        cur = conn.cursor.return_value.__enter__.return_value
        cur.fetchone.side_effect = rows
        return PostgresProbeBudget(connect), conn, cur

    def test_commit_before_reserved(self):
        store, conn, cur = self.setup_store([(ID,)])
        self.assertEqual(store(ID), 'reserved')
        conn.commit.assert_called_once()
        self.assertEqual(cur.execute.call_args_list[1].args, (INSERT, (ID,)))

    def test_replay_and_exhaustion(self):
        for winner, expected in [(ID, 'already_used'), (OTHER, 'exhausted')]:
            store, conn, cur = self.setup_store([None, (winner,)])
            self.assertEqual(store(ID), expected)
            conn.commit.assert_called_once()

    def test_commit_failure_never_grants(self):
        store, conn, cur = self.setup_store([(ID,)])
        conn.commit.side_effect = RuntimeError('commit failed')
        with self.assertRaises(RuntimeError):
            store(ID)

    def test_missing_row_and_bad_identity(self):
        store, conn, cur = self.setup_store([None, None])
        with self.assertRaises(RuntimeError):
            store(ID)
        with self.assertRaises(ValueError):
            store('invalid')


if __name__ == '__main__':
    unittest.main()
