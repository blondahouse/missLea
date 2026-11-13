"""Fairness metric invariants, not fabricated provider measurements."""
import unittest

from labs.llm_router.fair_latency import percentile, run


class FairLatencyTests(unittest.TestCase):
    def test_nearest_rank(self):
        self.assertEqual(percentile(list(range(1, 41)), 95), 38)
        self.assertEqual(percentile(list(range(1, 41)), 50), 20)

    def test_empty_invalid(self):
        with self.assertRaises(ValueError):
            percentile([], 95)

    def test_external_url_refused(self):
        with self.assertRaises(ValueError):
            run("litellm", "https://api.example.com", "x")

    def test_minimal_sample_count(self):
        with self.assertRaises(ValueError):
            run("litellm", "http://127.0.0.1:4000", "x", measured=1)


if __name__ == "__main__":
    unittest.main()
