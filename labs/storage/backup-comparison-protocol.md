# STO-002 — Five-way backup engine comparison (prospective protocol)

**Recorded:** 2026-11-15, before comparative tests. **Research only:** synthetic evidence; no account creation, cloud billing, Live integration, or use of the running agent's state. This is a child of [STO-001](selection-criteria.md) and does not reopen its primary-database selection.

## Decision

Choose an **encrypted backup engine** appropriate for a portable, mostly autonomous Miss Lea, without choosing the primary database or remote storage providers. Comparing **restic, Kopia, BorgBackup, rustic and Duplicacy CLI** is required. A product must not be eliminated because a different candidate was tested first.

### Explicit eligibility and fairness

- **Mandatory B1 — lawful repeatable use at Demo and anticipated revenue-generating Live:** no undocumented "personal-use" assumption; if licensing is unclear, mark `LICENSE_UNRESOLVED`, not FAIL or PASS.
- **Mandatory B2 — authenticated encryption and key separation:** trusted client can back up a synthetic snapshot without leaking a plaintext marker to the repository; wrong password must not restore. Tamper detection through full verification or restore.
- **Mandatory B3 — exact verified restore:** source SQLite records, provenance, unresolved obligation, revoked permission and attached bytes are restored bit-for-bit from an archive after original loss.
- **Mandatory B4 — non-authoritative restore:** restored data is quarantined, not run; restoring a database record never grants current API privileges.
- **Mandatory B5 — operational survivability:** a documented way to relocate to a clean host and restore using separately held recovery credentials; independently protected copies without one common deletion authority remain an **STO-001 integration requirement**, not something two local directories prove.
- **Mandatory B6 — practical backend fit:** supports at least one credible remote backend without a required paid-only proprietary subscription for the tool itself. Cloud provider quotas, external storage permissions, and billing require separate verification.
- **Mandatory B7 — security boundary:** a read/write backup process cannot by itself be trusted to protect old generations from malicious deletion; require an independent retention/WORM/append-only plan and verify before Demo adoption.

**Tradeoffs:** T1 median first/incremental backup and restore wall time on identical runner/fixture; T2 archive footprint and peak memory; T3 complexity of unattended maintenance/rotation and multi-writer/locking behavior; T4 recovery/key export portability; T5 remote targets (SFTP, S3, native Google Drive, rclone) and vendor lock-in. No default weight scores. Tie-break after all mandatory PASS: minimal ongoing operation burden, then cost, then simpler portability.

**Stop:** after every eligible candidate has comparable minimum evidence (or a documented blocker) and material differences are documented, produce a SELECT / DEFER decision. **No winner** if unresolved mandatory gates affect selection. Legacy restic results were obtained *before* this protocol; they remain historical evidence, not a baseline that determines the criteria.

## Candidate inventory before trials

| Candidate | License consideration | Distinct topology or benefit | Main risk to prove |
| --- | --- | --- | --- |
| **restic** | BSD-2-Clause open source | Encrypted deduplicated CLI; diverse backends via built-in integrations/rclone/REST | External schedule and retention; backup deletion rights |
| **Kopia 0.23.1** | Apache-2.0 open source | Encrypted snapshots, compression, policies/maintenance, S3/SFTP/Google Drive | Maintenance owner after host change; native Drive and rclone integrations explicitly experimental |
| **BorgBackup 1.4.x** | BSD open source | Efficient SSH/filesystem encrypted archive, append-only server option | Less direct object-store compatibility; server-side deletion authority and restore migration |
| **rustic 0.11.4** | Apache-2.0 or MIT open source | Rust client, configurable/multiple backends, restic-compatible format | Cross-client concurrency/locking and version compatibility |
| **Duplicacy CLI 3.3.0** | Source available; **free personal use, commercial backup requires paid license** | Lock-free multi-client backup and copy, several remote targets | Autonomous commercial use eligibility/cost, repo integrity and maintenance |

**Duplicacy trial rule (prospectively updated before first Duplicacy execution):** the official CLI license explicitly permits **commercial trials**, so one disposable synthetic evaluation is permitted. Pin release v3.3.0 and its official SHA-256 asset digest. This does **not** grant a free permanent commercial backup license; operational B1 for Live remains **CONDITIONAL_ON_LICENSE** and its annual cost is part of the comparison. Trial execution may not use real business or agent data.

**rustic trial rule:** because rustic reads restic repositories, compare both its own encrypted local repository and a **read-only restore of an existing restic archive** where compatible; never run competing retention/prune writers against the same repository.

## Minimum equivalently controlled workload

Pinned Ubuntu 24.04 GitHub Actions image; use the **same deterministic source fixture** for each candidate and record actual tool version.

1. Build an **application-consistent SQLite snapshot** of four synthetic records (source evidence, decision rationale, pending obligation, revoked grant), one attachment, and a deterministic extra file. All original data remains outside Git.
2. Initialize a fresh encrypted local repository with a randomly generated 48-byte-equivalent credential *outside* the backed-up directory. Record timings separately: initial backup, second backup after a small source modification, exhaustive verification (where supported), and full restore.
3. Lose original source. Recover into a **new quarantine directory**, compare complete SHA-256 manifest and SQLite records. No executable state or permission is restored.
4. Check wrong password refusal; inspect all archive bytes for a deliberately unique synthetic plaintext canary. Tamper test a copied archive, leaving the good archive intact; report `NOT_TESTED` if the candidate's API does not support a meaningful full check.
5. Report measured archive size, installed version, sample/runtime context, and every missing check. Never print or upload passwords, canary text, host keys or private provider data.

**Critical comparability caveats:** tools use distinct defaults, file-chunking, cache and packaging. Sizes and timings measured on a small CI fixture are **illustrative only**, not a robust performance ranking; no production conclusions without repeated realistic workload samples. Never call `check` equivalent if it only scans metadata and then claim ciphertext integrity was verified. A restore/rehash is authoritative for the tested snapshot.

## Separate hard integration gates still open (STO-001)

No local experiment establishes two *independent* providers, credential blast radius, deletion-resistant generations, recoverable unlock roots, sustained operating cost, reliable RPO/RTO, or active-instance fencing. Success here is **candidate backup engine evidence**, not selection of an end-to-end storage topology.

### Sources (official, accessed 2026-11-15)

- [restic repository and security](https://restic.readthedocs.io/en/stable/100_references.html)
- [Kopia command line](https://kopia.io/docs/reference/command-line/), [consistency](https://kopia.io/docs/advanced/consistency/), [maintenance owner](https://kopia.io/docs/advanced/maintenance/), [remote repositories/experimental Google Drive](https://kopia.io/docs/repositories/)
- [Borg 1.4 encryption](https://borgbackup.readthedocs.io/en/stable/usage/init.html), [full verify](https://borgbackup.readthedocs.io/en/stable/usage/check.html)
- [rustic compared to restic](https://rustic.cli.rs/docs/comparison-restic.html), [restore](https://rustic.cli.rs/docs/commands/restore/intro.html)
- [Duplicacy commercial licensing](https://duplicacy.com/buy.html), [CLI releases](https://github.com/gilbertchen/duplicacy/releases)
- [STO-001](selection-criteria.md) and [Evaluation policy](../../docs/evaluation-policy.md)
