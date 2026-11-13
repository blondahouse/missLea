"""Evidence-first comparison: no imputation, no rank from missing tests."""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

from labs.llm_router.security_suite import CASES

CANDIDATES = ("litellm", "gomodel", "bifrost", "portkey")
FUNCTIONAL_GATES = (
    "basic_chat", "free_provider_fallback", "all_free_outage_fail_closed",
    "tool_call_roundtrip", "streaming", "explicit_paid_only",
)
STATUSES = {"pass", "fail", "not_tested", "unsupported"}
SSRf_KNOWN = {
    "portkey": {
        "status": "fail", "evidence": "reproduced pinned-image legacy proxy SSRF",
        "source": "reports/portkey-security.json",
    },
}


def classify(candidate, functional, security_status):
    """No unknown mandatory test can silently qualify a gateway."""
    if security_status == "fail":
        return "blocked_known_security_failure"
    if any(functional.get(k) in (None, "fail", "unsupported")
           for k in FUNCTIONAL_GATES):
        return "incomplete_or_failed_functional_gate"
    if any(functional.get(k) != "pass" for k in FUNCTIONAL_GATES):
        return "insufficient_evidence"
    if security_status not in ("pass_limited",):
        return "insufficient_security_evidence"
    # Scoped synthetic tests are not a general security audit.
    return "synthetic_functional_and_security_checks_only"


def evaluate(folder: Path):
    candidates = {}
    execution_complete = True
    for name in CANDIDATES:
        path = folder / f"{name}.json"
        latency_path = folder / f"{name}-latency.json"
        security_path = folder / f"{name}-security.json"
        if not path.exists() or not latency_path.exists() or not security_path.exists():
            execution_complete = False
            candidates[name] = {
                "trial": "not_tested", "reason": "missing gateway, latency or security report",
                "functional": {key: "not_tested" for key in FUNCTIONAL_GATES},
                "security": "fail" if name == "portkey" else "not_tested",
                "budget_with_real_keys": "not_tested",
                "eligibility": classify(
                    name, {key: "not_tested" for key in FUNCTIONAL_GATES},
                    "fail" if name == "portkey" else "not_tested",
                ),
            }
            continue
        trial = json.loads(path.read_text())
        latency = json.loads(latency_path.read_text())
        security_report = json.loads(security_path.read_text())
        if security_report.get("candidate") != name or security_report.get("synthetic") is not True:
            raise ValueError(f"wrong synthetic security evidence: {name}")
        security_tests = security_report.get("tests", {})
        if set(security_tests) != set(CASES):
            raise ValueError(f"security evidence coverage is incomplete: {name}")
        allowed_security_status = {"pass", "fail", "not_tested", "not_applicable"}
        if any(data.get("status") not in allowed_security_status
               for data in security_tests.values()):
            raise ValueError(f"unknown security verdict for {name}")
        security_failures = [
            k for k, v in security_tests.items() if v["status"] == "fail"
        ]
        security_gaps = [
            k for k, v in security_tests.items()
            if v["status"] in ("not_tested", "not_applicable")
        ]
        if trial.get("gateway") != name or latency.get("candidate") != name:
            raise ValueError(f"wrong candidate report: {name}")
        functions = {}
        for key in FUNCTIONAL_GATES:
            value = trial.get("tests", {}).get(key, {}).get("result", "not_tested")
            if value not in STATUSES:
                raise ValueError(f"{name}/{key}: unknown result {value!r}")
            functions[key] = value
        if not latency.get("valid"):
            execution_complete = False
        known = SSRf_KNOWN.get(name)
        security_status = (
            "fail" if known or security_failures
            else ("not_tested" if security_gaps else "pass_limited")
        )
        cold = folder / f"{name}-cold-ready.txt"
        raw_cold = cold.read_text() if cold.exists() else ""
        match = re.search(r"(\d+) ms", raw_cold)
        metrics = folder / f"{name}-metrics.txt"
        if not match or not metrics.exists():
            execution_complete = False
        candidates[name] = {
            "trial": "complete" if latency["valid"] else "invalid",
            "functional": functions,
            "security": security_status,
            "security_evidence": (
                known["evidence"] if known else
                f"{len(security_tests)} scoped synthetic probes; not a full audit"
            ),
            "security_profile_tests": {
                key: data["status"] for key, data in security_tests.items()
            },
            "security_profile_failures": security_failures,
            "security_profile_unverified": security_gaps,
            "security_profile_context": security_report.get("configuration"),
            "budget_with_real_keys": "not_tested",
            "eligibility": classify(name, functions, security_status),
            "sample": {
                "latency": latency["latency_ms"] if latency["valid"] else None,
                "cold_ready_ms": int(match.group(1)) if match else None,
                "memory_snapshot_raw": metrics.read_text().strip() if metrics.exists() else None,
            },
            "evidence_files": [str(path), str(latency_path), str(security_path)],
        }
        if any(v != "pass" for v in functions.values()):
            execution_complete = False
    return {
        "schema_version": 1,
        "synthetic": True,
        "method": "no_imputation_no_composite_score",
        "execution_complete": execution_complete,
        "deployment_approved": False,
        "winner": None,
        "candidates": candidates,
        "limitations": [
            "real provider quota, costs, and budgeting not tested",
            "same security probes run on all four; profiles may not be production-hardened",
            "Portkey has an additional confirmed hardened-profile SSRF bypass",
            "limited local threat probes cannot establish global security clearance",
            "scoped identity with free-only authorization not provisioned in this suite",
            "performance is one sequential batch per gateway on one shared runner",
            "sequential order and background load can bias latency",
            "memory snapshot is not peak usage",
            "cold readiness excludes image download; no repeated cold-start distribution",
            "native gateway configuration is different even with identical scenarios",
        ],
    }


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--reports", default="reports")
    p.add_argument("--output", default="reports/fair-comparison.json")
    args = p.parse_args()
    data = evaluate(Path(args.reports))
    Path(args.output).write_text(json.dumps(data, indent=2) + "\n")
    print(json.dumps(data, indent=2))
    if not data["execution_complete"]:
        raise SystemExit("COMPARISON INCOMPLETE: report preserved; no winner selected")


if __name__ == "__main__":
    main()
