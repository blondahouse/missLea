"""Cloudflare identity lab: offline lifecycle simulation and optional read-only verification."""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
from pathlib import Path

from labs.identity.cloudflare_service import (
    CloudflareAdmissionError, role_guidance, verify_service_identity,
)
from labs.identity.cloudflare_simulation import synthetic_lifecycle


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Cloudflare service-identity research")
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("simulate", help="Synthetic rotation/revocation/recovery; zero external calls")
    roles = sub.add_parser("roles", help="Print documented Cloudflare Workers authority options")
    roles.add_argument("mode", choices=("existing_worker", "new_workers"))
    verify = sub.add_parser("verify", help="Opt-in read-only Cloudflare token status check")
    verify.add_argument("--live", action="store_true", help="Allow one Cloudflare API GET")
    verify.add_argument("--acknowledge-account-access", action="store_true",
                        help="Confirm authorization to use this Cloudflare account token")
    verify.add_argument("--account-id", required=True, help="Cloudflare 32-character account ID")
    verify.add_argument("--expected-token-id", help="Optional token ID to detect wrong credential")
    verify.add_argument("--token-env", default="CF_ACCOUNT_API_TOKEN",
                        help="Name of environment variable containing the token (never printed)")
    verify.add_argument("--output", help="Write sanitized JSON to reports/ (ignored by Git)")
    args = parser.parse_args(argv)

    if args.command == "simulate":
        evidence = synthetic_lifecycle()
        ok = all(evidence[key] for key in (
            "original_execution", "editor_cannot_create_worker",
            "rotation_new_credential_works", "revoked_provider_credential_rejected",
            "revoked_local_grant_rejected", "restored_execution_disabled",
            "explicitly_readmitted_host_works",
        ))
    elif args.command == "roles":
        evidence = role_guidance(args.mode)
        ok = True
    else:
        if not args.live or not args.acknowledge_account_access:
            parser.error("Verification requires --live and --acknowledge-account-access")
        if not re.fullmatch(r"[A-Z_][A-Z0-9_]*", args.token_env):
            parser.error("Invalid environment variable name")
        token = os.environ.get(args.token_env)
        if not token:
            parser.error("Token environment variable is unset")
        try:
            evidence = verify_service_identity(
                account_id=args.account_id,
                token=token,
                expected_token_id=args.expected_token_id,
            )
        except (CloudflareAdmissionError, ValueError):
            print(json.dumps({"provider": "cloudflare", "admission": "blocked",
                              "error": "Verification failed; inspect account permissions locally"},
                             indent=2))
            return 1
        ok = evidence["admission"] == "verified_active_not_scoped"
        if args.output:
            target = Path(args.output)
            if target.is_absolute() or ".." in target.parts or target.parts[:1] != ("reports",):
                parser.error("Reports must be written to relative reports/ directory")
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(json.dumps(evidence, indent=2) + "\n", encoding="utf-8")

    print(json.dumps(evidence, indent=2, ensure_ascii=False))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
