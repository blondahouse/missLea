"""Equal local security probes of the *tested gateway profile*, not a security audit.

All destinations are fixed loopback mocks. Never use with real API keys.
Routes without a confirmed positive control are NOT_TESTED, not PASS.
"""
from __future__ import annotations

import argparse
import base64
import json
import urllib.error
import urllib.request
from pathlib import Path

from labs.llm_router.bench import TOKEN, UPSTREAM_TOKEN, BIFROST_TOKEN, build_request

PORTS = {"primary": 19100, "backup": 19101, "paid": 19102, "forbidden": 19103}
BAD_TOKEN = "sk-lab-invalid-token-canary"
CASES = (
    "baseline_authenticated",
    "anonymous_inference",
    "invalid_token_inference",
    "anonymous_paid_route",
    "invalid_token_paid_route",
    "outbound_client_key_isolated",
    "header_destination_override",
    "config_destination_override",
    "body_destination_override",
    "redirect_302",
    "redirect_307",
    "legacy_proxy_destination_override",
    "management_read_anonymous",
    "management_write_anonymous",
    "invalid_token_echo",
    "free_scoped_key_cannot_select_paid",
)

# These paths are documented *research candidates*, not universal admin APIs.
ADMIN_PATHS = {
    "litellm": ("/config/yaml", "/config/update"),
    "gomodel": ("/admin/plugins", "/admin/plugins"),
    "bifrost": ("/api/config", "/api/config"),
    "portkey": (None, None),  # no equivalent admin API demonstrated
}
MODEL_ROUTES = {
    "litellm": ("lab-primary", "lab-paid"),
    "gomodel": ("lab-free", "openai/lab-model"),
    "bifrost": ("lab-primary/lab-model", "lab-paid/lab-model"),
    "portkey": ("lab-model", "lab-model"),
}


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, request, fp, code, msg, headers, newurl):
        return None


NO_REDIRECT_CLIENT = urllib.request.build_opener(
    urllib.request.ProxyHandler({}), NoRedirect()
)


def request(method, url, payload=None, headers=None):
    """Never follow 302/307 on the client (prevents false SSRF positives)."""
    if not url.startswith("http://127.0.0.1:"):
        raise ValueError("security probes are restricted to loopback")
    raw = json.dumps(payload).encode() if payload is not None else None
    req = urllib.request.Request(
        url, data=raw, method=method,
        headers={"Content-Type": "application/json", **(headers or {})}
    )
    try:
        with NO_REDIRECT_CLIENT.open(req, timeout=15) as response:
            return response.status, response.read().decode("utf-8", "replace")
    except urllib.error.HTTPError as error:
        return error.code, error.read().decode("utf-8", "replace")
    except (urllib.error.URLError, TimeoutError) as error:
        return 0, str(error)


def observed():
    out = {}
    for tier, port in PORTS.items():
        status, raw = request("GET", f"http://127.0.0.1:{port}/lab/events")
        if status != 200:
            raise RuntimeError(f"mock {tier} not running")
        out[tier] = json.loads(raw)["events"]
    return out


def reset():
    for port in PORTS.values():
        status, _ = request("POST", f"http://127.0.0.1:{port}/lab/reset", {})
        if status != 200:
            raise RuntimeError("failed to reset local mock provider")


def delta(before, after):
    return {
        k: after[k][len(before[k]):] for k in PORTS
    }


def total_calls(changes):
    return sum(len(calls) for calls in changes.values())


def verdict(status, changes, expectation):
    """Return scoped verdict and observed evidence, never assume unsupported."""
    any_calls = total_calls(changes)
    forbidden = len(changes["forbidden"])
    paid = len(changes["paid"])
    if expectation == "deny":
        if any_calls:
            outcome = "fail"
        elif status in (400, 401, 403):
            outcome = "pass"
        else:
            outcome = "not_tested"
    elif expectation == "no_paid":
        if paid:
            outcome = "fail"
        elif status in (400, 401, 403):
            outcome = "pass"
        else:
            outcome = "not_tested"
    elif expectation == "no_forbidden":
        if forbidden:
            outcome = "fail"
        elif sum(len(changes[x]) for x in ("primary", "backup")) or (
            status in (400, 401, 403) and total_calls(changes) == 0
        ):
            outcome = "pass"
        else:
            outcome = "not_tested"
    elif expectation == "no_redirect":
        if forbidden:
            outcome = "fail"
        elif any(e["scenario"].startswith("LAB_REDIRECT")
                 for e in changes["primary"]):
            outcome = "pass"
        else:
            outcome = "not_tested"
    else:
        raise ValueError("unknown expectation")
    return {
        "status": outcome, "http_status": status,
        "upstream_calls": {k: len(v) for k, v in changes.items()},
        "client_gateway_key_sent_upstream": any(
            e.get("has_gateway_canary", False)
            for calls in changes.values() for e in calls
        ),
    }


