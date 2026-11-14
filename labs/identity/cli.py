"""Synthetic, offline-only demonstration of the first identity hub slice."""
from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path

from labs.identity.hub import AccessDenied, IdentityHub, SyntheticBroker


def demo() -> dict:
    with tempfile.TemporaryDirectory(prefix="misslea-identity-lab-") as temp:
        db = Path(temp) / "identity.sqlite"
        with IdentityHub(db, execution_enabled=True, clock=lambda: 1000) as hub:
            hub.register_resource(
                id="compute-demo", provider="synthetic-cloudflare", kind="compute",
                legal_holder="test human bootstrap", operator="synthetic-agent",
                billing_party="none-synthetic", recovery_authority="test custodian",
                human_bootstrap="hypothetical", transferability="not_tested",
                credential_handle="lab-token",
            )
            grant = hub.grant(subject="miss-lea-lab", resource_id="compute-demo",
                              action="compute.run", issued_by="trusted-test-harness",
                              expires_at=2000)
            broker = SyntheticBroker(hub, {"lab-token": "DO-NOT-PRINT-SYNTHETIC-SECRET"})
            result = broker.invoke(subject="miss-lea-lab", resource_id="compute-demo",
                                   action="compute.run")
            hub.revoke(grant)
            try:
                broker.invoke(subject="miss-lea-lab", resource_id="compute-demo",
                              action="compute.run")
                revoked = False
            except AccessDenied:
                revoked = True
            inventory = hub.inventory()
            audit = hub.audit()
            snapshot = Path(temp) / "copy.sqlite"
            hub.snapshot(snapshot)
        with IdentityHub(snapshot, clock=lambda: 1000) as restored:
            restored_denies = not restored.authorize(
                subject="miss-lea-lab", resource_id="compute-demo", action="compute.run")
        return {"synthetic": True, "result": result, "revocation_enforced": revoked,
                "restore_defaults_inactive": restored_denies, "inventory": inventory,
                "audit": audit, "external_calls": 0}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Miss Lea synthetic Identity & Capability Hub")
    parser.add_argument("command", choices=["demo"])
    args = parser.parse_args(argv)
    if args.command == "demo":
        result = demo()
        print(json.dumps(result, indent=2, ensure_ascii=False))
        return 0 if (result["revocation_enforced"]
                     and result["restore_defaults_inactive"]
                     and result["result"] == {"count": 3, "sum": 10, "squares": 38}) else 1
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
