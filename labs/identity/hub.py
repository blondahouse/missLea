"""Offline-only identity/capability research fixture. NOT an authentication boundary."""
from __future__ import annotations

import re
import sqlite3
import time
import uuid
from pathlib import Path
from typing import Callable, Mapping

ACTIONS = frozenset({"compute.run", "compute.inspect", "compute.delete"})
IDENTIFIER = re.compile(r"^[a-zA-Z0-9][a-zA-Z0-9._:-]{0,95}$")
EXPECTED = {"count": 3, "sum": 10, "squares": 38}


class AccessDenied(PermissionError):
    """No capability, unavailable resource, or inactive local session."""


def _check_identifier(value: str, name: str) -> str:
    if not isinstance(value, str) or not IDENTIFIER.fullmatch(value) or value == "*":
        raise ValueError(f"Invalid {name}")
    return value


def _check_description(value: str, name: str) -> str:
    if not isinstance(value, str) or not value.strip() or len(value) > 200:
        raise ValueError(f"Invalid {name}")
    return value.strip()


class IdentityHub:
    """Resource inventory, exact-scope grants, and an append-only decision audit.

    The execution_enabled switch is for a trusted test harness, not identity
    proof. Any code able to open the DB or instantiate this class is privileged.
    Never connect real secrets/services to this research fixture.
    """

    def __init__(self, path: str | Path = ":memory:", *, execution_enabled: bool = False,
                 clock: Callable[[], int] | None = None):
        self._enabled = execution_enabled
        self._clock = clock or (lambda: int(time.time()))
        self.db = sqlite3.connect(str(path))
        self.db.row_factory = sqlite3.Row
        self.db.execute("PRAGMA foreign_keys = ON")
        self.db.executescript("""
            CREATE TABLE IF NOT EXISTS resources (
                id TEXT PRIMARY KEY, provider TEXT NOT NULL, kind TEXT NOT NULL,
                legal_holder TEXT NOT NULL, operator TEXT NOT NULL,
                billing_party TEXT NOT NULL, recovery_authority TEXT NOT NULL,
                human_bootstrap TEXT NOT NULL, transferability TEXT NOT NULL,
                credential_handle TEXT NOT NULL, status TEXT NOT NULL
                    CHECK (status IN ('active','suspended','retired'))
            );
            CREATE TABLE IF NOT EXISTS grants (
                id TEXT PRIMARY KEY, subject TEXT NOT NULL,
                resource_id TEXT NOT NULL REFERENCES resources(id),
                action TEXT NOT NULL, issued_by TEXT NOT NULL,
                expires_at INTEGER NOT NULL, revoked_at INTEGER
            );
            CREATE TABLE IF NOT EXISTS audit (
                seq INTEGER PRIMARY KEY AUTOINCREMENT, recorded_at INTEGER NOT NULL,
                subject TEXT NOT NULL, resource_id TEXT NOT NULL,
                action TEXT NOT NULL, verdict TEXT NOT NULL,
                reason TEXT NOT NULL
            );
        """)
        self.db.commit()

    def close(self) -> None:
        self.db.close()

    def __enter__(self) -> "IdentityHub":
        return self

    def __exit__(self, *_: object) -> None:
        self.close()

    def register_resource(self, *, id: str, provider: str, kind: str,
                          legal_holder: str, operator: str, billing_party: str,
                          recovery_authority: str, human_bootstrap: str,
                          transferability: str, credential_handle: str) -> None:
        """Trusted test setup only; no self-service account creation."""
        ident = _check_identifier(id, "resource ID")
        handle = _check_identifier(credential_handle, "credential handle")
        descriptions = [_check_description(value, name) for name, value in [
            ("provider", provider), ("kind", kind),
            ("legal holder", legal_holder), ("operator", operator),
            ("billing party", billing_party), ("recovery authority", recovery_authority),
            ("human bootstrap", human_bootstrap), ("transferability", transferability),
        ]]
        with self.db:
            self.db.execute("INSERT INTO resources VALUES (?,?,?,?,?,?,?,?,?,?,?)",
                            (ident, *descriptions, handle, "active"))

    def set_resource_status(self, resource_id: str, status: str) -> None:
        """Trusted test setup only; not callable via the capability broker."""
        if status not in {"active", "suspended", "retired"}:
            raise ValueError("Unknown resource status")
        with self.db:
            result = self.db.execute("UPDATE resources SET status=? WHERE id=?",
                                     (status, resource_id))
            if result.rowcount != 1:
                raise KeyError("Unknown resource")

    def grant(self, *, subject: str, resource_id: str, action: str,
              issued_by: str, expires_at: int) -> str:
        """Trusted test setup only; grants are never self-issued by a worker."""
        _check_identifier(subject, "subject")
        _check_identifier(resource_id, "resource ID")
        if action not in ACTIONS:
            raise ValueError("Action is not available in this lab")
        _check_description(issued_by, "grant issuer")
        if not isinstance(expires_at, int) or isinstance(expires_at, bool) or expires_at <= self._clock():
            raise ValueError("Expiry must be a future Unix timestamp")
        grant_id = str(uuid.uuid4())
        with self.db:
            self.db.execute("""INSERT INTO grants
                (id,subject,resource_id,action,issued_by,expires_at)
                VALUES (?,?,?,?,?,?)""",
                (grant_id, subject, resource_id, action, issued_by, expires_at))
        return grant_id

    def revoke(self, grant_id: str) -> bool:
        """Trusted test setup only; revocation takes effect at next check."""
        with self.db:
            result = self.db.execute("UPDATE grants SET revoked_at=? WHERE id=? AND revoked_at IS NULL",
                                     (self._clock(), grant_id))
        return result.rowcount == 1

    def _record(self, subject: str, resource_id: str, action: str,
                verdict: str, reason: str) -> None:
        with self.db:
            self.db.execute("""INSERT INTO audit
                (recorded_at,subject,resource_id,action,verdict,reason)
                VALUES (?,?,?,?,?,?)""",
                (self._clock(), subject, resource_id, action, verdict, reason))

    def authorize(self, *, subject: str, resource_id: str, action: str) -> bool:
        """Fail closed, exact resource+subject+action and time-bound grant."""
        reason = "authorized"
        resource = self.db.execute("SELECT status FROM resources WHERE id=?", (resource_id,)).fetchone()
        if not self._enabled:
            reason = "session_inactive"
        elif action not in ACTIONS:
            reason = "unsupported_action"
        elif resource is None:
            reason = "unknown_resource"
        elif resource["status"] != "active":
            reason = "resource_inactive"
        else:
            grant = self.db.execute("""SELECT id FROM grants WHERE subject=? AND resource_id=?
                AND action=? AND revoked_at IS NULL AND expires_at>? LIMIT 1""",
                (subject, resource_id, action, self._clock())).fetchone()
            if grant is None:
                reason = "no_valid_grant"
        self._record(subject, resource_id, action,
                     "ALLOW" if reason == "authorized" else "DENY", reason)
        return reason == "authorized"

    def credential_handle(self, resource_id: str) -> str:
        """Internal trusted-broker lookup. Never expose via inventory/agent API."""
        row = self.db.execute("SELECT credential_handle FROM resources WHERE id=?",
                              (resource_id,)).fetchone()
        if row is None:
            raise KeyError("Unknown resource")
        return str(row["credential_handle"])

    def inventory(self) -> list[dict]:
        """Portable non-secret account/dependency metadata, not authority."""
        cols = ("id", "provider", "kind", "legal_holder", "operator", "billing_party",
                "recovery_authority", "human_bootstrap", "transferability", "status")
        return [{name: row[name] for name in cols} for row in self.db.execute(
            "SELECT * FROM resources ORDER BY id")]

    def audit(self) -> list[dict]:
        return [dict(row) for row in self.db.execute(
            "SELECT recorded_at,subject,resource_id,action,verdict,reason FROM audit ORDER BY seq")]

    def snapshot(self, path: str | Path) -> None:
        """SQLite-consistent snapshot; opening it does NOT activate execution."""
        dest = sqlite3.connect(str(path))
        try:
            self.db.backup(dest)
        finally:
            dest.close()


class SyntheticBroker:
    """Trusted-host-only demonstration of mediated execution, no real APIs.

    Credentials remain in this object's process memory, not in SQLite or the
    returned result. THIS IS NOT a production secret manager or process boundary.
    """

    def __init__(self, hub: IdentityHub, credentials: Mapping[str, str]):
        self._hub = hub
        self._credentials = dict(credentials)

    def invoke(self, *, subject: str, resource_id: str, action: str) -> dict:
        if not self._hub.authorize(subject=subject, resource_id=resource_id, action=action):
            raise AccessDenied("Capability denied")
        if action != "compute.run":
            # The policy may recognize inspect/delete scopes, but the mock only
            # implements compute.run: never pretend a capability is operational.
            raise NotImplementedError("No synthetic implementation for action")
        handle = self._hub.credential_handle(resource_id)
        if not self._credentials.get(handle):
            raise AccessDenied("Credential unavailable to trusted broker")
        values = (2, 3, 5)
        return {"count": len(values), "sum": sum(values),
                "squares": sum(n * n for n in values)}
