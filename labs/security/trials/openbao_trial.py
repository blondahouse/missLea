"""Real OpenBao localhost smoke: synthetic data only, no LLM or external accounts.

Exercises a restrictive machine token, forbidden actions, and revocation.
This dev-mode trial is NOT evidence of durable identity, HA, unsealing or S9.
"""
from __future__ import annotations

import json
import os
import time
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

BASE = "http://127.0.0.1:18200/v1"
CANARY = "synthetic-misslea-compute-not-a-real-credential"


def api(path: str, token: str, method: str = "GET", data: dict | None = None):
    payload = None if data is None else json.dumps(data).encode()
    req = Request(
        BASE + path, data=payload, method=method,
        headers={"X-Vault-Token": token, "Content-Type": "application/json"},
    )
    try:
        with urlopen(req, timeout=7) as response:
            body = response.read(131072)
            return response.status, (json.loads(body) if body.strip() else {})
    except HTTPError as exc:
        # Never print provider bodies, which may contain sensitive material.
        return exc.code, None


def wait_ready(root: str) -> None:
    for _ in range(60):
        try:
            status, data = api("/sys/health", root)
            if status == 200 and data and data.get("initialized") and not data.get("sealed"):
                return
        except (URLError, TimeoutError, OSError):
            pass
        time.sleep(1)
    raise RuntimeError("OpenBao did not become healthy")


def assert_success(status: int, what: str):
    if status not in (200, 204):
        raise RuntimeError(f"Unexpected status for {what}: HTTP {status}")


def trial() -> dict:
    root = os.environ.get("BAO_ROOT_TEST_TOKEN")
    if not root or len(root) < 20:
        raise RuntimeError("Missing ephemeral synthetic OpenBao root token")
    wait_ready(root)
    # Real KV-v2 engine, not a mocked API.
    status, _ = api("/sys/mounts/misslea", root, "POST", {
        "type": "kv", "options": {"version": "2"}, "description": "Synthetic trial only"
    })
    assert_success(status, "mount KV")
    status, _ = api("/misslea/data/compute", root, "POST", {
        "data": {"provider_key": CANARY}
    })
    assert_success(status, "write canary")
    policy = 'path "misslea/data/compute" { capabilities = ["read"] }'
    status, _ = api("/sys/policies/acl/lab-broker-read", root, "PUT", {
        "policy": policy
    })
    assert_success(status, "create policy")
    status, issued = api("/auth/token/create", root, "POST", {
        "policies": ["lab-broker-read"], "no_default_policy": True,
        "ttl": "30m", "renewable": False
    })
    assert_success(status, "issue restricted machine token")
    machine = issued["auth"]["client_token"]
    try:
        status, secret = api("/misslea/data/compute", machine)
        read_ok = status == 200 and secret["data"]["data"]["provider_key"] == CANARY

        # Machine token MUST NOT be able to create further tokens, enumerate
        # system mounts, write any secret, or access a second secret path.
        blocked = {}
        for label, path, method, body in (
            ("new_tokens", "/auth/token/create", "POST", {"policies": ["root"]}),
            ("system_mounts", "/sys/mounts", "GET", None),
            ("secret_write", "/misslea/data/compute", "POST",
             {"data": {"provider_key": "unexpected"}}),
            ("other_secret", "/misslea/data/other", "GET", None),
        ):
            code, _ = api(path, machine, method, body)
            blocked[label] = code in (400, 403)
        if not read_ok or not all(blocked.values()):
            raise RuntimeError("Least-privilege enforcement failed")
    finally:
        code, _ = api("/auth/token/revoke", root, "POST", {"token": machine})
        assert_success(code, "revoke machine token")
    code, _ = api("/misslea/data/compute", machine)
    revoked_denied = code in (400, 403)
    if not revoked_denied:
        raise RuntimeError("Revoked token still accesses the test secret")
    return {
        "provider": "openbao",
        "mode": "isolated_ephemeral_dev_server",
        "synthetic_only": True,
        "checks": {
            "real_kv_v2": True,
            "restricted_machine_token_can_read_only_allowed_canary": read_ok,
            "out_of_scope_denied": blocked,
            "revoked_token_denied": revoked_denied,
        },
        "not_tested": [
            "independent machine authentication / production AppRole setup",
            "unlock and restore after host loss",
            "LLM-safe independently deployed credential broker",
            "deployment rights isolation",
            "durable audit and recovery root",
        ],
        "status": "PASS_SCOPED_SMOKE",
    }


if __name__ == "__main__":
    print(json.dumps(trial(), indent=2))
