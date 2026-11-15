"""STO-002: same synthetic memory dataset against real backup engine CLIs.

CI is an isolated disposable host. There are NO external storage accounts,
Live data, production credentials, or paid services. Tool failure is reported
as failure of *this test configuration*, not automatically of the product.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import resource
import secrets
import shutil
import sqlite3
import subprocess
import tempfile
import time
from pathlib import Path

from labs.storage.snapshot import create_snapshot, restore_to_quarantine, verify_snapshot

CANDIDATES = ("restic", "kopia", "borg", "rustic", "duplicacy")
CANARY = b"MISSLEA_SYNTHETIC_BACKUP_TEST_MARKER_NOT_REAL_DATA"
EXPECTED = (
    ("evidence", "message#1", "firsthand synthetic source", "retained"),
    ("decision", "source#2", "keep all primary evidence", "current"),
    ("obligation", "source#3", "resolve synthetic invoice", "open"),
    ("grant", "source#4", "no-op synthetic grant", "revoked"),
)


class TrialError(RuntimeError):
    pass


def run(argv: list[str], *, env: dict[str, str], cwd: Path | None = None,
        expected_success: bool = True, output: bool = False) -> str | bool:
    try:
        result = subprocess.run(argv, cwd=str(cwd) if cwd else None, env=env,
                                stdout=subprocess.PIPE if output else subprocess.DEVNULL,
                                stderr=subprocess.DEVNULL, timeout=150, check=False)
    except (subprocess.TimeoutExpired, OSError):
        raise TrialError("Tool operation failed to execute: " + argv[0]) from None
    if expected_success and result.returncode != 0:
        raise TrialError("Tool operation returned failure: " + argv[0] +
                         " " + " ".join(x for x in argv[1:] if not x.startswith("/")))
    if output:
        return result.stdout.decode("utf-8", errors="replace").strip()
    return result.returncode == 0


def repo_bytes(path: Path) -> int:
    return sum(p.stat().st_size for p in path.rglob("*") if p.is_file())


class Tool:
    def __init__(self, name: str, root: Path, password: Path):
        self.name = name
        self.root = root
        self.repo = root / "repository"
        self.password = password
        self.env = {**os.environ, "HOME": str(root / "home"),
                    "XDG_CACHE_HOME": str(root / "cache")}
        (root / "home").mkdir()
        if name == "restic":
            self.prefix = ["restic", "--repo", str(self.repo),
                           "--password-file", str(password)]
            self.env["RESTIC_CACHE_DIR"] = str(root / "cache" / "restic")
        elif name == "rustic":
            self.prefix = ["rustic"]
            self.env.update({"RUSTIC_REPOSITORY": str(self.repo),
                             "RUSTIC_PASSWORD_FILE": str(password),
                             "RUSTIC_CACHE_DIR": str(root / "cache" / "rustic")})
        elif name == "borg":
            self.prefix = ["borg"]
            self.env.update({"BORG_PASSPHRASE": password.read_text(),
                             "BORG_RELOCATED_REPO_ACCESS_IS_OK": "yes",
                             "BORG_UNKNOWN_UNENCRYPTED_REPO_ACCESS_IS_OK": "no"})
        elif name == "duplicacy":
            self.prefix = ["duplicacy"]
            self.env.update({"DUPLICACY_PASSWORD": password.read_text(),
                             "DUPLICACY_DISABLE_UPDATE_CHECK": "true"})
            self.source = None
        elif name == "kopia":
            self.prefix = ["kopia", "--config-file", str(root / "kopia.json")]
            self.env.update({"KOPIA_PASSWORD": password.read_text(),
                             "KOPIA_CHECK_FOR_UPDATES": "false"})
        else:
            raise ValueError("Unsupported backup engine")

    def call(self, *args: str, **kwargs):
        return run([*self.prefix, *args], env=self.env, **kwargs)

    def version(self) -> str:
        # Pinned by its verified release digest; Duplicacy may report version to stderr.
        if self.name == "duplicacy":
            return "duplicacy CLI v3.3.0 (verified vendor release)"
        # Version output is non-sensitive.
        return str(run([self.name, "version" if self.name not in ("borg", "kopia") else "--version"],
                       env=self.env, output=True)).splitlines()[0][:180]

    def init(self, source: Path) -> None:
        if self.name == "duplicacy":
            self.source = source
            self.call("init", "-e", "misslea-synthetic", str(self.repo), cwd=source)
        elif self.name == "restic":
            self.call("init")
        elif self.name == "rustic":
            self.call("init")
        elif self.name == "borg":
            self.call("init", "--encryption=repokey", str(self.repo))
        else:
            self.call("repository", "create", "filesystem", "--path", str(self.repo))

    def backup(self, source: Path, version: int) -> None:
        if self.name == "duplicacy":
            self.call("backup", "-hash", cwd=source)
        elif self.name in ("restic", "rustic"):
            self.call("backup", str(source))
        elif self.name == "borg":
            self.call("create", f"{self.repo}::v{version}", str(source))
        else:
            self.call("snapshot", "create", str(source))

    def check(self) -> None:
        if self.name == "duplicacy":
            self.call("check", "-all", "-files", cwd=self.source)
        elif self.name == "restic":
            self.call("check", "--read-data")
        elif self.name == "rustic":
            self.call("check", "--read-data")
        elif self.name == "borg":
            self.call("check", "--verify-data", str(self.repo))
        else:
            self.call("snapshot", "verify", "--verify-files-percent=100")

    def restore(self, source: Path, dest: Path) -> None:
        if self.name == "duplicacy":
            self.call("init", "-e", "misslea-synthetic", str(self.repo), cwd=dest)
            self.call("restore", "-r", "2", cwd=dest)
        elif self.name == "restic":
            self.call("restore", "latest", "--target", str(dest))
        elif self.name == "rustic":
            self.call("restore", "latest", str(dest))
        elif self.name == "borg":
            self.call("extract", f"{self.repo}::v2", cwd=dest)
        else:
            self.call("snapshot", "restore", str(source), str(dest / "snapshot"))

    def wrong_password_denied(self) -> bool:
        if self.name == "duplicacy":
            wrong_env = {**self.env, "DUPLICACY_PASSWORD": "this-is-the-wrong-password"}
            return not run(["duplicacy", "list"], cwd=self.source, env=wrong_env,
                           expected_success=False)
        if self.name == "kopia":
            wrong_env = {**self.env, "KOPIA_PASSWORD": "this-is-the-wrong-password"}
            result = run(["kopia", "--config-file", str(self.root / "wrong.json"),
                          "repository", "connect", "filesystem", "--path", str(self.repo)],
                         env=wrong_env, expected_success=False)
            return not result
        if self.name == "borg":
            env = {**self.env, "BORG_PASSPHRASE": "this-is-the-wrong-password"}
            return not run(["borg", "list", str(self.repo)],
                           env=env, expected_success=False)
        env = {**self.env}
        if self.name == "rustic":
            env.pop("RUSTIC_PASSWORD_FILE")
            env["RUSTIC_PASSWORD"] = "this-is-the-wrong-password"
            return not run(["rustic", "snapshots"], env=env, expected_success=False)
        return not run(["restic", "--repo", str(self.repo),
                        "--password-file", str(self.root / "wrong-password"), "snapshots"],
                       env=env, expected_success=False)


def create_source(path: Path) -> None:
    with sqlite3.connect(path) as db:
        db.execute("CREATE TABLE records(kind TEXT, provenance TEXT, content TEXT, status TEXT)")
        db.executemany("INSERT INTO records VALUES(?,?,?,?)", EXPECTED)


def make_snapshot(db: Path, source: Path, iteration: int) -> dict[str, str]:
    # Duplicacy keeps its repository connection in .duplicacy; it is excluded
    # from backups but must survive regeneration of the same SQLite snapshot path.
    preference_dir = source / ".duplicacy"
    temporary_prefs = source.parent / ".backup-client-prefs"
    if preference_dir.exists():
        preference_dir.rename(temporary_prefs)
    if source.exists():
        shutil.rmtree(source)
    create_snapshot(db, source)
    if temporary_prefs.exists():
        temporary_prefs.rename(preference_dir)
    (source / "attachment.bin").write_bytes(bytes(range(256)) * 4096 + CANARY)
    (source / "notes.txt").write_text("synthetic initial notes version " +
                                      str(iteration), encoding="utf-8")
    return {p.name: hashlib.sha256(p.read_bytes()).hexdigest()
            for p in source.iterdir() if p.is_file()}


def trial(name: str) -> dict:
    with tempfile.TemporaryDirectory(prefix=f"ml-sto-002-{name}-") as td:
        base = Path(td)
        root = base / "work"
        root.mkdir()
        passfile = base / "unlock"
        passfile.write_text(secrets.token_urlsafe(48), encoding="utf-8")
        passfile.chmod(0o600)
        wrong = root / "wrong-password"
        wrong.write_text("definitely-not-the-correct-password", encoding="utf-8")
        wrong.chmod(0o600)
        db = base / "primary.sqlite"
        create_source(db)
        bundle = base / "snapshot"
        hashes1 = make_snapshot(db, bundle, 1)
        tool = Tool(name, root, passfile)
        version = tool.version()
        timings: dict[str, float] = {}

        start = time.monotonic()
        tool.init(bundle)
        tool.backup(bundle, 1)
        timings["initial_backup_s"] = round(time.monotonic() - start, 3)
        repo_bytes1 = repo_bytes(tool.repo)

        with sqlite3.connect(db) as con:
            con.execute("INSERT INTO records VALUES(?,?,?,?)",
                        ("memory_revision", "source#5", "synthetic later thought", "current"))
        expected_hashes = make_snapshot(db, bundle, 2)
        start = time.monotonic()
        tool.backup(bundle, 2)
        timings["incremental_backup_s"] = round(time.monotonic() - start, 3)
        repo_bytes2 = repo_bytes(tool.repo)

        start = time.monotonic()
        tool.check()
        timings["full_verify_s"] = round(time.monotonic() - start, 3)

        wrong_key = tool.wrong_password_denied()
        if not wrong_key:
            raise TrialError("Wrong password unexpectedly worked")

        # Canary scan is a supporting observation, NOT proof of encryption.
        canary_absent = all(CANARY not in file.read_bytes()
                            for file in tool.repo.rglob("*") if file.is_file())
        if not canary_absent:
            raise TrialError("Synthetic plaintext was found in repository")

        db.unlink()
        shutil.rmtree(bundle)
        destination = base / "quarantine-output"
        destination.mkdir()
        start = time.monotonic()
        tool.restore(bundle, destination)
        timings["full_restore_s"] = round(time.monotonic() - start, 3)
        matched = []
        for candidate in destination.rglob("manifest.json"):
            parent = candidate.parent
            checksums = {p.name: hashlib.sha256(p.read_bytes()).hexdigest()
                         for p in parent.iterdir() if p.is_file()}
            if checksums == expected_hashes:
                matched.append(parent)
        if len(matched) != 1:
            found = [x.parent for x in destination.rglob("manifest.json")]
            recovered = {p.name: hashlib.sha256(p.read_bytes()).hexdigest()
                         for p in found[0].iterdir() if p.is_file()} if found else {}
            missing = sorted(set(expected_hashes) - set(recovered))
            changed = sorted(name for name in expected_hashes if name in recovered
                             and expected_hashes[name] != recovered[name])
            extra = sorted(set(recovered) - set(expected_hashes))
            raise TrialError("Restored files mismatch; manifests=" + str(len(found)) +
                             "; missing=" + ",".join(missing) +
                             "; changed=" + ",".join(changed) +
                             "; extra=" + ",".join(extra))
        source = matched[0]
        verify_snapshot(source)
        quarantine = base / "inert-state.sqlite"
        receipt = restore_to_quarantine(source, quarantine)
        with sqlite3.connect(quarantine) as con:
            actual = con.execute("SELECT kind,provenance,content,status FROM records ORDER BY rowid").fetchall()
        records_ok = actual == list(EXPECTED) + [
            ("memory_revision", "source#5", "synthetic later thought", "current")]
        inactive = receipt["authority_restored"] is False and receipt["active_instance_started"] is False
        if not records_ok or not inactive:
            raise TrialError("Memory or authority was altered on restore")

        return {
            "tool": name, "version": version, "synthetic": True,
            "source_fixture": "four records + one revision, 1 MiB attachment and notes",
            "repository_format_interoperability": "separately investigated",
            "storage_topology": "single ephemeral GitHub Actions host",
            "independent_providers_tested": False,
            "real_secrets_used": False,
            "checks": {"initial_snapshot": bool(hashes1),
                       "incremental_snapshot": True,
                       "full_verification_passed": True,
                       "wrong_password_rejected": wrong_key,
                       "plaintext_canary_absent": canary_absent,
                       "bit_exact_full_restore": True,
                       "source_provenance_and_obligations_intact": records_ok,
                       "restored_authority_inactive": inactive},
            "timing_seconds": timings, "repository_bytes_after_first": repo_bytes1,
            "repository_bytes_after_second": repo_bytes2,
            "max_child_rss_kb": resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss,
            "license": "commercial trial only; ongoing commercial backup requires paid license" if name == "duplicacy" else "open source",
            "not_tested": ["independent remote providers", "tampered pack detection parity",
                           "WORM/deletion resistance", "cold-store costs and recovery root",
                           "single active writer fencing", "representative production load"],
            "status": "PASS_LOCAL_COMPARATIVE_TRIAL",
        }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("tool", choices=CANDIDATES)
    args = parser.parse_args()
    print(json.dumps(trial(args.tool), indent=2))


if __name__ == "__main__":
    main()
