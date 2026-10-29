"""Budget-to-probe composition; synthetic failures, no network or DB."""
import json
import unittest
from unittest.mock import MagicMock, patch
import research_probe
from probe_budget import PostgresProbeBudget

ID = '151f046a-6621-4bb2-9f8a-9bfb6ff08400'
RAW = json.dumps({'request_id': ID}).encode()


class CompositionTests(unittest.TestCase):
    def test_connection_failure_denies_capture(self):
        connect = MagicMock(side_effect=RuntimeError('secret URL placeholder'))
        self.check_denied(PostgresProbeBudget(connect))

    def check_denied(self, backend):
        with patch.dict('os.environ', PICKNOW_ENABLE_ODDIZE_PROBE='1',
                        PICKNOW_ODDIZE_API_KEY='synthetic-key'), \
             patch.object(research_probe, 'RESERVE', backend), \
             patch.object(research_probe, 'capture') as capture:
            code, result = research_probe.run(RAW)
        self.assertEqual(code, 503)
        self.assertEqual(result['status'], 'budget_store_unavailable')
        self.assertFalse(result['approved_for_picks'])
        self.assertNotIn('secret', json.dumps(result))
        capture.assert_not_called()

    def test_commit_failure_denies_capture(self):
        connect = MagicMock()
        conn = connect.return_value.__enter__.return_value
        conn.cursor.return_value.__enter__.return_value.fetchone.return_value = (ID,)
        conn.commit.side_effect = RuntimeError('secret commit detail')
        self.check_denied(PostgresProbeBudget(connect))
        conn.commit.assert_called_once()

    def test_context_exit_failure_denies_capture(self):
        connect = MagicMock()
        conn = connect.return_value.__enter__.return_value
        conn.cursor.return_value.__enter__.return_value.fetchone.return_value = (ID,)
        connect.return_value.__exit__.side_effect = RuntimeError('secret close detail')
        self.check_denied(PostgresProbeBudget(connect))


if __name__ == '__main__':
    unittest.main()
