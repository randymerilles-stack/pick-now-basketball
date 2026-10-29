"""Offline HTTP status diagnostics, without error-body/credential disclosure."""
import io
import json
import unittest
from unittest.mock import patch
from urllib.error import HTTPError
from audit_dual_scoreboard import fetch


class ErrorCaptureTests(unittest.TestCase):
    def test_http_status_is_preserved_without_body(self):
        for status in (403, 404, 429, 503):
            error=HTTPError('https://example.org/data',status,'private exception text',{},
                            io.BytesIO(b'private rejected body'))
            with patch('audit_dual_scoreboard.urlopen',side_effect=error):
                row=fetch(('test','https://example.org/data'))
            self.assertEqual(row['http_status'],status)
            self.assertEqual(row['error_stage'],'http_status')
            self.assertNotIn('response',row)
            self.assertNotIn('private',json.dumps(row))
            self.assertIsNotNone(row['received_at'])

    def test_network_failure_does_not_invent_status(self):
        with patch('audit_dual_scoreboard.urlopen',side_effect=TimeoutError('private timeout text')):
            row=fetch(('test','https://example.org/data'))
        self.assertNotIn('http_status',row)
        self.assertEqual(row['error_stage'],'request')
        self.assertNotIn('private',json.dumps(row))


if __name__=='__main__':
    unittest.main()
