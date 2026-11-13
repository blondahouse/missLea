"""Probe an actual third-party gateway with mock LLMs; no real API keys.

Probes report observed behaviour, not assumed features. Only critical failures
fail the exit code. Different router profiles legitimately support different
features, and unsupported probes remain visible as not_tested / failed.
"""
from __future__ import annotations

import argparse
import json
import time
import urllib.error
import urllib.request
from pathlib import Path


MOCK_PORTS = {"primary": 19100, "backup": 19101, "paid": 19102}
TOKEN = "sk-lab-gateway-client"
UPSTREAM_TOKEN = "sk-lab-synthetic-only"


def call(url: str, data=None, *, timeout=15, headers=None):
    raw = None if data is None else json.dumps(data).encode("utf-8")
    hdr = {"Content-Type": "application/json", **(headers or {})}
    req = urllib.request.Request(url, data=raw, headers=hdr)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as response:
            return response.status, response.read().decode("utf-8", "replace")
    except urllib.error.HTTPError as error:
        return error.code, error.read().decode("utf-8", "replace")


def events():
    return {
        tier: json.loads(call(f"http://127.0.0.1:{port}/lab/events")[1])["events"]
        for tier, port in MOCK_PORTS.items()
    }


def reset():
    for port in MOCK_PORTS.values():
        status, _ = call(f"http://127.0.0.1:{port}/lab/reset", {})
        if status != 200:
            raise RuntimeError("mock reset failed")


def choose_text(raw):
    try:
        choice = json.loads(raw)["choices"][0]
        return choice.get("message") or {}
    except (KeyError, IndexError, ValueError, TypeError):
        return {}


def build_request(candidate, marker, model, name="basic", payload=None):
    """Build an equivalent synthetic call through each gateway's native contract.

    Portkey uses an in-request routing header; other gateways resolve configured
    model aliases server-side. This architectural difference is recorded, not hidden.
    Only hardcoded loopback mocks and synthetic credentials are permitted.
    """
    request = {
        "model": model,
        "messages": [{"role": "user", "content": marker}],
        **(payload or {}),
    }
    call_headers = {"Authorization": "Bearer " + TOKEN}
    if candidate == "bifrost" and name != "explicit_paid":
        # Explicitly never include the paid mock in a free fallback chain.
        request["fallbacks"] = ["lab-backup/lab-model"]
    if candidate == "portkey":
        # Portkey's per-request config is part of its documented gateway API.
        # No arbitrary user-provided hosts: every target is a fixed lab port.
        free_targets = [
            {"provider": "openai", "api_key": UPSTREAM_TOKEN,
             "custom_host": f"http://127.0.0.1:{MOCK_PORTS[tier]}/v1"}
            for tier in ("primary", "backup")
        ]
        paid_target = [
            {"provider": "openai", "api_key": UPSTREAM_TOKEN,
             "custom_host": f"http://127.0.0.1:{MOCK_PORTS['paid']}/v1"}
        ]
        call_headers["x-portkey-config"] = json.dumps({
            "strategy": {"mode": "fallback"},
            "targets": paid_target if name == "explicit_paid" else free_targets,
        })
    return request, call_headers


