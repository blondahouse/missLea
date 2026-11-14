"""Opt-in Compute Lab. No network calls happen unless explicitly acknowledged."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

PROVIDERS = {
    "e2b": "API-created Linux sandbox; Python SDK required",
    "cloudflare": "Short-lived HTTP Worker; Wrangler/Node required",
    "cloud_run": "One-off container Job; gcloud and Cloud Logging access required",
}


def main(argv=None):
    parser = argparse.ArgumentParser(description="Miss Lea isolated compute experiments")
    sub = parser.add_subparsers(dest="action", required=True)
    sub.add_parser("list", help="Show independently supported platforms")
    trial = sub.add_parser("run", help="Create, execute, observe and delete a remote trial")
    trial.add_argument("provider", choices=PROVIDERS.keys())
    trial.add_argument("--live", action="store_true", help="Permit contacting the cloud provider")
    trial.add_argument("--acknowledge-cost", action="store_true",
                       help="Explicitly accept possible provider charges")
    trial.add_argument("--output", help="Write JSON report (use ignored reports/ folder)")
    args = parser.parse_args(argv)
    if args.action == "list":
        for name, description in PROVIDERS.items():
            print(f"{name}: {description}")
        return 0
    if not args.live or not args.acknowledge_cost:
        parser.error("Remote trials require BOTH --live and --acknowledge-cost; no resources created")
    if args.provider == "e2b":
        from labs.compute.e2b_trial import run
    elif args.provider == "cloudflare":
        from labs.compute.cloudflare_trial import run
    else:
        from labs.compute.cloud_run_trial import run
    outcome = run()
    serialized = json.dumps(outcome, ensure_ascii=False, indent=2) + "\n"
    if args.output:
        target = Path(args.output)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(serialized, encoding="utf-8")
    print(serialized, end="")
    return 0 if outcome["status"] == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
