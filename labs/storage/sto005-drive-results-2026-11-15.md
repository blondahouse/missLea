# STO-005 — Verified Google Drive second-provider encrypted recovery

**Evidence time:** 2026-11-15 (GitHub Actions UTC). **Result:** SUCCESS for a real Google Drive provider and clean cloud-runner recovery of a **synthetic** archive. **Project-wide STO-001 decision:** still DEFERRED until same-generation two-provider failover, actual root-key custody and retention/deletion isolation are proven.

## Verified real run

- [GitHub Actions run #43772924787](https://github.com/blondahouse/missLea/actions/runs/43772924787), manually launched on `main` at commit `bb94d01d6ca1dbf32191e9fd4ce1bd2d671a9998`.
- Workflow `STO-005 Google Drive second-provider trial (MANUAL ONLY)`: `completed / success`.
- **`upload-drive`** passed. A temporary GitHub-hosted runner generated a consistent SQLite fixture (4 original synthetic records and an attachment), encrypted it using real restic, packed only the encrypted repository, verified the local archive, and uploaded the compressed repository directly through the official Google Drive API using the `drive.file` OAuth scope to the **separate Miss Lea Google account**.
- **`clean-runner-drive-recovery`** passed on a different runner with **no Backblaze access** and no original SQLite database. The runner retrieved the Google Drive file, checked its SHA-256, unpacked it under path/size restrictions, ran `restic check --read-data`, and restored the original snapshot into quarantine.
- The actual validation receipt from the restore job was:
  ```json
  {
    "exact_record_and_attachment_recovery": true,
    "record_count": 4,
    "revocation_record_preserved": true,
    "authority_restored": false,
    "agent_started": false,
    "quarantine": true
  }
  ```
- The test left one synthetic archive named `misslea-sto005-synthetic-43772924787.tar.gz` in Miss Lea's Google Drive. A separate manifest is short-lived GitHub artifact evidence (retention one day). No access tokens, refresh tokens, OAuth client secrets, B2 keys or real memory are included in this report.

## What has been demonstrated (strict boundary)

After [STO-004 real Backblaze B2 success](sto004-b2-results-2026-11-15.md), STO-005 now establishes working encrypted synthetic backup and clean-runner recovery using **a second organizationally independent provider** (Google Drive), accessed with separately created scoped OAuth credentials.

However:
- STO-004 and STO-005 used **different snapshots and separate test generations**. No common source generation was replicated to both and recovered under a true B2 outage, so **STO-001 D4 complete failover remains NOT TESTED**.
- Both recoveries depended on **GitHub Actions orchestration**. Loss of GitHub, its environment approvals, or account access was not simulated. Different cloud storage providers ≠ independent overall recovery control.
- The restic repository encryption password is **intentionally public, synthetic-only**. It protects the archive format in the trial, but **does not provide meaningful confidentiality of actual memory**. Do not reuse these credentials or deploy this workflow for real backups.
- Google OAuth `drive.file` token is accessible to approved workflow code. GitHub Environment Secrets are a temporary protected manual mechanism, **not** a trusted production credential broker.
- **Immutable/object-locked history, independent administrator/deletion rights, offline recoverable root key, a production single-writer lease and live RPO/RTO** are **not** demonstrated.
- Google OAuth test-mode refresh tokens can expire after seven days; automated long-lived operation has not been authorized or implemented.
- GitHub Actions job logs included the non-secret **Google Drive file ID** in job environment metadata. This is not a token, but logs should avoid unnecessary object identifier exposure in future production designs.

## Next acceptance barrier

One **identical** consistent synthetic memory snapshot must be sent to both Backblaze B2 and Google Drive under independently scoped credentials; verify exact snapshot identity at both, then recover with one provider completely inaccessible, and repeat the other way around. Separately test retention against deletion using *real* provider roles, and establish an external recovery-key path that cannot be lost along with GitHub or the active host.

After this experiment, revoke the short-lived B2 Application Key and Google OAuth approval, and delete the temporary GitHub Environment Secrets; do not rely on token expiration alone when retiring unused access. Retention/cleanup of synthetic archives should be deliberate and should not delete unrelated objects.

**State:** STO-005 evidence recorded; no live Miss Lea memory migration, paid subscription, or autonomous key access authorized.
