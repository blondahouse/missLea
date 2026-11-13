"""Safety probe classifier invariants. No real network destinations or keys."""
import unittest

from labs.llm_router.security_suite import (
    CASES, delta, total_calls, verdict, request,
)


def ev(**kwargs):
    values = {"primary": [], "backup": [], "paid": [], "forbidden": []}
    values.update(kwargs)
    return values


class SecuritySuiteTests(unittest.TestCase):
    def test_same_negative_scenarios_are_required_for_all(self):
        self.assertEqual(len(CASES), 16)

    def test_missing_auth_reaching_upstream_is_failure(self):
        self.assertEqual(
            verdict(200, ev(primary=[{"scenario": "LAB_BASIC"}]), "deny")["status"],
            "fail",
        )

    def test_unauthorized_without_upstream_and_with_401_passes_scoped_test(self):
        self.assertEqual(verdict(401, ev(), "deny")["status"], "pass")

    def test_non_authorization_http_error_does_not_count_as_auth_pass(self):
        self.assertEqual(verdict(404, ev(), "deny")["status"], "not_tested")

    def test_paid_canary_must_never_be_called_by_invalid_identity(self):
        self.assertEqual(
            verdict(401, ev(paid=[{"scenario": "LAB_BASIC"}]), "no_paid")["status"],
            "fail",
        )

    def test_redirect_canary_counts_as_failure(self):
        self.assertEqual(
            verdict(200, ev(
                primary=[{"scenario": "LAB_REDIRECT_307"}],
                forbidden=[{"scenario": "LAB_REDIRECT_307"}],
            ), "no_redirect")["status"],
            "fail",
        )

    def test_redirect_not_exercised_remains_unknown(self):
        self.assertEqual(verdict(404, ev(), "no_redirect")["status"], "not_tested")

    def test_forbidden_header_override_reaching_canary_fails(self):
        self.assertEqual(
            verdict(200, ev(forbidden=[{"scenario": "LAB_BASIC"}]), "no_forbidden")["status"],
            "fail",
        )

    def test_total_calls_is_instrumented(self):
        self.assertEqual(total_calls(ev(primary=[{}], forbidden=[{}])), 2)

    def test_refuses_external_url(self):
        with self.assertRaises(ValueError):
            request("GET", "https://example.com/")

    def test_client_does_not_follow_gateway_redirects(self):
        from labs.llm_router.security_suite import NoRedirect
        self.assertIsNone(NoRedirect().redirect_request(None, None, 307, "", {}, "http://127.0.0.1:19103"))


if __name__ == "__main__":
    unittest.main()
