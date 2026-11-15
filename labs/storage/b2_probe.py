"""STO-006 synthetic-only B2 transport via the standard boto3 S3 client.

Temporary, bucket-scoped B2 credentials are supplied by a protected GitHub
environment. Neither B2 key nor provider HTTP response bodies are logged.
"""
from __future__ import annotations

import argparse
import hashlib
import os
from pathlib import Path

BUCKET = "misslea-storage-lab-b2"
ENDPOINT = "https://s3.eu-central-003.backblazeb2.com"
REGION = "eu-central-003"
MAX_BYTES = 20 * 1024 * 1024


def validate_key(key: str) -> None:
    import re
    if not re.fullmatch(r"sto006/[0-9]+/memory-restic[.]tar[.]gz", key):
        raise ValueError("Unexpected object prefix")


def s3_client():
    if not os.getenv("AWS_ACCESS_KEY_ID") or not os.getenv("AWS_SECRET_ACCESS_KEY"):
        raise RuntimeError("Protected B2 application key missing")
    import boto3
    from botocore.config import Config
    return boto3.client(
        "s3",
        endpoint_url=ENDPOINT,
        region_name=REGION,
        config=Config(signature_version="s3v4", s3={"addressing_style": "path"},
                      retries={"max_attempts": 3, "mode": "standard"}),
    )


def verify_size(path: Path) -> int:
    if not path.is_file():
        raise ValueError("Archive not found")
    size = path.stat().st_size
    if size < 1 or size > MAX_BYTES:
        raise ValueError("Synthetic archive exceeds test bounds")
    return size


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def upload(path: Path, key: str, *, client=None) -> None:
    validate_key(key)
    size = verify_size(path)
    s3 = client if client is not None else s3_client()
    # Avoid a mutable shared naming convention or write outside test prefix.
    with path.open("rb") as body:
        s3.put_object(Bucket=BUCKET, Key=key, Body=body,
                      ContentType="application/gzip")
    metadata = s3.head_object(Bucket=BUCKET, Key=key)
    if int(metadata.get("ContentLength", -1)) != size:
        raise RuntimeError("Remote B2 object size mismatch")
    print("PASS: exact synthetic common-generation archive uploaded to B2")


def download(path: Path, key: str, checksum: str, *, client=None) -> None:
    import re
    validate_key(key)
    if not re.fullmatch(r"[0-9a-f]{64}", checksum):
        raise ValueError("Invalid synthetic checksum")
    s3 = client if client is not None else s3_client()
    path.parent.mkdir(parents=True, exist_ok=True)
    response = s3.get_object(Bucket=BUCKET, Key=key)
    stream = response["Body"]
    try:
        with path.open("wb") as output:
            while True:
                chunk = stream.read(1024 * 1024)
                if not chunk:
                    break
                output.write(chunk)
                if output.tell() > MAX_BYTES:
                    raise ValueError("B2 download exceeds synthetic limit")
    finally:
        stream.close()
    verify_size(path)
    if sha256(path) != checksum:
        raise ValueError("B2 archive SHA-256 mismatch")
    print("PASS: synthetic archive downloaded from B2 with exact SHA-256")


def main() -> None:
    parser = argparse.ArgumentParser()
    commands = parser.add_subparsers(dest="command", required=True)
    for command in ("upload", "download"):
        p = commands.add_parser(command)
        p.add_argument("--path", type=Path, required=True)
        p.add_argument("--key", required=True)
        if command == "download":
            p.add_argument("--sha256", required=True)
    args = parser.parse_args()
    try:
        if args.command == "upload":
            upload(args.path, args.key)
        else:
            download(args.path, args.key, args.sha256)
    except Exception as exc:
        # boto3 may attach request URL/authorization context to an exception.
        # We intentionally report *only* the class without the provider body.
        raise SystemExit("STO-006 B2 transport failed (" +
                         type(exc).__name__ + ")") from None


if __name__ == "__main__":
    main()
