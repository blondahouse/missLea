# STO-002 — Five backup engines: comparative results (2026-11-15)

**Status:** comparative **local synthetic** trials completed. **Decision:** no production backup engine selected, pending STO-001 storage provider independence, deletion/recovery rights and key custody gates. [Predeclared protocol](backup-comparison-protocol.md); [original durable storage criteria](selection-criteria.md).

## Verified runs and configuration

- [GitHub Actions successful five-engine + cross-client run #43709840284](https://github.com/blondahouse/missLea/actions/runs/43709840284) on revision `b32b81ccdf27329a56c76abe3e366903a9dbdd02`.
- All five versions were actually executed on ephemeral Ubuntu 24.04; pinned official SHA-256 downloads were used for Kopia, rustic and Duplicacy. Ubuntu repositories provided restic and Borg.
- Each CLI received the same **application-consistent synthetic SQLite snapshot**, one ~1 MiB compressible attachment and a second version of the records. Each performed initial and incremental encrypted backup, its strongest included verification operation, wrong-password refusal and bit-exact recovery to a **quarantined, non-executable** database retaining provenance, obligations, and a revoked-grant record.
- No user's Mac, personal Google Drive, real Cloudflare token, real memory, paid account or remote storage provider was used. A pass **does not** mean production-ready or resistant to malicious administrator deletion.

| Engine (actual version) | Real CLI backup, password rejection, full restore | Final local repo size (2 generations) | Initial backup incl. repository init | Incremental | Verify | Restore |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| **restic 0.16.4** | **PASS** | 7,402 B | 3.785 s | 0.765 s | 0.766 s | 0.766 s |
| **Kopia 0.23.1** | **PASS** (explicit `zstd` policy) | 36,218 B | 0.793 s | 0.214 s | 0.164 s | 0.164 s |
| **BorgBackup 1.2.8** | **PASS** | 53,017 B | 0.429 s | 0.214 s | 0.214 s | 0.215 s |
| **rustic 0.11.4** | **PASS** | 7,309 B | 0.529 s | 0.265 s | 0.365 s | 0.265 s |
| **Duplicacy CLI 3.3.0** | **PASS** (forced `backup -hash`) | 10,182 B | 0.331 s | 0.165 s | 0.065 s | 0.096 s |

**Do not rank by these numbers.** One very small, highly compressible CI fixture and one run per configuration are inadequate performance benchmarks. Repository overhead, compression, cache policy, key-derivation cost, defaults and shared-runner noise differ. Initial restic time includes repository initialization; Kopia's *default* is **no compression**, which initially produced ~1.1 MB on this fixture. Its measured line above explicitly enables `zstd`, following [Kopia's official guidance](https://kopia.io/docs/faqs/). Memory figure is maximum RSS of child processes, not a reliable per-command isolated peak and is therefore excluded from ranking. All sizes are entire local repositories, not exact ciphertext payload size.

### Findings that materially change operational design

1. **Duplicacy change detection is a real reliability consideration.** An initial test occasionally restored the *previous* contents of recently overwritten SQLite snapshot files even when the backup completed, because Duplicacy defaults to comparing size/mtime and our synthetic snapshots were rewritten quickly. Using **`duplicacy backup -hash`** resolved the issue and the successful five-way run explicitly uses it. Hash mode reads every file, trading CPU/I/O for correctness. See the [documented behavior](https://forum.duplicacy.com/t/backup-command-details/1077). This is a tested configuration issue, **not** a claim that the product is generally defective. Its trial was conducted under vendor-permitted commercial evaluation, **not** an ongoing free commercial license.
2. **Kopia default compression is off.** Fair evaluation must specify a compression policy; we used `zstd` to avoid a misleading inflated archive. Kopia's built-in policy and maintenance features might lower the amount of orchestration we must write; its experimental Google Drive/rclone paths and maintenance-owner handoff require more careful investigation before selecting them.
3. **Borg append-only is relevant to Sustainability.** Borg has a documented remote `borg serve --append-only` setup that can stop a compromised backup client from physically deleting committed segments, provided the client cannot directly modify the server-side repository and cannot access a more privileged SSH identity. This is a promising D5/B7 control, **not yet tested in this PR**. Its SSH/local-first topology is less convenient if we ultimately need native S3/object storage.
4. **rustic and restic can recover one another's snapshots.** [Cross-client CI](https://github.com/blondahouse/missLea/actions/runs/43709840284) successfully performed read-only **restic → rustic** and **rustic → restic** restore, confirmed original record hashes and inactive authority. **Do not concurrently run writers or prune between them:** rustic does not honor restic's locking semantics, so mixed writes and cleanup can cause repository damage. [Official rustic FAQ](https://rustic.cli.rs/docs/FAQ.html). This is a recovery option under a carefully single-writer regime, not a license to run both backup engines against the same live repository.
5. **Duplicacy's commercial license is a Sustainability cost.** The CLI can be evaluated under its published trial terms, but continued for-profit backup requires a paid CLI license, unlike the four open-source alternatives. Restore, check/copy/prune may have different licensing rights; do not infer that backup is permanently free. [Vendor licensing](https://duplicacy.com/buy.html).

## Actual gates after this test

| Gate | Evidence status |
| --- | --- |
| **B1 lawful repeatable use** | Open-source license supported for restic/Kopia/Borg/rustic; Duplicacy ongoing commercial use **conditional on paid license**, trial demonstrated |
| **B2 encrypted authenticated backup** | Actual encrypted repository, wrong-key failure and full verification demonstrated on all five local configurations; targeted ciphertext corruption rejection separately demonstrated for restic in [STO-001](restic-results-2026-11-15.md), **not yet equally tested for every candidate** |
| **B3 exact complete restore** | **PASS for all five** on the common synthetic two-generation workload, with explicit source hash checks |
| **B4 restored authority inactive** | **PASS for quarantine behavior of our harness**; actual independent authorization/fencing remains **NOT TESTED** |
| **B5 host-loss recovery and independent retained keys** | Actual full restoration from an existing encrypted repository proven locally; independent off-host key custody / provider failure **NOT TESTED** |
| **B6 remote backend without mandatory paid-only backup vendor** | Documentary support for remote destinations in four free engines; no provider trial or authorization, so complete integrated gate **NOT TESTED** |
| **B7 append-only / deletion protection** | Borg capability documented, no live separate SSH identity exercised; all provider-specific deletion permission setups **NOT TESTED** |

## Candidate differentiation — no winner assigned

| Candidate | When it deserves a deeper test | Open issue |
| --- | --- | --- |
| **restic** | Minimal mature CLI with varied remote providers; straightforward unattended snapshot-and-copy sequence | External maintenance/retention automation, independent writer vs prune rights |
| **Kopia** | Reduce custom policy/scheduling logic, support several remote backends and managed maintenance | Maintenance coordinator recovery, free vs paid integration paths, credential/deletion isolation |
| **BorgBackup** | A personally controlled SSH backup server with **forced-command append-only** privileges | Separate SSH host/server overhead; direct native object-store use and cross-version migration |
| **rustic** | Fast independent recovery client for restic-compatible repository and lock-free capabilities | Mixed-client locking/pruning danger; distinct long-term maintenance/version maturity |
| **Duplicacy** | Diverse cloud providers and lock-free snapshot model, especially when a license is already available | Ongoing commercial license; `-hash` correctness/performance for rapidly rewritten snapshots; retention safety |

### Next minimum evidence (do not scale this lab blindly)

A primary+backup selection cannot pass [STO-001](selection-criteria.md) without **two genuinely independent storage failure domains** and a root unlock path that does not depend on the vault or computer being restored. The most decision-relevant next experiment is a real provider/SSH-SFTP or S3-compatible pair with **separate write/delete authority and provider/accounts**, and a tested clean-host restore. Candidate shortlist for that experiment: restic and Kopia (with rustic read-only recovery compatibility), plus Borg **if** an SSH-controlled append-only backend is practical. Duplicacy remains an evaluated comparator but carries a licensing cost.

**Selection outcome: DEFER**. We have meaningful comparable backup evidence, but not evidence of operationally sustainable remote storage. Do not move TinyFund state or create paid resources based on this result.
