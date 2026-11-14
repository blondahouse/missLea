"""Offline service-identity and Cloudflare-shaped lifecycle tests.

Synthetic provider and transport only. Never call real Cloudflare from CI.
"""
from __future__ import annotations

import contextlib
import io
import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from labs.identity import cloudflare_cli
from labs.identity.cloudflare_service import (
    CloudflareAdmissionError, role_guidance, verify_service_identity,
)
from labs.identity.cloudflare_simulation import (
    CloudflareMockBroker, MockCloudflareAccount, MockProviderDenied,
    MockSecretStore, synthetic_lifecycle,
)
from labs.identity.hub import AccessDenied, IdentityHub

ACCOUNT = "a" * 32
TOKEN_ID = "b" * 32
TOKEN = "cfat_SYNTHETIC_DO_NOT_EXPOSE_012345678901234567890"


def response(status="active", token_id=TOKEN_ID):
    return {"success": True, "result": {"id": token_id, "status": status}}


class CloudflareAdmissionTests(unittest.TestCase):
    def test_verified_active_only_not_role_or_ownership(self):
        called = []
        def fake_request(account, token):
            called.append((account, token))
            return response()
        actual = verify_service_identity(account_id=ACCOUNT, token=TOKEN,
                                         request=fake_request, expected_token_id=TOKEN_ID)
        self.assertEqual(actual["admission"], "verified_active_not_scoped")
        self.assertFalse(actual["account_ownership_verified"])
        self.assertFalse(actual["token_permissions_verified"])
        self.assertFalse(actual["legal_account_holder_verified"])
        self.assertEqual(called, [(ACCOUNT, TOKEN)])
        self.assertNotIn(TOKEN, json.dumps(actual))
        self.assertEqual(actual["external_requests"], 1)

    def test_user_owned_token_not_admitted_as_service_identity(self):
        result = verify_service_identity(account_id=ACCOUNT, token="cfut_NOT_FOR_SERVICE",
                                         request=lambda *_: response())
        self.assertEqual(result["admission"], "blocked")
        self.assertEqual(result["token_format_hint"], "user-token-format")

    def test_legacy_format_not_proven_account_owned(self):
        result = verify_service_identity(account_id=ACCOUNT, token="unprefixed-old-test",
                                         request=lambda *_: response())
        self.assertEqual(result["token_format_hint"], "legacy-or-unknown")
        self.assertFalse(result["account_ownership_verified"])

    def test_expected_identity_must_match(self):
        outcome = verify_service_identity(account_id=ACCOUNT, token=TOKEN,
                                          request=lambda *_: response(),
                                          expected_token_id="c" * 32)
        self.assertEqual(outcome["admission"], "blocked")
        self.assertFalse(outcome["expected_token_matches"])

    def test_disabled_expired_and_bad_provider_response_fail_closed(self):
        for state in ("disabled", "expired"):
            with self.subTest(state=state):
                report = verify_service_identity(account_id=ACCOUNT, token=TOKEN,
                                                 request=lambda *_: response(state))
                self.assertEqual(report["admission"], "blocked")
        for payload in ({"success": False}, {"success": True},
                        {"success": True, "result": {"id": "not-a-token-id", "status": "active"}},
                        {"success": True, "result": {"id": TOKEN_ID, "status": "wrong"}}):
            with self.subTest(payload=payload):
                with self.assertRaises(CloudflareAdmissionError):
                    verify_service_identity(account_id=ACCOUNT, token=TOKEN,
                                            request=lambda *_: payload)

    def test_bad_account_or_token_id_fails_before_http(self):
        with self.assertRaises(ValueError):
            verify_service_identity(account_id="bad-account", token=TOKEN,
                                    request=lambda *_: self.fail("Network attempted"))
        with self.assertRaises(ValueError):
            verify_service_identity(account_id=ACCOUNT, token=TOKEN,
                                    expected_token_id="bad-id",
                                    request=lambda *_: self.fail("Network attempted"))

    def test_roles_distinguish_existing_worker_and_creator(self):
        limited = role_guidance("existing_worker")
        broad = role_guidance("new_workers")
        self.assertEqual((limited["scope"], limited["role"]), ("individual Worker", "Editor"))
        self.assertFalse(limited["can_create_new_worker"])
        self.assertTrue(broad["can_create_new_worker"])
        self.assertEqual(broad["role"], "Admin")
        with self.assertRaises(ValueError):
            role_guidance("billing-admin")


