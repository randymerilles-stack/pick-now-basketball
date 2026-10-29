"""Real local HTTP handler checks; no production credentials or external calls."""
from contextlib import ExitStack
from http.client import HTTPConnection
from http.server import ThreadingHTTPServer
import threading
import unittest
from unittest.mock import patch
import app


class QuietHandler(app.Handler):
    def log_message(self, *args):
        pass


class ResearchBoundaryTests(unittest.TestCase):
    def request(self, method, path, authenticated):
        with ExitStack() as stack:
            stack.enter_context(patch.dict('os.environ', {
                'PICKNOW_ODDIZE_API_KEY':'synthetic-secret', 'PICKNOW_ORIGIN':'https://example.test',
                'PICKNOW_ENABLE_ODDIZE_PROBE':'0'}))
            stack.enter_context(patch('app.access.configured', return_value=True))
            stack.enter_context(patch('app.access.authenticated', return_value=authenticated))
            check=stack.enter_context(patch('app.check', side_effect=AssertionError('unexpected feed call')))
            odds=stack.enter_context(patch('oddize_capture.capture', side_effect=AssertionError('unexpected key use')))
            server=ThreadingHTTPServer(('127.0.0.1',0),QuietHandler)
            thread=threading.Thread(target=server.serve_forever, kwargs={'poll_interval':.01}, daemon=True)
            thread.start()
            try:
                connection=HTTPConnection('127.0.0.1',server.server_port,timeout=3)
                try:
                    connection.request(method,path,headers={'Origin':'https://example.test'})
                    response=connection.getresponse()
                    result=(response.status,response.read())
                finally:
                    connection.close()
            finally:
                server.shutdown();server.server_close();thread.join(timeout=3)
            check.assert_not_called();odds.assert_not_called()
        self.assertNotIn(b'synthetic-secret',result[1])
        return result

    def test_source_probe_requires_auth_and_is_not_a_current_route(self):
        self.assertEqual(self.request('GET','/api/research/oddize',False)[0],401)
        self.assertEqual(self.request('GET','/api/research/oddize',True)[0],404)

    def test_post_does_not_activate_research_when_key_exists(self):
        self.assertEqual(self.request('POST','/api/research/oddize',True)[0],404)

    def test_head_and_health_do_not_call_odds_api(self):
        self.assertEqual(self.request('HEAD','/api/research/oddize',True),(404,b''))
        self.assertEqual(self.request('GET','/health',False)[0],200)


if __name__=='__main__':
    unittest.main()
