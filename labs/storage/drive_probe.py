"""STO-005: browser-authorized, narrowly scoped Google Drive API lab transport.

ONLY synthetic encrypted restic repositories. No personal Drive account, no real
Miss Lea memory, no stored tokens, no unattended deployment. OAuth refresh
credentials come ONLY from a protected GitHub environment after manual approval.

The Google Drive official Python client is imported only for network operations;
the archive pack/unpack safety logic can be tested without network credentials.
"""
from __future__ import annotations

import argparse
import hashlib
import os
import re
import shutil
import tarfile
from pathlib import Path, PurePosixPath

SCOPE = "https://www.googleapis.com/auth/drive.file"
MAX_ARCHIVE_BYTES = 20 * 1024 * 1024
FILE_ID_RE = re.compile(r"^[A-Za-z0-9_-]{10,200}$")


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def pack_repository(repository: Path, destination: Path) -> None:
    if not repository.is_dir() or not (repository / "config").is_file():
        raise ValueError("Expected a complete restic repository")
    destination.parent.mkdir(parents=True, exist_ok=True)
    with tarfile.open(destination, mode="w:gz") as archive:
        # Repositories are encrypted by restic BEFORE packaging. The tar
        # container itself is not a security/encryption boundary.
        archive.add(repository, arcname="repository", recursive=True)
    if destination.stat().st_size > MAX_ARCHIVE_BYTES:
        destination.unlink()
        raise ValueError("Synthetic archive too large for STO-005")


def unpack_repository(archive: Path, destination: Path) -> Path:
    if not archive.is_file() or archive.stat().st_size > MAX_ARCHIVE_BYTES:
        raise ValueError("Missing or oversized synthetic archive")
    destination.mkdir(parents=True, exist_ok=True)
    with tarfile.open(archive, mode="r:gz") as stream:
        members = stream.getmembers()
        if len(members) > 5000 or sum(m.size for m in members) > MAX_ARCHIVE_BYTES:
            raise ValueError("Unsafe or oversized extracted archive")
        for member in members:
            name = PurePosixPath(member.name)
            # Defense-in-depth: a remote file is untrusted even when created
            # by the same application. No traversal, links, devices or escapes.
            if (not name.parts or name.parts[0] != "repository" or
                    name.is_absolute() or ".." in name.parts or
                    not (member.isfile() or member.isdir())):
                raise ValueError("Unsafe or unexpected archive member")
            target = destination.joinpath(*name.parts)
            if not target.resolve().is_relative_to(destination.resolve()):
                raise ValueError("Archive path escapes quarantine")
            if member.isdir():
                target.mkdir(parents=True, exist_ok=True)
            else:
                source = stream.extractfile(member)
                if source is None:
                    raise ValueError("Archive file missing payload")
                target.parent.mkdir(parents=True, exist_ok=True)
                with source, target.open("wb") as output:
                    shutil.copyfileobj(source, output, length=1024 * 1024)
    result = destination / "repository"
    if not (result / "config").is_file():
        raise ValueError("Restored archive lacks restic metadata")
    return result


def google_service():
    # Never log these values. Provider OAuth access is limited to files
    # created/opened by THIS app via the non-sensitive drive.file scope.
    required = ("STO005_DRIVE_CLIENT_ID", "STO005_DRIVE_CLIENT_SECRET",
                "STO005_DRIVE_REFRESH_TOKEN")
    if any(not os.getenv(name) for name in required):
        raise RuntimeError("One or more protected OAuth environment secrets are missing")
    from google.oauth2.credentials import Credentials
    from google.auth.transport.requests import Request
    from googleapiclient.discovery import build

    credentials = Credentials(
        token=None,
        refresh_token=os.environ["STO005_DRIVE_REFRESH_TOKEN"],
        token_uri="https://oauth2.googleapis.com/token",
        client_id=os.environ["STO005_DRIVE_CLIENT_ID"],
        client_secret=os.environ["STO005_DRIVE_CLIENT_SECRET"],
        scopes=[SCOPE],
    )
    credentials.refresh(Request())
    return build("drive", "v3", credentials=credentials, cache_discovery=False)


