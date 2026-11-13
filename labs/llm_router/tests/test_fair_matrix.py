"""Comparator must never reward missing evidence or a vulnerable gateway."""
import json
import tempfile
import unittest
from pathlib import Path

from labs.llm_router.fair_matrix import (
    CANDIDATES, FUNCTIONAL_GATES, classify, evaluate,
)


class FairMatrixTests(unittest.TestCase):
    def test_unchecked_mandatory_not_a_pass(self):
        checks = {key: "pass" for key in FUNCTIONAL_GATES}
        checks["free_provider_fallback"] = "not_tested"
        self.assertEqual(classify("gomodel", checks, "not_tested"),
                         "insufficient_evidence")

    def test_unsupported_not_equivalent_to_unchecked(self):
        checks = {key: "pass" for key in FUNCTIONAL_GATES}
        checks["explicit_paid_only"] = "unsupported"
        self.assertEqual(classify("gomodel", checks, "not_tested"),
                         "incomplete_or_failed_functional_gate")

    def test_known_security_failure_vetoes_functional_pass(self):
        checks = {key: "pass" for key in FUNCTIONAL_GATES}
        self.assertEqual(classify("portkey", checks, "fail"),
                         "blocked_known_security_failure")

    def test_even_all_synthetic_passes_are_not_production_approval(self):
        checks = {key: "pass" for key in FUNCTIONAL_GATES}
        self.assertEqual(classify("bifrost", checks, "not_tested"),
                         "functional_only_not_production_approved")

    def test_missing_report_does_not_get_assumed_success(self):
        with tempfile.TemporaryDirectory() as directory:
            report = evaluate(Path(directory))
        self.assertFalse(report["deployment_approved"])
        self.assertFalse(report["execution_complete"])
        self.assertIsNone(report["winner"])
        self.assertEqual(set(report["candidates"]), set(CANDIDATES))
        self.assertEqual(report["candidates"]["gomodel"]["functional"]["free_provider_fallback"], "not_tested")
        self.assertEqual(report["candidates"]["portkey"]["security"], "fail")
        self.assertEqual(
            report["candidates"]["portkey"]["eligibility"],
            "blocked_known_security_failure",
        )


if __name__ == "__main__":
    unittest.main()