def run(args):
    if not args.gateway.startswith("http://127.0.0.1:") and not args.gateway.startswith("http://localhost:"):
        raise ValueError("synthetic test only allows loopback gateway URLs")
    for port in MOCK_PORTS.values():
        if call(f"http://127.0.0.1:{port}/health")[0] != 200:
            raise RuntimeError("all three local mock providers must be running")
    reset()
    results = {}
    gateway = args.gateway.rstrip("/") + "/v1/chat/completions"
    def probe(name, marker, model, payload=None):
        request, call_headers = build_request(
            args.candidate, marker, model, name, payload
        )
        started = time.perf_counter()
        try:
            status, raw = call(gateway, request, timeout=30, headers=call_headers)
            return status, raw, round((time.perf_counter() - started) * 1000, 2)
        except (urllib.error.URLError, TimeoutError) as error:
            return 0, str(error), round((time.perf_counter() - started) * 1000, 2)

    status, raw, ms = probe("basic", "LAB_BASIC", args.model)
    msg = choose_text(raw)
    results["basic_chat"] = {
        "result": "pass" if status == 200 and msg.get("content") == "mock:primary" else "fail",
        "status": status, "latency_ms": ms, "observed": msg.get("content"),
    }

    status, raw, ms = probe("quota", "LAB_QUOTA", args.model)
    msg = choose_text(raw)
    if args.expect_fallback:
        state = "pass" if status == 200 and msg.get("content") == "mock:backup" else "fail"
    else:
        state = "not_tested"
    results["free_provider_fallback"] = {
        "result": state, "status": status, "latency_ms": ms,
        "observed": msg.get("content"),
        "note": "expected fallback" if args.expect_fallback else "fallback not configured for this profile",
    }

    before_paid = len(events()["paid"])
    status, raw, ms = probe("outage", "LAB_OUTAGE", args.model)
    snapshot = events()
    paid_delta = len(snapshot["paid"]) - before_paid
    free_outage_requests = [
        e for tier in ("primary", "backup")
        for e in snapshot[tier] if e["scenario"] == "LAB_OUTAGE"
    ]
    failed_closed = status >= 400 and paid_delta == 0 and bool(free_outage_requests)
    results["all_free_outage_fail_closed"] = {
        "result": "pass" if failed_closed else "fail",
        "status": status, "latency_ms": ms,
        "unexpected_paid_calls": paid_delta,
        "free_provider_requests": len(free_outage_requests),
    }

    status, raw, ms = probe(
        "tools", "LAB_TOOL", args.model,
        {"tools": [{"type": "function", "function": {
            "name": "inspect", "description": "synthetic check",
            "parameters": {"type": "object", "properties": {}},
        }}], "tool_choice": "auto"},
    )
    msg = choose_text(raw)
    tools = msg.get("tool_calls") or []
    results["tool_call_roundtrip"] = {
        "result": "pass" if status == 200 and tools and tools[0].get("function", {}).get("name") == "inspect" else "fail",
        "status": status, "latency_ms": ms,
    }

    status, raw, ms = probe("stream", "LAB_STREAM", args.model, {"stream": True})
    results["streaming"] = {
        "result": "pass" if status == 200 and "data: " in raw and "[DONE]" in raw else "fail",
        "status": status, "latency_ms": ms,
    }

    if args.paid_model:
        before_paid = len(events()["paid"])
        status, raw, ms = probe("explicit_paid", "LAB_BASIC", args.paid_model)
        paid_delta = len(events()["paid"]) - before_paid
        results["explicit_paid_only"] = {
            "result": "pass" if status == 200 and paid_delta == 1 else "fail",
            "status": status, "latency_ms": ms, "paid_calls": paid_delta,
        }
    else:
        results["explicit_paid_only"] = {
            "result": "not_tested",
            "note": "this profile has no paid mock route",
        }

    final_events = events()
    report = {
        "schema_version": 1,
        "synthetic": True,
        "gateway": args.candidate,
        "configuration": {
            "profile": args.profile,
            "model": args.model,
            "free_fallback_expected": args.expect_fallback,
            "paid_route_exercised_only_with_explicit_model": bool(args.paid_model),
        },
        "tests": results,
        "observed_provider_calls": {
            tier: len(data) for tier, data in final_events.items()
        },
        "not_measured": [
            "actual_model_quality", "real_vendor_billing", "real_budget_enforcement",
            "peak_rss_mb", "cross_provider_model_equivalence",
        ] + ([] if args.expect_fallback else ["independent_provider_failover"]),
    }
    return report


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--candidate", required=True)
    parser.add_argument("--gateway", required=True)
    parser.add_argument("--model", required=True)
    parser.add_argument("--paid-model")
    parser.add_argument("--profile", required=True)
    parser.add_argument("--expect-fallback", action="store_true")
    parser.add_argument("--output", default="router-report.json")
    args = parser.parse_args()
    report = run(args)
    Path(args.output).write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2))
    required = ["basic_chat", "all_free_outage_fail_closed"]
    if args.expect_fallback:
        required.append("free_provider_fallback")
    if args.paid_model:
        required.append("explicit_paid_only")
    if any(report["tests"][name]["result"] != "pass" for name in required):
        raise SystemExit("CRITICAL ROUTER CHECK FAILED")


if __name__ == "__main__":
    main()
