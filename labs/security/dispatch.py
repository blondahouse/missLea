"""Manual-only protected invocation of the synthetic Cloudflare Worker.

No Cloudflare account API key required. No general code execution.
"""
from __future__ import annotations

import argparse
import getpass
import json
import os
import sys
from urllib.error import HTTPError, URLError
from urllib.parse import urlsplit
from urllib.request import HTTPRedirectHandler, Request, build_opener


class NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


def valid_endpoint(url: str) -> bool:
    try:
        parsed = urlsplit(url)
        return (parsed.scheme == "https" and
                parsed.hostname is not None and
                parsed.hostname.endswith(".workers.dev") and
                parsed.username is None and parsed.password is None and
                parsed.port is None and
                parsed.path == "/run" and
                not parsed.query and not parsed.fragment)
    except ValueError:
        return False


def submit(url: str, token: str, values: list[int], *, opener=None) -> dict:
    if not valid_endpoint(url):
        raise ValueError("Expected an HTTPS *.workers.dev/run endpoint")
    if not (isinstance(token, str) and len(token) >= 32 and len(token) <= 256
            and all(c.isascii() and (c.isalnum() or c in "-_") for c in token)):
        raise ValueError("Token must be 32–256 URL-safe characters")
    if not (0 < len(values) <= 16 and
            all(type(v) is int and -1000 <= v <= 1000 for v in values)):
        raise ValueError("Values must be 1–16 small integers")

    data = json.dumps({"task": "sum_squares", "values": values}).encode("utf-8")
    req = Request(url, data=data, method="POST", headers={
        "Authorization": "Bearer " + token,
        "Content-Type": "application/json",
        "Accept": "application/json",
    })
    transport = opener or build_opener(NoRedirect())
    try:
        with transport.open(req, timeout=15) as response:
            if response.status != 200:
                raise RuntimeError("Worker did not return HTTP 200")
            result = json.loads(response.read(4096))
    except HTTPError as exc:
        # Never echo the HTTP error body: it could include attacker-supplied data.
        raise RuntimeError(f"Worker rejected the request (HTTP {exc.code})") from None
    except (URLError, TimeoutError, OSError, json.JSONDecodeError):
        raise RuntimeError("Unable to complete or parse the Worker request") from None
    if not isinstance(result, dict) or result.get("status") != "ok":
        raise RuntimeError("Unexpected Worker result")
    actual = result.get("result")
    expected = {"count": len(values), "sum": sum(values),
                "squares": sum(v * v for v in values)}
    if actual != expected:
        raise RuntimeError("Worker result did not match expected computation")
    return {"status": "PASS", "result": actual, "remote_job": "synchronous_synthetic"}


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="Manually send a synthetic task to Cloudflare")
    parser.add_argument("--endpoint", required=True, help="HTTPS *.workers.dev/run")
    parser.add_argument("--values", default="2,3,5", help="Comma-separated small integers")
    args = parser.parse_args(argv)
    try:
        values = [int(v.strip()) for v in args.values.split(",")]
        token = os.environ.get("MISSLEA_TASK_TOKEN") or getpass.getpass(
            "Worker task token (input hidden): "
        )
        result = submit(args.endpoint, token, values)
    except (ValueError, RuntimeError) as exc:
        # Do not include credential, request body, or remote response text.
        print(f"FAIL: {exc}", file=sys.stderr)
        return 1
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
