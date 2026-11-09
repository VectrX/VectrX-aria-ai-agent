import http.client
import json
import os
import threading
import unittest
from http.server import ThreadingHTTPServer
from unittest.mock import patch

from aria import Handler, SYSTEM_PROMPT


class AriaTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        cls.port = cls.server.server_address[1]
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()

    def request(self, method, path, data=None, token=None):
        connection = http.client.HTTPConnection("127.0.0.1", self.port, timeout=5)
        headers = {"Content-Type": "application/json"}
        if token is not None:
            headers["Authorization"] = f"Bearer {token}"
        connection.request(method, path, body=json.dumps(data) if data is not None else None, headers=headers)
        response = connection.getresponse()
        result = response.status, json.loads(response.read())
        connection.close()
        return result

    def test_health(self):
        status, body = self.request("GET", "/health")
        self.assertEqual(status, 200)
        self.assertEqual(body["status"], "ok")

    def test_chat_requires_authorization(self):
        with patch.dict(os.environ, {"ARIA_ADMIN_TOKEN": "test-secret"}):
            status, _ = self.request("POST", "/api/chat", {"message": "Hi"})
            self.assertEqual(status, 401)

    def test_chat_mocked_provider(self):
        with patch.dict(os.environ, {"ARIA_ADMIN_TOKEN": "test-secret"}):
            with patch("aria.generate_reply", return_value="Hello MAVRO"):
                status, body = self.request("POST", "/api/chat", {"message": "Hi"}, "test-secret")
                self.assertEqual(status, 200)
                self.assertEqual(body["reply"], "Hello MAVRO")

    def test_invalid_message(self):
        with patch.dict(os.environ, {"ARIA_ADMIN_TOKEN": "test-secret"}):
            status, _ = self.request("POST", "/api/chat", {"message": ""}, "test-secret")
            self.assertEqual(status, 400)

    def test_agent_does_not_claim_unverified_execution(self):
        self.assertIn("verified tool evidence", SYSTEM_PROMPT)


if __name__ == "__main__":
    unittest.main()
