"""Diagnose Portkey's known SSRF guard bypass using fake keys and localhost ONLY.

Never send this diagnostic to any public gateway or non-loopback target.
The returned 'vulnerable' verdict intentionally does not claim an exploit
against a real service, nor any actual credential exposure.
"""
from __future__ import annotations

import json
import urllib.error
import urllib.request
from pathlib import Path

GATEWAY = "http://127.0.0.1:8787"
MOCK = "http://127.0.0.1:19100"
CANARY = "sk-lab-synthetic-only"


def http(method: str, url: str, payload=None, headers=None):
    if not (url.startswith(GATEWAY + "/") or url.startswith(MOCK + "/")):
        raise ValueError("security diagnostic is restricted to local fixtures")
    body = None if payload is None else json.dumps(payload).encode()
    request = urllib.request.Request(
        url, data=body, method=method,
        headers={"Content-Type": "application/json", **(headers or {})},
    )
    try:
        with urllib.request.urlopen(request, timeout=10) as response:
            return response.status, response.read()
    except urllib.error.HTTPError as error:
        return error.code, error.read()


def mock_events():
    status, body = http("GET", MOCK + "/lab/events")
    if status != 200:
        raise RuntimeError("mock event stream unavailable")
    return json.loads(body)["events"]


def diagnose(protected_status, protected_hits, legacy_status, legacy_hits):
    if protected_hits:
        return "INCONCLUSIVE: even the ordinary route reached a forbidden local host"
    if protected_status < 400:
        return "INCONCLUSIVE: ordinary route returned success without mock traffic"
    if legacy_hits:
        return "VULNERABLE: deprecated proxy route bypassed host validation"
    if legacy_status >= 400:
        return "NOT_REPRODUCED: both routes refused the test local destination"
    return "INCONCLUSIVE: legacy route returned success without mock traffic"


def run():
    http("POST", MOCK + "/lab/reset", {})
    # This hostname is deliberately absent from the gateway's test allowlist.
    # No internet traffic, external endpoints, or real credentials.
    headers = {
        "Authorization": "Bearer " + CANARY,
        "x-portkey-provider": "openai",
        "x-portkey-custom-host": MOCK + "/",
    }
    payload = {
        "model": "lab-model",
        "messages": [{"role": "user", "content": "LAB_BASIC"}],
    }
    protected_status, _ = http(
        "POST", GATEWAY + "/v1/chat/completions", payload, headers
    )
    protected_hits = len(mock_events())
    # The legacy route must enforce the SAME host policy as the ordinary route.
    legacy_status, _ = http(
        "POST", GATEWAY + "/v1/proxy/v1/chat/completions", payload, headers
    )
    legacy_hits = len(mock_events()) - protected_hits
    verdict = diagnose(protected_status, protected_hits, legacy_status, legacy_hits)
    report = {
        "synthetic": True,
        "gateway": "portkey",
        "probe": "local-only-ssrf-routing-regression",
        "protected_route": {"http_status": protected_status, "mock_hits": protected_hits},
        "legacy_route": {"http_status": legacy_status, "mock_hits": legacy_hits},
        "security_verdict": verdict,
        "production_eligible": False,
        "not_tested": [
            "redirect-following bypass",
            "actual credential forwarding",
            "real network isolation",
            "other HTTP methods and provider-specific routes",
            "production authentication/authorization",
        ],
    }
    return report


def main():
    report = run()
    Path("reports").mkdir(exist_ok=True)
    Path("reports/portkey-security.json").write_text(
        json.dumps(report, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(report, indent=2))
    if report["security_verdict"].startswith("VULNERABLE"):
        print("::warning title=Portkey Security Gate BLOCKED::"
              "Pinned Portkey image accepted a forbidden localhost route "
              "through the deprecated proxy endpoint. Production use with "
              "real keys is NOT approved.")
    if report["security_verdict"].startswith("INCONCLUSIVE"):
        raise SystemExit("SSRF diagnostic inconclusive; inspect the synthetic report")


if __name__ == "__main__":
    main()
