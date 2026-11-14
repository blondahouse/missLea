"""Cloudflare account-owned service identity admission: read-only live verification.

Only the verify endpoint is accessible. No account, token, or Worker mutations.
This is NOT a credential vault, authentication server or rights attestation.
"""
from __future__ import annotations

import json
import re
from typing import Callable
from urllib.error import HTTPError, URLError
from urllib.request import HTTPRedirectHandler, Request, build_opener

ACCOUNT_ID_RE = re.compile(r"^[a-fA-F0-9]{32}$")
TOKEN_ID_RE = re.compile(r"^[a-fA-F0-9]{32}$")
API_ORIGIN = "https://api.cloudflare.com"
ROLES = {
    "existing_worker": {
        "scope": "individual Worker",
        "role": "Editor",
        "can_create_new_worker": False,
        "can_edit_existing_worker": True,
        "can_delete_worker": False,
        "note": "Requires a Worker created separately during bootstrap",
    },
    "new_workers": {
        "scope": "Workers product on a dedicated account",
        "role": "Admin",
        "can_create_new_worker": True,
        "can_edit_existing_worker": True,
        "can_delete_worker": True,
        "note": "Broader authority; use only inside a dedicated isolated account",
    },
}


class CloudflareAdmissionError(RuntimeError):
    """No raw provider responses or authentication material in messages."""


def token_format(value: str) -> str:
    """A format hint, NOT proof of token ownership or permissions."""
    if value.startswith("cfat_"):
        return "account-token-format"
    if value.startswith("cfut_"):
        return "user-token-format"
    return "legacy-or-unknown"


def http_verify(account_id: str, token: str) -> dict:
    """Read-only account-owned token verification; fixed endpoint, no redirects."""
    url = API_ORIGIN + "/client/v4/accounts/" + account_id + "/tokens/verify"
    request = Request(url, method="GET", headers={
        "Authorization": "Bearer " + token,
        "Accept": "application/json",
    })
    class DenyRedirect(HTTPRedirectHandler):
        def redirect_request(self, req, fp, code, msg, headers, newurl):
            return None

    try:
        with build_opener(DenyRedirect()).open(request, timeout=12) as response:
            data = response.read(16385)
    except (HTTPError, URLError, TimeoutError, OSError) as exc:
        # Deliberately omit raw HTTP bodies, URLs and token-bearing exceptions.
        raise CloudflareAdmissionError("Cloudflare verification transport failed") from None
    if len(data) > 16384:
        raise CloudflareAdmissionError("Verification response too large")
    try:
        response = json.loads(data)
    except (ValueError, UnicodeDecodeError):
        raise CloudflareAdmissionError("Invalid verification response") from None
    if not isinstance(response, dict):
        raise CloudflareAdmissionError("Unexpected verification response")
    return response


def verify_service_identity(*, account_id: str, token: str,
                            request: Callable[[str, str], dict] = http_verify,
                            expected_token_id: str | None = None) -> dict:
    """Return redacted evidence, never return/pass through the token value.

    A PASS proves an active credential for the supplied account but does not prove
    its account-owned origin, precise roles, financial caps, or legal ownership.
    """
    if not ACCOUNT_ID_RE.fullmatch(account_id):
        raise ValueError("Account ID must be 32 hex characters")
    if not isinstance(token, str) or not token:
        raise ValueError("Missing token")
    if expected_token_id is not None and not TOKEN_ID_RE.fullmatch(expected_token_id):
        raise ValueError("Expected token ID must be 32 hex characters")
    response = request(account_id, token)
    if not isinstance(response, dict) or response.get("success") is not True:
        raise CloudflareAdmissionError("Cloudflare rejected token verification")
    data = response.get("result")
    if not isinstance(data, dict):
        raise CloudflareAdmissionError("Cloudflare did not provide token status")
    token_id, status = data.get("id"), data.get("status")
    if not isinstance(token_id, str) or not TOKEN_ID_RE.fullmatch(token_id):
        raise CloudflareAdmissionError("Cloudflare returned invalid token ID")
    if status not in ("active", "disabled", "expired"):
        raise CloudflareAdmissionError("Cloudflare returned unknown token status")
    matches = expected_token_id is None or token_id.lower() == expected_token_id.lower()
    # The prefix is only a hint. Old Cloudflare tokens may lack cfat_/cfut_.
    format_hint = token_format(token)
    admitted = status == "active" and matches and format_hint != "user-token-format"
    return {
        "provider": "cloudflare",
        "account_id": account_id,
        "token_id": token_id,
        "token_status": status,
        "token_format_hint": format_hint,
        "expected_token_matches": matches if expected_token_id is not None else None,
        "credential_active": status == "active",
        "admission": "verified_active_not_scoped" if admitted else "blocked",
        "account_ownership_verified": False,
        "token_permissions_verified": False,
        "legal_account_holder_verified": False,
        "external_requests": 1,
        "note": "Read-only active-token verification; actual account ownership and Workers role require separate evidence.",
    }


def role_guidance(mode: str) -> dict:
    if mode not in ROLES:
        raise ValueError("Unknown Cloudflare Workers mode")
    return {"mode": mode, **ROLES[mode]}
