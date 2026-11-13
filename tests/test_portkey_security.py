"""Classifier tests; all probes use synthetically fabricated response codes."""
import unittest

from router_lab.portkey_security import diagnose


class SSRFClassifierTests(unittest.TestCase):
    def test_bypass_is_blocked_for_production(self):
        self.assertTrue(diagnose(400, 0, 200, 1).startswith("VULNERABLE"))

    def test_protected_legacy_route(self):
        self.assertTrue(diagnose(400, 0, 403, 0).startswith("NOT_REPRODUCED"))

    def test_normal_route_must_reject_test_target(self):
        self.assertTrue(diagnose(200, 1, 200, 1).startswith("INCONCLUSIVE"))

    def test_zero_network_hits_with_legacy_success_is_inconclusive(self):
        self.assertTrue(diagnose(400, 0, 200, 0).startswith("INCONCLUSIVE"))


if __name__ == "__main__":
    unittest.main()
