"""Mock provider semantics and benchmark bookkeeping, without any LLM API."""
import json
import threading
import unittest
from urllib.error import HTTPError
from urllib.request import Request, urlopen

from router_lab.mock_provider import Handler, LabServer


def req(base, path, data=None):
    body = None if data is None else json.dumps(data).encode()
    request = Request(base + path, data=body, headers={"Content-Type": "application/json"})
    try:
        with urlopen(request, timeout=3) as response:
            return response.status, json.load(response)
    except HTTPError as error:
        return error.code, json.load(error)


class MockProviderTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.servers = []
        for tier in ("primary", "backup", "paid"):
            server = LabServer(("127.0.0.1", 0), Handler, tier)
            thread = threading.Thread(target=server.serve_forever, daemon=True)
            thread.start()
            cls.servers.append((server, thread))
        cls.urls = {
            tier: f"http://127.0.0.1:{server.server_address[1]}"
            for tier, (server, _) in zip(("primary", "backup", "paid"), cls.servers)
        }

    @classmethod
    def tearDownClass(cls):
        for server, thread in cls.servers:
            server.shutdown()
            thread.join(timeout=3)
            server.server_close()

    def send(self, tier, marker):
        return req(self.urls[tier], "/v1/chat/completions", {
            "model": "lab-model", "messages": [
                {"role": "user", "content": marker}
            ]
        })

    def test_success_and_deterministic_marker(self):
        status, body = self.send("primary", "LAB_BASIC")
        self.assertEqual(status, 200)
        self.assertEqual(body["choices"][0]["message"]["content"], "mock:primary")

    def test_quota_only_on_primary(self):
        self.assertEqual(self.send("primary", "LAB_QUOTA")[0], 429)
        self.assertEqual(self.send("backup", "LAB_QUOTA")[0], 200)

    def test_outage_never_disables_paid_mock(self):
        self.assertEqual(self.send("primary", "LAB_OUTAGE")[0], 503)
        self.assertEqual(self.send("backup", "LAB_OUTAGE")[0], 503)
        self.assertEqual(self.send("paid", "LAB_OUTAGE")[0], 200)

    def test_events_can_be_inspected_and_reset(self):
        self.send("paid", "LAB_BASIC")
        _, state = req(self.urls["paid"], "/lab/events")
        self.assertTrue(state["events"])
        req(self.urls["paid"], "/lab/reset", {})
        _, state = req(self.urls["paid"], "/lab/events")
        self.assertEqual(state["events"], [])

    def test_model_catalog_and_embedding(self):
        _, models = req(self.urls["primary"], "/v1/models")
        self.assertIn("lab-model", [x["id"] for x in models["data"]])
        status, data = req(self.urls["primary"], "/v1/embeddings", {
            "model": "lab-embed", "input": "LAB_EMBED",
        })
        self.assertEqual(status, 200)
        self.assertEqual(data["data"][0]["embedding"], [0.1, 0.2, 0.3])


if __name__ == "__main__":
    unittest.main()
