# STO-006 — Identical backup generation, two real storage providers

**Prospective protocol (2026-11-16).** Research only; no production migration, paid subscriptions, or new credentials. Both test providers and their manually protected GitHub environments already exist from STO-004/005.

## Question and strict acceptance

Can **the exact same encrypted restic repository archive** containing one consistent synthetic memory generation be stored in **Backblaze B2** and **Google Drive**, and independently restored by a clean, separate executor from *either* service, with the *other service completely absent from that executor's credentials and API calls*?

- **G1:** Build original SQLite evidence, decision, outstanding obligation, revoked grant, attachment; run restic encryption once. Compute an exact SHA-256 for the one resulting archive. No provider key in this generation stage.
- **G2:** Upload the exact archive bytes to B2 and Drive in independent GitHub Actions jobs using **distinct already protected environments** `sto004-b2` and `sto005-drive`. Fail if either upload fails. Use names and prefixes limited to `sto006/<run-id>`, no bucket/global deletion.
- **G3:** Once **both** uploads succeeded, recover on **two different clean GitHub-hosted runners**: the B2 job has B2-only secrets; Drive job has Drive-only secrets. Each downloads **from its own provider**, checks the same original SHA-256, performs full restic data verification and restores exact original contents.
- **G4:** Validate every recovered original, provenance and record order, pending obligation, revoked grant and attachment. Recovery is quarantined; no grant, credential or execution resumes.
- **G5:** No user or live Miss Lea data, real archive encryption secrets, master B2 key, account-wide Google Drive scope, recurring triggers, paid services or automatic deletion. Default GitHub environment reviewer approvals remain mandatory.
- **G6:** Report precise gaps: logical isolation of each provider is proven by per-job absent credentials and dependencies, but **no physical provider outage was induced**. GitHub is still a shared build/orchestration/manifest failure domain. The restic password is intentionally public **synthetic-only**, so confidentiality of actual memory is NOT proven. Off-platform root key escrow, immutable history and independent deletion authority are NOT TESTED.

**PASS requires all five jobs** (build, upload-B2, upload-Drive, restore-B2, restore-Drive) and file-hash equality to finish successfully on the manual run. This is stronger than two separate STO-004/005 generations but **not** full STO-001 D4/D5/D8 acceptance.

## Implementation boundaries

- Use the pre-existing [Google Drive `drive.file` client](drive_probe.py) and its OAuth environment; extend its filename validation only for the STO-006 synthetic filename.
- Use real AWS S3-compatible API for Backblaze at the existing `s3.eu-central-003.backblazeb2.com` endpoint and scoped `misslea-storage-lab-b2` bucket. AWS CLI is an API client, not a new credential.
- GitHub artifacts temporarily carry the common encrypted **synthetic** archive to both upload jobs. Clean recovery jobs download **only checksums / original expected manifest**, never the shared archive, forcing each to fetch its own provider.
- The B2 and Drive OAuth credentials are not available to build job nor to one another's upload/recovery jobs. A job approved to use its environment still could inspect that environment's secrets; this experiment does not substitute for a trusted Credential Broker.
- On successful proof, leave only tiny named synthetic test objects so subsequent retention and deletion-limit experiments can target known objects. Retire ephemeral provider keys and GitHub environment secrets after the authorized testing sequence; don't delete unrelated backups.
- The combined tests are **manual only** (`workflow_dispatch`) and must run from `main` with required reviewers and blocked administrator bypass.

## Decision after success

Record separate evidence for identical-generation two-provider storage and isolated restored paths. **STO-001 remains OPEN** until independent encryption-key recovery, deletion-proof retained generations under real provider permissions, provider failure/admin shutdown scenarios, loss of GitHub, and long-term costs/RPO/RTO are tested. Never equate different cloud provider names with complete autonomy of recovery.

Related: [STO-004 B2 evidence](sto004-b2-results-2026-11-15.md), [STO-005 Google Drive evidence](sto005-drive-results-2026-11-15.md), [STO-001 criteria](selection-criteria.md).