def run(candidate, gateway, model, paid_model):
    if candidate not in MODEL_ROUTES:
        raise ValueError("unknown gateway")
    if not gateway.startswith("http://127.0.0.1:"):
        raise ValueError("only local gateways")
    if not model or not paid_model:
        raise ValueError("all candidates require free and explicit paid models")
    for port in PORTS.values():
        if request("GET", f"http://127.0.0.1:{port}/health")[0] != 200:
            raise RuntimeError("all four mock tiers must be running")
    base = gateway.rstrip("/")
    endpoint = base + "/v1/chat/completions"
    results = {}

    def probe(name, marker="LAB_BASIC", auth="valid", use_paid=False,
              override=None, path=None):
        reset()
        request_body, headers = build_request(
            candidate, marker, paid_model if use_paid else model,
            "explicit_paid" if use_paid else "basic",
        )
        if auth == "none":
            headers.pop("Authorization", None)
        elif auth == "invalid":
            headers["Authorization"] = "Bearer " + BAD_TOKEN
        elif auth == "free" and candidate == "bifrost":
            headers["Authorization"] = "Bearer sk-bf-lab-free-only"
        elif auth != "valid":
            raise ValueError("invalid auth marker")
        if override == "header":
            headers["x-portkey-custom-host"] = "http://127.0.0.1:19103/v1"
        elif override == "config":
            headers["x-portkey-config"] = json.dumps({
                "strategy": {"mode": "fallback"},
                "targets": [{
                    "provider": "openai", "api_key": UPSTREAM_TOKEN,
                    "custom_host": "http://127.0.0.1:19103/v1",
                }],
            })
        elif override == "body":
            request_body["api_base"] = "http://127.0.0.1:19103/v1"
            request_body["base_url"] = "http://127.0.0.1:19103/v1"
        before = observed()
        status, body = request("POST", base + path if path else endpoint,
                               request_body, headers)
        return status, body, delta(before, observed())

    control_status, _, control_delta = probe("baseline_authenticated")
    valid_control = (
        control_status == 200 and len(control_delta["primary"]) == 1
        and not any(control_delta[x] for x in ("paid", "backup", "forbidden"))
    )
    results["baseline_authenticated"] = {
        "status": "pass" if valid_control else "fail",
        "http_status": control_status,
        "upstream_calls": {k: len(v) for k, v in control_delta.items()},
    }
    if not valid_control:
        raise RuntimeError("valid baseline is required before negative probes")

    for label, auth in (
        ("anonymous_inference", "none"), ("invalid_token_inference", "invalid")
    ):
        status, _, changes = probe(label, auth=auth)
        results[label] = verdict(status, changes, "deny")

    for label, auth in (
        ("anonymous_paid_route", "none"), ("invalid_token_paid_route", "invalid")
    ):
        status, _, changes = probe(label, auth=auth, use_paid=True)
        results[label] = verdict(status, changes, "no_paid")

    results["outbound_client_key_isolated"] = {
        "status": "fail" if any(
            e.get("has_gateway_canary") for e in control_delta["primary"]
        ) else "pass",
        "upstream_calls": {"primary": len(control_delta["primary"])},
        "description": "checks synthetic gateway client token, not other secret formats",
    }

    for label, override in (
        ("header_destination_override", "header"),
        ("config_destination_override", "config"),
        ("body_destination_override", "body")
    ):
        status, _, changes = probe(label, override=override)
        results[label] = verdict(status, changes, "no_forbidden")

    for marker in ("LAB_REDIRECT_302", "LAB_REDIRECT_307"):
        label = "redirect_" + marker.rsplit("_", 1)[-1]
        status, _, changes = probe(label, marker=marker)
        results[label] = verdict(status, changes, "no_redirect")

    status, _, changes = probe(
        "legacy_proxy_destination_override", override="header",
        path="/v1/proxy/v1/chat/completions",
    )
    if candidate == "portkey":
        results["legacy_proxy_destination_override"] = verdict(
            status, changes, "no_forbidden"
        )
    else:
        # A missing vendor-specific endpoint is not an SSRF security pass.
        results["legacy_proxy_destination_override"] = {
            "status": "not_applicable" if status == 404 and total_calls(changes) == 0
                      else verdict(status, changes, "no_forbidden")["status"],
            "http_status": status,
            "upstream_calls": {k: len(v) for k, v in changes.items()},
        }

    admin_read, admin_write = ADMIN_PATHS[candidate]
    if admin_read:
        if candidate == "bifrost":
            admin_token = base64.b64encode(
                b"lab-admin:sk-lab-admin-password"
            ).decode()
            admin_headers = {"Authorization": "Basic " + admin_token}
        else:
            admin_headers = {"Authorization": "Bearer " + TOKEN}
        good_status, _ = request(
            "GET", base + admin_read, headers=admin_headers,
        )
        bad_status, _ = request("GET", base + admin_read)
        if bad_status == 200:
            state = "fail"
        elif good_status == 200 and bad_status in (401, 403):
            state = "pass"
        else:
            state = "not_tested"
        results["management_read_anonymous"] = {
            "status": state, "http_status": bad_status,
            "authorized_http_status": good_status,
            "path": admin_read,
        }
        # Never make valid admin mutations, even with fake credentials.
        bad_write, _ = request(
            "PUT" if candidate == "bifrost" else "POST",
            base + admin_write, {},
        )
        results["management_write_anonymous"] = {
            "status": "fail" if 200 <= bad_write < 300
                      else ("pass" if bad_write in (401, 403)
                            else "not_tested"),
            "http_status": bad_write,
            "path": admin_write,
            "note": "invalid harmless empty payload, no approved admin mutation",
        }
    else:
        results["management_read_anonymous"] = {
            "status": "not_tested", "reason": "no equivalent native admin path"
        }
        results["management_write_anonymous"] = {
            "status": "not_tested", "reason": "no equivalent native admin path"
        }

    status, body, changes = probe(
        "invalid_token_echo", auth="invalid",
        marker="LAB_BASIC secret-response-check"
    )
    results["invalid_token_echo"] = {
        "status": "fail" if BAD_TOKEN in body else (
            "pass" if status in (400, 401, 403) else "not_tested"
        ),
        "http_status": status,
        "credential_echoed": BAD_TOKEN in body,
        "upstream_calls": {k: len(v) for k, v in changes.items()},
        "scope": "one wrong-token HTTP response; container logs not inspected",
    }

    if candidate == "bifrost":
        free_status, _, free_hits = probe("free_scope_positive", auth="free")
        paid_status, _, paid_hits = probe(
            "free_scope_paid_denial", auth="free", use_paid=True
        )
        valid_free_scope = (
            free_status == 200 and len(free_hits["primary"]) == 1
            and len(free_hits["paid"]) == 0
        )
        if valid_free_scope:
            scoped_status = (
                "fail" if paid_hits["paid"]
                else ("pass" if paid_status in (400, 401, 403) else "not_tested")
            )
        else:
            scoped_status = "not_tested"
        results["free_scoped_key_cannot_select_paid"] = {
            "status": scoped_status, "free_control_http_status": free_status,
            "paid_http_status": paid_status,
            "free_control_upstream_calls": {
                k: len(v) for k, v in free_hits.items()
            },
            "paid_attempt_upstream_calls": {
                k: len(v) for k, v in paid_hits.items()
            },
            "scope": "Bifrost native fixture virtual key, not real-money guarantee",
        }
    else:
        results["free_scoped_key_cannot_select_paid"] = {
            "status": "not_tested",
            "reason": "no verified native free-scoped identity in this profile",
        }

    failures = [n for n, v in results.items() if v["status"] == "fail"]
    unknown = [n for n, v in results.items()
               if v["status"] in ("not_tested", "not_applicable")]
    return {
        "schema_version": 1,
        "synthetic": True,
        "candidate": candidate,
        "configuration": "same profile as functional benchmark, not production-hardened",
        "gateway_client_credential_distinct_from_upstream_credential": True,
        "tests": results,
        "observed_failures": failures,
        "not_verified": unknown,
        "profile_security": (
            "fail" if failures else "partial_pass_not_a_security_clearance"
        ),
        "real_key_approved": False,
        "not_tested_globally": [
            "TLS and authenticated remote clients",
            "real scoped free-only virtual keys and paid authorization",
            "real budget enforcement and concurrent spend",
            "supply chain and dependency vulnerabilities",
            "privileged admin operations after authenticated session",
            "external IP ranges, DNS rebinding and complex redirects",
            "HTTP request smuggling, UI XSS, extension surfaces",
            "actual secret persistence and gateway log retention",
        ],
    }


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--candidate", choices=MODEL_ROUTES, required=True)
    p.add_argument("--gateway", required=True)
    p.add_argument("--model", required=True)
    p.add_argument("--paid-model", required=True)
    p.add_argument("--output", required=True)
    args = p.parse_args()
    report = run(args.candidate, args.gateway, args.model, args.paid_model)
    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))
    # This is a diagnostic. An observed vulnerability must never be hidden.
    # It does not fail CI merely for finding a security defect; the verdict
    # is enforced by the comparator's deployment gate.
    if report["tests"]["baseline_authenticated"]["status"] != "pass":
        raise SystemExit("unable to establish authenticated security baseline")


if __name__ == "__main__":
    main()
