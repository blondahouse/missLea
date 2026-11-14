"""No external accounts, networks, genuine credentials or billable operations."""
from __future__ import annotations

import contextlib
import io
import json
import sqlite3
import tempfile
import unittest
from pathlib import Path

from labs.identity.cli import demo, main
from labs.identity.hub import AccessDenied, EXPECTED, IdentityHub, SyntheticBroker


class IdentityHubTests(unittest.TestCase):
    def setUp(self):
        self.now = 1000
        self.hub = IdentityHub(execution_enabled=True, clock=lambda: self.now)
        self.hub.register_resource(
            id="cloudflare-1", provider="cloudflare", kind="compute",
            legal_holder="person-bootstrap", operator="miss-lea",
            billing_party="no-billing-test", recovery_authority="human-sandbox",
            human_bootstrap="required", transferability="unknown",
            credential_handle="opaque-handle",
        )
        self.broker = SyntheticBroker(self.hub, {"opaque-handle": "HIGHLY-SENSITIVE-SYNTHETIC"})

    def tearDown(self):
        self.hub.close()

    def grant(self, action="compute.run", subject="lea", resource_id="cloudflare-1", expiry=2000):
        return self.hub.grant(subject=subject, resource_id=resource_id,
                              action=action, issued_by="trusted-fixture", expires_at=expiry)

    def test_deny_by_default_and_unknown_actor(self):
        with self.assertRaises(AccessDenied):
            self.broker.invoke(subject="lea", resource_id="cloudflare-1", action="compute.run")
        self.grant()
        with self.assertRaises(AccessDenied):
            self.broker.invoke(subject="imposter", resource_id="cloudflare-1", action="compute.run")
        self.assertEqual([entry["verdict"] for entry in self.hub.audit()], ["DENY", "DENY"])

    def test_scoped_execution_and_no_secret_leak(self):
        self.grant()
        self.assertEqual(self.broker.invoke(subject="lea", resource_id="cloudflare-1",
                                            action="compute.run"), EXPECTED)
        with self.assertRaises(AccessDenied):
            self.broker.invoke(subject="lea", resource_id="cloudflare-2", action="compute.run")
        with self.assertRaises(AccessDenied):
            self.broker.invoke(subject="lea", resource_id="cloudflare-1", action="compute.delete")
        evidence = json.dumps({"inventory": self.hub.inventory(), "audit": self.hub.audit()})
        self.assertNotIn("HIGHLY-SENSITIVE", evidence)
        self.assertNotIn("opaque-handle", evidence)
        self.assertIn("person-bootstrap", evidence)
        self.assertIn("recovery_authority", evidence)

    def test_grant_expiry_revocation_and_suspension(self):
        issued = self.grant(expiry=1002)
        self.assertTrue(self.hub.authorize(subject="lea", resource_id="cloudflare-1", action="compute.run"))
        self.now = 1002
        self.assertFalse(self.hub.authorize(subject="lea", resource_id="cloudflare-1", action="compute.run"))
        self.assertTrue(self.hub.revoke(issued))
        self.assertFalse(self.hub.revoke(issued))
        self.grant(expiry=1004)
        self.hub.set_resource_status("cloudflare-1", "suspended")
        self.assertFalse(self.hub.authorize(subject="lea", resource_id="cloudflare-1", action="compute.run"))
        self.hub.set_resource_status("cloudflare-1", "active")
        self.assertTrue(self.hub.authorize(subject="lea", resource_id="cloudflare-1", action="compute.run"))

    def test_no_wildcards_paid_actions_or_expired_grants(self):
        for args in ({"subject": "*"}, {"action": "wallet.pay"}, {"action": "*"}, {"expires_at": 1000}):
            with self.subTest(args=args), self.assertRaises(ValueError):
                self.hub.grant(subject=args.get("subject", "lea"), resource_id="cloudflare-1",
                               action=args.get("action", "compute.run"), issued_by="fixture",
                               expires_at=args.get("expires_at", 2000))
        with self.assertRaises(ValueError):
            self.hub.register_resource(
                id="another", provider="test", kind="compute", legal_holder="unknown",
                operator="unknown", billing_party="unknown", recovery_authority="unknown",
                human_bootstrap="unknown", transferability="unknown", credential_handle="*"
            )

    def test_snapshot_does_not_reenable_authority(self):
        self.grant()
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "state.sqlite"
            self.hub.snapshot(target)
            with IdentityHub(target, clock=lambda: self.now) as restored:
                self.assertEqual(restored.inventory(), self.hub.inventory())
                self.assertFalse(restored.authorize(subject="lea", resource_id="cloudflare-1",
                                                    action="compute.run"))
                self.assertEqual(restored.audit()[-1]["reason"], "session_inactive")

    def test_credentials_not_stored_in_sqlite(self):
        self.grant()
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "state.sqlite"
            self.hub.snapshot(target)
            with sqlite3.connect(target) as conn:
                all_text = " ".join(str(row) for table in ("resources", "grants", "audit")
                                    for row in conn.execute(f"SELECT * FROM {table}"))
                self.assertNotIn("HIGHLY-SENSITIVE", all_text)

    def test_mock_unimplemented_scope_fails(self):
        self.grant(action="compute.inspect")
        with self.assertRaises(NotImplementedError):
            self.broker.invoke(subject="lea", resource_id="cloudflare-1", action="compute.inspect")


class CLI(unittest.TestCase):
    def test_demo_end_to_end(self):
        result = demo()
        self.assertTrue(result["revocation_enforced"])
        self.assertTrue(result["restore_defaults_inactive"])
        self.assertEqual(result["external_calls"], 0)
        self.assertEqual(result["result"], EXPECTED)
        with contextlib.redirect_stdout(io.StringIO()) as output:
            self.assertEqual(main(["demo"]), 0)
        self.assertNotIn("DO-NOT-PRINT-SYNTHETIC-SECRET", output.getvalue())


if __name__ == "__main__":
    unittest.main()
