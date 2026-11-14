"""Deterministic offline Cloudflare service-identity lifecycle fixture.

Not an API emulation, a production secret store, or proof of provider behavior.
This deliberately tests authority boundaries before a real account is connected.
"""
from __future__ import annotations

import secrets
import tempfile
from dataclasses import dataclass
from pathlib import Path

from labs.identity.hub import AccessDenied, IdentityHub


class MockProviderDenied(PermissionError):
    """Synthetic provider rejected an action."""


@dataclass
class _Token:
    secret: str
    role: str
    worker_scope: str | None
    active: bool = True


class MockCloudflareAccount:
    """Model Cloudflare Workers Editor vs product Admin using dummy resources."""

    def __init__(self):
        self.workers = {"misslea-example": 0}
        self._tokens: dict[str, _Token] = {}

    def provision(self, *, role: str, worker_scope: str | None = None) -> str:
        """Trusted provisioner, intentionally unavailable through agent broker."""
        if role not in {"editor", "admin"}:
            raise ValueError("Only two Workers roles modeled")
        if role == "editor" and (worker_scope is None or worker_scope not in self.workers):
            raise ValueError("Editor requires an existing Worker scope")
        if role == "admin" and worker_scope is not None:
            raise ValueError("Admin is product-level in this mock")
        value = "synthetic-only-" + secrets.token_hex(16)
        self._tokens[value] = _Token(value, role, worker_scope)
        return value

    def revoke(self, secret: str) -> None:
        """Trusted provisioner, not an agent operation."""
        token = self._tokens.get(secret)
        if token is None:
            raise KeyError("Unknown synthetic identity")
        token.active = False

    def operate(self, *, secret: str, operation: str, worker: str) -> None:
        token = self._tokens.get(secret)
        if token is None or not token.active:
            raise MockProviderDenied("Inactive synthetic credential")
        if operation not in {"deploy", "create", "delete"}:
            raise MockProviderDenied("Unsupported action")
        if token.role == "editor" and (
            operation != "deploy" or token.worker_scope != worker
        ):
            raise MockProviderDenied("Editor cannot create/delete or leave its Worker scope")
        if operation == "create":
            if worker in self.workers:
                raise MockProviderDenied("Worker already exists")
            self.workers[worker] = 0
        elif operation == "deploy":
            if worker not in self.workers:
                raise MockProviderDenied("Worker does not exist")
            self.workers[worker] += 1
        else:
            if worker not in self.workers:
                raise MockProviderDenied("Worker does not exist")
            del self.workers[worker]


class MockSecretStore:
    """Simulates a separate credential resolution service; never serialized to SQLite."""

    def __init__(self):
        self._secrets: dict[str, str] = {}

    def set(self, handle: str, value: str) -> None:
        if not value:
            raise ValueError("Empty synthetic credential")
        self._secrets[handle] = value

    def resolve(self, handle: str) -> str:
        value = self._secrets.get(handle)
        if value is None:
            raise AccessDenied("Synthetic credential unavailable")
        return value


class CloudflareMockBroker:
    """Exactly scoped local grants plus separate fake Cloudflare permission checks."""

    def __init__(self, hub: IdentityHub, store: MockSecretStore,
                 cloudflare: MockCloudflareAccount, *, allowed_worker: str):
        self._hub = hub
        self._store = store
        self._cloudflare = cloudflare
        self._allowed_worker = allowed_worker

    def deploy(self, *, subject: str, resource_id: str, worker: str) -> None:
        if worker != self._allowed_worker:
            raise AccessDenied("Worker outside local capability scope")
        if not self._hub.authorize(
            subject=subject, resource_id=resource_id, action="compute.run"
        ):
            raise AccessDenied("Local grant denied")
        handle = self._hub.credential_handle(resource_id)
        self._cloudflare.operate(
            secret=self._store.resolve(handle), operation="deploy", worker=worker
        )


def synthetic_lifecycle() -> dict:
    """Exercise bootstrap, restricted access, replacement, revocation and recovery."""
    now = 1000
    cloudflare = MockCloudflareAccount()
    store = MockSecretStore()
    old = cloudflare.provision(role="editor", worker_scope="misslea-example")
    store.set("cloudflare-operator", old)

    with tempfile.TemporaryDirectory() as folder:
        first = Path(folder) / "original.sqlite"
        backup = Path(folder) / "snapshot.sqlite"
        with IdentityHub(first, execution_enabled=True, clock=lambda: now) as hub:
            hub.register_resource(
                id="cloudflare-compute-lab", provider="cloudflare", kind="compute",
                legal_holder="human-bootstrap-synthetic",
                operator="miss-lea-demo-synthetic",
                billing_party="none-no-real-account",
                recovery_authority="trusted-provisioner-synthetic",
                human_bootstrap="initial-signup-and-terms-required",
                transferability="unknown",
                credential_handle="cloudflare-operator",
            )
            grant_id = hub.grant(
                subject="miss-lea-lab", resource_id="cloudflare-compute-lab",
                action="compute.run", issued_by="trusted-bootstrap",
                expires_at=2000,
            )
            broker = CloudflareMockBroker(hub, store, cloudflare, allowed_worker="misslea-example")
            broker.deploy(subject="miss-lea-lab", resource_id="cloudflare-compute-lab",
                          worker="misslea-example")
            first_pass = cloudflare.workers["misslea-example"] == 1

            editor_cannot_create = False
            try:
                cloudflare.operate(secret=old, operation="create", worker="another")
            except MockProviderDenied:
                editor_cannot_create = True

            # Trusted provisioning and vault update; unavailable to the agent broker.
            new = cloudflare.provision(role="editor", worker_scope="misslea-example")
            store.set("cloudflare-operator", new)
            cloudflare.revoke(old)
            old_rejected = False
            try:
                cloudflare.operate(secret=old, operation="deploy", worker="misslea-example")
            except MockProviderDenied:
                old_rejected = True

            broker.deploy(subject="miss-lea-lab", resource_id="cloudflare-compute-lab",
                          worker="misslea-example")
            rotated_pass = cloudflare.workers["misslea-example"] == 2
            hub.snapshot(backup)
            inventory = hub.inventory()
            first_audit = hub.audit()

        with IdentityHub(backup, clock=lambda: now) as restored:
            restored_inactive = not restored.authorize(
                subject="miss-lea-lab", resource_id="cloudflare-compute-lab",
                action="compute.run")
        # This reenactment requires an explicit trusted harness admission.
        # Real identity verification/fencing is still NOT implemented.
        with IdentityHub(backup, execution_enabled=True, clock=lambda: now) as restored:
            recovered_broker = CloudflareMockBroker(restored, store, cloudflare, allowed_worker="misslea-example")
            recovered_broker.deploy(
                subject="miss-lea-lab", resource_id="cloudflare-compute-lab",
                worker="misslea-example")
            recovered = cloudflare.workers["misslea-example"] == 3
            restored.revoke(grant_id)
            local_revoked = not restored.authorize(
                subject="miss-lea-lab", resource_id="cloudflare-compute-lab",
                action="compute.run")

        return {
            "synthetic": True,
            "provider": "cloudflare",
            "external_calls": 0,
            "original_execution": first_pass,
            "editor_cannot_create_worker": editor_cannot_create,
            "rotation_new_credential_works": rotated_pass,
            "revoked_provider_credential_rejected": old_rejected,
            "revoked_local_grant_rejected": local_revoked,
            "restored_execution_disabled": restored_inactive,
            "explicitly_readmitted_host_works": recovered,
            "no_personal_account_used": True,
            "inventory": inventory,
            "audit": first_audit,
            "production_authentication_tested": False,
        }
