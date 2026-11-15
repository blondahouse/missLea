"""Offline-only manual dispatcher tests; never call the Cloudflare network."""
from __future__ import annotations

import io
import json
import unittest
from urllib.error import HTTPError

from labs.security.dispatch import submit, valid_endpoint


SECRET = "A" * 48
URL = "https://late-glade-5dde.misslea931.workers.dev/run"


class FakeResponse:
    def __init__(self, body: dict, status: int = 200):
        self.status = status
        self._body = json.dumps(body).encode("utf-8")

    def __enter__(self):
        return self

    def __exit__(self, *_):
        pass

    def read(self, length):
        return self._body[:length]


class FakeOpener:
    def __init__(self, response=None, error=None):
        self.response = response
        self.error = error
        self.request = None

    def open(self, request, timeout=None):
        self.request = request
        assert timeout == 15
        if self.error:
            raise self.error
        return self.response


class ManualDispatchTests(unittest.TestCase):
    def test_url_allowlist_requires_https_and_exact_path(self):
        self.assertTrue(valid_endpoint(URL))
        for bad in (
            "http://late-glade.misslea931.workers.dev/run",
            "https://evil.tld/run",
            "https://misslea931.workers.dev.evil.tld/run",
            "https://a.workers.dev/admin",
            "https://a.workers.dev/run?secret=x",
            "https://x:token@a.workers.dev/run",
            "https://a.workers.dev:8080/run",
        ):
            with self.subTest(bad=bad):
                self.assertFalse(valid_endpoint(bad))

    def test_real_request_requires_secret_and_matches_expected_answer(self):
        opener = FakeOpener(FakeResponse({
            "status": "ok", "result": {"count": 3, "sum": 10, "squares": 38}
        }))
        result = submit(URL, SECRET, [2, 3, 5], opener=opener)
        self.assertEqual(result["status"], "PASS")
        self.assertEqual(opener.request.get_header("Authorization"), "Bearer " + SECRET)
        self.assertEqual(json.loads(opener.request.data)["task"], "sum_squares")
        self.assertNotIn(SECRET, json.dumps(result))

    def test_invalid_request_cannot_invoke_network(self):
        for token, numbers in (("short", [1]), (SECRET, []),
                               (SECRET, list(range(17))), (SECRET, [2.5]),
                               (SECRET, [1001]), (SECRET, [True])):
            opener = FakeOpener()
            with self.subTest(token=token[:2], numbers=numbers), self.assertRaises(ValueError):
                submit(URL, token, numbers, opener=opener)
            self.assertIsNone(opener.request)

    def test_mismatch_fails_closed(self):
        opener = FakeOpener(FakeResponse({
            "status": "ok", "result": {"count": 3, "sum": 100, "squares": 38}
        }))
        with self.assertRaises(RuntimeError):
            submit(URL, SECRET, [2, 3, 5], opener=opener)

    def test_error_body_not_exposed(self):
        error = HTTPError(URL, 401, "denied", {}, io.BytesIO(SECRET.encode()))
        with self.assertRaisesRegex(RuntimeError, "HTTP 401") as caught:
            submit(URL, SECRET, [2, 3, 5], opener=FakeOpener(error=error))
        self.assertNotIn(SECRET, str(caught.exception))


if __name__ == "__main__":
    unittest.main()
