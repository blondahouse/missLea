"""Equal, uniquely tagged local calls for *within-run* latency comparison.

Does not make claims about production latency or actual model quality.
"""
from __future__ import annotations

import argparse
import json
import math
import statistics
import time
from pathlib import Path
from urllib.error import URLError

from labs.llm_router.bench import (
    build_request, call, choose_text, events, reset, TOKEN,
)

WARMUP = 8
MEASURED = 40


def percentile(values, p):
    """Nearest-rank percentile, intentionally deterministic and documented."""
    if not values or not 0 < p <= 100:
        raise ValueError("non-empty samples and percentile 1..100 required")
    return sorted(values)[math.ceil(len(values) * p / 100) - 1]


def run(candidate, gateway, model, warmup=WARMUP, measured=MEASURED):
    if not gateway.startswith("http://127.0.0.1:"):
        raise ValueError("local gateways only")
    if warmup < 1 or measured < 2:
        raise ValueError("insufficient sample count")
    reset()
    ms_values = []
    failures = []
    for i in range(warmup + measured):
        # Unique marker prevents response caching from misleading comparisons.
        request, headers = build_request(
            candidate, f"LAB_BASIC sample-{i:04d}", model
        )
        started = time.perf_counter()
        try:
            status, raw = call(
                gateway.rstrip("/") + "/v1/chat/completions",
                request, timeout=30, headers=headers,
            )
        except (URLError, TimeoutError) as error:
            status, raw = 0, str(error)
        latency_ms = (time.perf_counter() - started) * 1000
        if status != 200 or choose_text(raw).get("content") != "mock:primary":
            failures.append({"iteration": i, "status": status})
        if i >= warmup:
            ms_values.append(latency_ms)
    backend_events = events()
    primary_calls = sum(
        e["scenario"] == "LAB_BASIC" for e in backend_events["primary"]
    )
    backup_calls = sum(
        e["scenario"] == "LAB_BASIC" for e in backend_events["backup"]
    )
    paid_calls = len(backend_events["paid"])
    complete = (not failures and primary_calls == warmup + measured
                and backup_calls == 0 and paid_calls == 0)
    return {
        "synthetic": True, "candidate": candidate,
        "workload": {
            "warmup_requests": warmup, "measured_requests": measured,
            "concurrency": 1, "unique_prompts": True,
            "upstream": "same deterministic loopback mock",
            "cache_disabled_by": "unique prompt per request and upstream audit",
        },
        "valid": complete,
        "validation": {
            "failures": failures,
            "primary_calls": primary_calls,
            "backup_calls": backup_calls,
            "paid_calls": paid_calls,
        },
        "latency_ms": {
            "p50": round(percentile(ms_values, 50), 2),
            "p95": round(percentile(ms_values, 95), 2),
            "mean": round(statistics.mean(ms_values), 2),
            "min": round(min(ms_values), 2),
            "max": round(max(ms_values), 2),
        },
        "limitations": [
            "one batch on one CI runner; not production performance",
            "does not isolate gateway CPU from mock-provider processing",
            "no meaningful confidence interval from one run",
            "auth and request config are gateway-native, not byte-identical",
        ],
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--candidate", required=True)
    parser.add_argument("--gateway", required=True)
    parser.add_argument("--model", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    report = run(args.candidate, args.gateway, args.model)
    Path(args.output).write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2))
    if not report["valid"]:
        raise SystemExit("INVALID LATENCY SAMPLE: upstream call audit mismatch")


if __name__ == "__main__":
    main()