class CloudflareLifecycleTests(unittest.TestCase):
    def test_mock_lifecycle_rotation_revoke_and_recovery(self):
        result = synthetic_lifecycle()
        for label in (
            "original_execution", "editor_cannot_create_worker",
            "rotation_new_credential_works", "revoked_provider_credential_rejected",
            "revoked_local_grant_rejected", "restored_execution_disabled",
            "explicitly_readmitted_host_works",
        ):
            self.assertTrue(result[label], label)
        self.assertEqual(result["external_calls"], 0)
        self.assertFalse(result["production_authentication_tested"])
        self.assertNotIn("synthetic-only-", json.dumps(result))
        self.assertNotIn("cloudflare-operator", json.dumps(result))
        self.assertEqual(result["inventory"][0]["legal_holder"], "human-bootstrap-synthetic")

    def test_provider_rejects_editor_creation_and_other_worker(self):
        provider = MockCloudflareAccount()
        token = provider.provision(role="editor", worker_scope="misslea-example")
        for operation, worker in (("create", "new-worker"),
                                  ("delete", "misslea-example"),
                                  ("deploy", "unknown-worker")):
            with self.subTest(operation=operation, worker=worker):
                with self.assertRaises(MockProviderDenied):
                    provider.operate(secret=token, operation=operation, worker=worker)

    def test_provider_admin_can_create_worker_then_revoke(self):
        provider = MockCloudflareAccount()
        token = provider.provision(role="admin")
        provider.operate(secret=token, operation="create", worker="new-worker")
        provider.operate(secret=token, operation="deploy", worker="new-worker")
        self.assertEqual(provider.workers["new-worker"], 1)
        provider.revoke(token)
        with self.assertRaises(MockProviderDenied):
            provider.operate(secret=token, operation="delete", worker="new-worker")

    def test_local_worker_allowlist_still_blocks_admin_token(self):
        provider = MockCloudflareAccount()
        secret = provider.provision(role="admin")
        store = MockSecretStore()
        store.set("operator", secret)
        with IdentityHub(execution_enabled=True, clock=lambda: 1000) as hub:
            hub.register_resource(
                id="lab-only", provider="cloudflare", kind="compute",
                legal_holder="synthetic", operator="synthetic",
                billing_party="synthetic", recovery_authority="synthetic",
                human_bootstrap="synthetic", transferability="unknown",
                credential_handle="operator")
            hub.grant(subject="lea", resource_id="lab-only", action="compute.run",
                      issued_by="trusted-test", expires_at=2000)
            broker = CloudflareMockBroker(hub, store, provider,
                                          allowed_worker="misslea-example")
            with self.assertRaises(AccessDenied):
                broker.deploy(subject="lea", resource_id="lab-only", worker="outside")
            broker.deploy(subject="lea", resource_id="lab-only", worker="misslea-example")
            self.assertNotIn("outside", provider.workers)
            self.assertEqual(provider.workers["misslea-example"], 1)

    def test_fake_secret_store_denies_missing_handle(self):
        store = MockSecretStore()
        with self.assertRaises(PermissionError):
            store.resolve("missing")


class CloudflareCLITests(unittest.TestCase):
    def test_mock_run_no_credentials_or_external_calls(self):
        with contextlib.redirect_stdout(io.StringIO()) as out:
            status = cloudflare_cli.main(["simulate"])
        self.assertEqual(status, 0)
        report = json.loads(out.getvalue())
        self.assertEqual(report["external_calls"], 0)

    def test_verify_needs_two_explicit_flags(self):
        for flags in ([], ["--live"], ["--acknowledge-account-access"]):
            with self.subTest(flags=flags):
                with patch.dict(os.environ, {"CF_ACCOUNT_API_TOKEN": TOKEN}):
                    with patch.object(cloudflare_cli, "verify_service_identity") as remote:
                        with contextlib.redirect_stderr(io.StringIO()):
                            with self.assertRaises(SystemExit):
                                cloudflare_cli.main(["verify", "--account-id", ACCOUNT, *flags])
                        remote.assert_not_called()

    def test_verify_uses_env_without_echoing_token(self):
        with patch.dict(os.environ, {"CF_ACCOUNT_API_TOKEN": TOKEN}):
            with patch.object(cloudflare_cli, "verify_service_identity",
                              return_value={"admission": "verified_active_not_scoped",
                                            "external_requests": 1}) as remote:
                with contextlib.redirect_stdout(io.StringIO()) as output:
                    code = cloudflare_cli.main(["verify", "--account-id", ACCOUNT,
                                                "--live", "--acknowledge-account-access"])
        self.assertEqual(code, 0)
        self.assertEqual(remote.call_args.kwargs["token"], TOKEN)
        self.assertNotIn(TOKEN, output.getvalue())

    def test_invalid_variable_name_rejected_before_network(self):
        with contextlib.redirect_stderr(io.StringIO()):
            with self.assertRaises(SystemExit):
                cloudflare_cli.main(["verify", "--account-id", ACCOUNT,
                                     "--live", "--acknowledge-account-access",
                                     "--token-env", "BAD;NAME"])

    def test_failure_message_is_sanitized(self):
        with patch.dict(os.environ, {"CF_ACCOUNT_API_TOKEN": TOKEN}):
            with patch.object(cloudflare_cli, "verify_service_identity",
                              side_effect=CloudflareAdmissionError("raw secret must NOT leak")):
                with contextlib.redirect_stdout(io.StringIO()) as output:
                    code = cloudflare_cli.main(["verify", "--account-id", ACCOUNT,
                                                "--live", "--acknowledge-account-access"])
        self.assertEqual(code, 1)
        self.assertNotIn("raw secret", output.getvalue())
        self.assertNotIn(TOKEN, output.getvalue())


if __name__ == "__main__":
    unittest.main()
