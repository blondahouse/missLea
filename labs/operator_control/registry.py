"""Portable, secret-free account manifest validator."""
from __future__ import annotations
import json
import re

SERVICES={"cloudflare","google","github","infisical"}
HANDLE=re.compile(r"^(ROOT|OPS):[A-Z][A-Z0-9_]{2,79}$")


def validate_manifest(blob):
    if not isinstance(blob,dict) or blob.get("version")!=1 or not isinstance(blob.get("accounts"),list):
        raise ValueError("invalid_manifest")
    ids=set()
    for a in blob["accounts"]:
        if not isinstance(a,dict) or set(a)!={"id","provider","principal","legal_holder",
                "operator","billing_party","recovery_authority","root_ref","ops_ref"}:
            raise ValueError("invalid_account_shape")
        if not isinstance(a["id"],str) or not re.fullmatch(r"[a-z0-9-]{3,64}",a["id"]) or a["id"] in ids:
            raise ValueError("duplicate_or_invalid_id")
        ids.add(a["id"])
        if a["provider"] not in SERVICES:
            raise ValueError("unknown_service")
        if not HANDLE.fullmatch(a["root_ref"]) or not HANDLE.fullmatch(a["ops_ref"]):
            raise ValueError("invalid_secret_reference")
        if not a["root_ref"].startswith("ROOT:") or not a["ops_ref"].startswith("OPS:"):
            raise ValueError("tier_mismatch")
        for field in ("principal","legal_holder","operator","billing_party","recovery_authority"):
            if not isinstance(a[field],str) or not 1<=len(a[field])<=160:
                raise ValueError("invalid_account_metadata")
    return blob


def public_account_index(blob):
    validate_manifest(blob)
    return [{k:a[k] for k in ("id","provider","principal","legal_holder","operator","billing_party")}
            for a in blob["accounts"]]