def upload(archive: Path, name: str, id_output: Path) -> None:
    if (not re.fullmatch(r"misslea-sto00[56]-synthetic-[0-9]+[.]tar[.]gz", name)
            or archive.stat().st_size > MAX_ARCHIVE_BYTES):
        raise ValueError("Invalid laboratory archive name or size")
    from googleapiclient.http import MediaFileUpload

    service = google_service()
    data = service.files().create(
        body={"name": name, "description": "STO-005 encrypted SYNTHETIC test archive only"},
        media_body=MediaFileUpload(str(archive), mimetype="application/gzip",
                                   resumable=False),
        fields="id,size,md5Checksum",
    ).execute()
    file_id = data.get("id", "")
    if not FILE_ID_RE.fullmatch(file_id):
        raise RuntimeError("Google Drive did not return a valid file identifier")
    if int(data.get("size", "-1")) != archive.stat().st_size:
        raise RuntimeError("Google Drive object size mismatch")
    # ID alone cannot access the Private Drive file; nevertheless do not echo
    # it to logs or print credentials. GH job output is internal metadata.
    id_output.write_text(file_id, encoding="utf-8")
    print("PASS: encrypted synthetic repository uploaded to independent Google Drive")


def download(file_id: str, destination: Path, expected_hash: str) -> None:
    if (not FILE_ID_RE.fullmatch(file_id)
            or not re.fullmatch(r"[0-9a-f]{64}", expected_hash)):
        raise ValueError("Invalid test object identifier or SHA-256")
    from googleapiclient.http import MediaIoBaseDownload

    service = google_service()
    request = service.files().get_media(fileId=file_id)
    destination.parent.mkdir(parents=True, exist_ok=True)
    with destination.open("wb") as output:
        downloader = MediaIoBaseDownload(output, request, chunksize=1024 * 1024)
        done = False
        while not done:
            _, done = downloader.next_chunk(num_retries=2)
            if output.tell() > MAX_ARCHIVE_BYTES:
                raise ValueError("Remote archive exceeded synthetic limit")
    if sha256(destination) != expected_hash:
        raise ValueError("Drive bytes differ from independently retained checksum")
    print("PASS: encrypted synthetic archive retrieved from Drive with verified SHA-256")


def main() -> None:
    parser = argparse.ArgumentParser()
    commands = parser.add_subparsers(dest="action", required=True)
    pack = commands.add_parser("pack")
    pack.add_argument("--repo", type=Path, required=True)
    pack.add_argument("--archive", type=Path, required=True)
    unpack = commands.add_parser("unpack")
    unpack.add_argument("--archive", type=Path, required=True)
    unpack.add_argument("--dest", type=Path, required=True)
    put = commands.add_parser("upload")
    put.add_argument("--archive", type=Path, required=True)
    put.add_argument("--name", required=True)
    put.add_argument("--id-output", type=Path, required=True)
    get = commands.add_parser("download")
    get.add_argument("--file-id", required=True)
    get.add_argument("--archive", type=Path, required=True)
    get.add_argument("--sha256", required=True)
    args = parser.parse_args()
    if args.action == "pack":
        pack_repository(args.repo, args.archive)
    elif args.action == "unpack":
        unpack_repository(args.archive, args.dest)
    else:
        try:
            if args.action == "upload":
                upload(args.archive, args.name, args.id_output)
            elif args.action == "download":
                download(args.file_id, args.archive, args.sha256)
        except Exception as exc:
            # No provider body, Authorization header or token values in logs.
            raise SystemExit("STO-005 provider operation failed (" +
                             type(exc).__name__ + ")") from None


if __name__ == "__main__":
    main()
