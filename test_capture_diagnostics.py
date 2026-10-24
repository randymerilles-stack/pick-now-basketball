import unittest
from unittest.mock import patch
from audit_dual_scoreboard import fetch

class Response:
    status=200
    headers={}
    def __init__(self, raw): self.raw=raw
    def __enter__(self): return self
    def __exit__(self,*args): pass
    def read(self,n): return self.raw[:n]

class DiagnosticTests(unittest.TestCase):
    def test_size_and_json_failures_are_distinct_without_body(self):
        for raw,stage in [(b'x'*3000001,'payload_size'),(b'private-invalid-json','json_decode')]:
            with patch('audit_dual_scoreboard.urlopen',return_value=Response(raw)):
                r=fetch(('test','https://example.com'))
            self.assertEqual(r['error_stage'],stage)
            self.assertNotIn('response',r)
            self.assertNotIn('private-invalid-json',str(r))
    def test_transport_failure_is_sanitized(self):
        with patch('audit_dual_scoreboard.urlopen',side_effect=TimeoutError('secret')):
            r=fetch(('test','https://example.com'))
        self.assertEqual(r['error_stage'],'request')
        self.assertNotIn('secret',str(r))
