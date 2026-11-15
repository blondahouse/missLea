# STO-006 — Verified identical encrypted generation in Backblaze B2 and Google Drive

**Verified 2026-11-16 (Kyiv local time; 2026-11-15 UTC)** · **Status: PASS for the stated STO-006 experimental gates, NOT production storage acceptance.**

## Primary reproducible evidence

- [GitHub Actions workflow #43775893336](https://github.com/blondahouse/missLea/actions/runs/43775893336): `completed / success` on `main`, SHA `606b7c099a1b68d32b4f68af9739f5bc043effc3`.
- `build-one-generation` — **PASS**: one application-consistent synthetic SQLite snapshot encrypted with restic once, packed once into the common synthetic artifact, with one original SHA-256 manifest.
- `upload-drive` — **PASS**: that same artifact uploaded using the pre-existing separate Google `drive.file` OAuth environment `sto005-drive`.
- `upload-b2` — **PASS**: that same artifact uploaded via the real Backblaze B2 S3-compatible API with the pre-existing bucket-scoped environment `sto004-b2` and pinned boto3 client.
- `restore-from-b2-without-drive` — **PASS**: a separate new Actions runner without Google OAuth credentials downloaded the B2 object, matched the original archived bytes by **SHA-256**, passed `restic check --read-data`, and restored the original synthetic records and attachment into inactive quarantine.
- `restore-from-drive-without-b2` — **PASS**: another separate Actions runner without Backblaze keys downloaded the Drive object, matched **the same original SHA-256**, passed restic verification, and restored the records and attachment into inactive quarantine.

The two restore jobs each emitted this actual validation receipt:

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

This is evidence for **byte-for-byte identity of the encrypted archive from both real providers**, not merely equivalent separately generated data. A different independent source image was **not** made for each backend.

## Important boundary: what did NOT happen

- Neither B2 nor Google experienced an **actual service outage**. Isolation was achieved by leaving each recovery job without credentials to the other provider and making no calls to that provider. This supports recoverability *if* the remaining provider is accessible; it is **not** a real-world outage SLA test.
- All stages were orchestrated on **GitHub Actions** and source checksums traveled via a **GitHub artifact**. If GitHub and its environment secrets are unavailable, this run does **not** prove independent emergency recovery.
- The synthetic restic encryption password is intentionally **public in the workflow code**, so the tested archive is *not confidential*. **Never place real Miss Lea memory in this design as-is.** Independent private key custody / outside-GitHub escrow has **not** passed.
- Both provider credentials were held in GitHub Actions protected environments and were visible to the approved steps that needed them. This is temporary owner-reviewed access, **not** an isolated credential Broker.
- There is **no evidence yet** that the B2 writer cannot erase all retained generations under the real B2 provider policy, or that Google Drive retention resists deletion by the owner or the approved OAuth client. **Object Lock/WORM and independent deletion authority are NOT TESTED.**
- Long-term scheduling, original chat archive scale, costs/free-quota exhaustion, true RPO/RTO, independent root-account recovery, and single active-writer fencing remain **NOT TESTED**.

## Earlier failure and resolution

Initial [run #43774602100](https://github.com/blondahouse/missLea/actions/runs/43774602100) failed at the **Ubuntu system package installation** stage (`awscli` absent), before it contacted B2; Drive had already accepted the same synthetic artifact, recoveries were skipped. The fix [PR #28](https://github.com/blondahouse/missLea/pull/28) replaced the unavailable system tool with pinned `boto3==1.44.3`, limited secret exposure to the actual S3 steps, and added offline SDK round-trip and corruption tests. All CI passed before this successful *new* manual run.

## Retention and credential retirement

The successful test leaves small, **synthetic-only** artifacts: B2 key `sto006/43775893336/memory-restic.tar.gz` in the existing `misslea-storage-lab-b2` bucket, and Drive file named `misslea-sto006-synthetic-43775893336.tar.gz` in the separate Miss Lea Google account. A Drive test file from the first failed STO-006 attempt may also remain.

Do **not** delete whole buckets or unrelated Drive files. Once no additional authorized retention tests need the data, deliberately remove only named synthetic objects, then revoke the short-lived B2 application key, Google OAuth app authorization, and both temporary GitHub environment secrets. OAuth refresh token in *Testing* may expire after seven days; this is not a reliable permanent automation scheme.

## Decision

**STO-006 experimental protocol: PASS. STO-001 end-to-end storage selection: DEFER** until proof of:
1. **Privately encrypted real-memory backups with independently recoverable root unlock** outside the host, GitHub and both providers, without circular dependency on the vault.
2. **Deletion/overwrite protection and blast-radius limits** under real provider credentials, with preserved history despite a compromised backup writer.
3. **Recovery when GitHub is unavailable**, including independent current-authority/clone fencing before any live agent resumes.
4. Actual realistic capacity, free-tier/expiry behavior, recurring schedules, costs and achievable recovery-point/time targets.

No live TinyFund state, permissions, provider settings or billing were changed in STO-006.
