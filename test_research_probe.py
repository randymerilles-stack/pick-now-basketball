"""Synthetic private-probe policy/HTTP tests. No actual keys, ledger or API."""
from contextlib import ExitStack
from http.client import HTTPConnection
from http.server import ThreadingHTTPServer
import json
import threading
import unittest
from unittest.mock import Mock, patch
import app
import research_probe

REQUEST_ID='00000000-0000-4000-8000-000000000001'
RAW=json.dumps({'request_id':REQUEST_ID}).encode()


class PolicyTests(unittest.TestCase):
    def setUp(self):
        self.stack=ExitStack();self.addCleanup(self.stack.close)
        self.stack.enter_context(patch.dict('os.environ',{
            'PICKNOW_ENABLE_ODDIZE_PROBE':'1','PICKNOW_ODDIZE_API_KEY':'synthetic-secret'}))
        self.capture=self.stack.enter_context(patch('research_probe.capture',return_value={
            'status':'captured_research_only','events':[],'unexpected_secret':'synthetic-secret'}))

    def test_disabled_flag_is_exact(self):
        for value in ('','0','true','yes'):
            with patch.dict('os.environ',{'PICKNOW_ENABLE_ODDIZE_PROBE':value}):
                self.assertEqual(research_probe.run(RAW)[0],404)
        self.capture.assert_not_called()

    def test_unconfigured_durable_budget_blocks_even_with_key(self):
        with patch('research_probe.RESERVE',None):
            code,result=research_probe.run(RAW)
        self.assertEqual(code,503)
        self.assertEqual(result['status'],'durable_budget_not_configured')
        self.capture.assert_not_called()

    def test_missing_source_key_does_not_reserve(self):
        with patch.dict('os.environ',{'PICKNOW_ODDIZE_API_KEY':''}),patch('research_probe.RESERVE') as reserve:
            self.assertEqual(research_probe.run(RAW)[0],503)
            reserve.assert_not_called()

    def test_bad_request_schemas_do_not_consume_budget(self):
        samples=[b'{}',b'[]',b'null',b'bad-json',b'\xff',
            json.dumps({'request_id':REQUEST_ID,'key':'injection'}).encode(),
            json.dumps({'request_id':'not-uuid'}).encode(),
            ('{"request_id":"'+REQUEST_ID+'","request_id":"'+REQUEST_ID+'"}').encode()]
        with patch('research_probe.RESERVE') as reserve:
            for raw in samples:self.assertEqual(research_probe.run(raw)[0],400)
            reserve.assert_not_called()
        self.capture.assert_not_called()

    def test_replay_exhaustion_unknown_and_store_error_fail_closed(self):
        for value,code in [('already_used',409),('exhausted',429),('unknown',503)]:
            with patch('research_probe.RESERVE',return_value=value):
                self.assertEqual(research_probe.run(RAW)[0],code)
        with patch('research_probe.RESERVE',side_effect=RuntimeError('synthetic-secret')):
            code,result=research_probe.run(RAW)
        self.assertEqual(code,503);self.assertNotIn('synthetic-secret',json.dumps(result))
        self.capture.assert_not_called()

    def test_single_reserved_capture_is_research_only_and_filtered(self):
        with patch('research_probe.RESERVE',return_value='reserved') as reserve:
            code,result=research_probe.run(RAW)
        reserve.assert_called_once_with(REQUEST_ID);self.capture.assert_called_once_with()
        self.assertEqual(code,200)
        self.assertFalse(result['approved_for_picks'])
        self.assertFalse(result['capture']['training_eligible'])
        self.assertNotIn('synthetic-secret',json.dumps(result))

    def test_source_failure_does_not_release_or_retry_reservation(self):
        self.capture.side_effect=RuntimeError('synthetic-secret')
        with patch('research_probe.RESERVE',return_value='reserved') as reserve:
            code,result=research_probe.run(RAW)
        self.assertEqual(code,502);reserve.assert_called_once();self.capture.assert_called_once()
        self.assertNotIn('synthetic-secret',json.dumps(result))


class QuietHandler(app.Handler):
    def log_message(self,*args):pass


class HttpTests(unittest.TestCase):
    def request(self,*,authenticated=True,origin='https://example.test',body=RAW,
                content_type='application/json',method='POST'):
        with ExitStack() as stack:
            stack.enter_context(patch.dict('os.environ',{'PICKNOW_ENABLE_ODDIZE_PROBE':'1',
                'PICKNOW_ODDIZE_API_KEY':'synthetic-secret','PICKNOW_ORIGIN':'https://example.test'}))
            stack.enter_context(patch('app.access.configured',return_value=True))
            stack.enter_context(patch('app.access.authenticated',return_value=authenticated))
            reserve=stack.enter_context(patch('research_probe.RESERVE',return_value='reserved'))
            capture=stack.enter_context(patch('research_probe.capture',return_value={
                'status':'captured_research_only','events':[]}))
            server=ThreadingHTTPServer(('127.0.0.1',0),QuietHandler)
            thread=threading.Thread(target=server.serve_forever,kwargs={'poll_interval':.01},daemon=True)
            thread.start()
            try:
                connection=HTTPConnection('127.0.0.1',server.server_port,timeout=3)
                try:
                    connection.request(method,'/api/research/oddize',body=body,
                        headers={'Origin':origin,'Content-Type':content_type})
                    response=connection.getresponse();code=response.status;raw=response.read()
                finally:connection.close()
            finally:server.shutdown();server.server_close();thread.join(timeout=3)
            calls=(reserve.call_count,capture.call_count)
        self.assertNotIn(b'synthetic-secret',raw)
        return code,calls

    def test_wrong_origin_and_missing_session_cannot_reserve(self):
        self.assertEqual(self.request(origin='https://wrong.example'),(403,(0,0)))
        self.assertEqual(self.request(authenticated=False),(401,(0,0)))

    def test_owner_post_with_durable_reservation_makes_one_mock_call(self):
        self.assertEqual(self.request(),(200,(1,1)))

    def test_wrong_method_type_size_and_schema_never_call_source(self):
        for options,code in [(dict(method='GET'),404),(dict(content_type='text/plain'),415),
                             (dict(body=b'x'*257),400),(dict(body=b'{}'),400)]:
            with self.subTest(options=options):self.assertEqual(self.request(**options),(code,(0,0)))


if __name__=='__main__':unittest.main()
