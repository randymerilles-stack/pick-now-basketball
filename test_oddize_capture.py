"""Synthetic HTTP responses only; no live key or paid calls."""
import io
import json
import unittest
from unittest.mock import patch
from urllib.error import HTTPError
from oddize_capture import capture, NoRedirect


class Response:
    status = 200
    headers = {'X-Credits-Cost': '1', 'X-Credits-Remaining': '1499'}
    def __enter__(self): return self
    def __exit__(self, *args): pass
    def read(self, count):
        return json.dumps({'events': [{'event_id': 'synthetic', 'sport': 'nba', 'team1': 'A', 'team2': 'B',
                                      'odds': [{'book': 'b365', 'line': -2.5, 'secret_extra': 'excluded'}]}],
                           'unexpected_account_field': 'excluded'}).encode()[:count]


class CaptureTests(unittest.TestCase):
    def test_no_key_no_network(self):
        with patch.dict('os.environ', {}, clear=True), patch('oddize_capture.build_opener') as opener:
            self.assertEqual(capture()['status'], 'missing_api_key')
            opener.assert_not_called()

    def test_success_filters_and_never_prints_key(self):
        with patch.dict('os.environ', {'PICKNOW_ODDIZE_API_KEY': 'synthetic-secret'}), patch('oddize_capture.build_opener') as opener:
            opener.return_value.open.return_value = Response()
            result = capture()
            request = opener.return_value.open.call_args.args[0]
        self.assertEqual(result['status'], 'captured_research_only')
        self.assertNotIn('synthetic-secret', json.dumps(result))
        self.assertNotIn('excluded', json.dumps(result))
        self.assertNotIn('synthetic-secret', request.full_url)
        self.assertFalse(result['training_eligible'])

    def test_http_failures_no_retry_or_error_body(self):
        for status in (302, 401, 429, 503):
            error = HTTPError('https://oddize.com', status, 'synthetic-secret', {}, io.BytesIO(b'private-body'))
            with patch.dict('os.environ', {'PICKNOW_ODDIZE_API_KEY': 'synthetic-secret'}), patch('oddize_capture.build_opener') as opener:
                opener.return_value.open.side_effect = error
                result = capture()
                self.assertEqual(opener.return_value.open.call_count, 1)
            self.assertEqual(result['http_status'], status)
            self.assertNotIn('synthetic-secret', json.dumps(result))
            self.assertNotIn('private-body', json.dumps(result))

    def test_redirect_is_not_followed(self):
        self.assertIsNone(NoRedirect().redirect_request(None, None, 302, '', {}, 'https://other.example'))


if __name__ == '__main__':
    unittest.main()
