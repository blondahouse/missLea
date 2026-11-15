# STO-001 — Restic encrypted recovery, first real CLI trial

The [GitHub Actions workflow](../../.github/workflows/storage-restic-trial.yml) runs **the real restic executable** with synthetic SQLite source records and **two distinct, randomly generated repository passwords**. It does not access any storage provider or the running Miss Lea agent.

## Predeclared acceptance

1. Make a coherent snapshot of original evidence, decisions, an unresolved obligation and an explicitly revoked grant.
2. Back it up into two separately initialized encrypted restic repositories, using different ephemeral keys; reject a cross-repository wrong key.
3. Prove the marker appears nowhere in the on-disk repository files, and verify both archives via `restic check --read-data`.
4. Corrupt one encrypted pack, ensure restic detects it, erase primary and unencrypted staging, and restore through the undamaged archive.
5. Verify all records and provenance survive and the result remains **quarantined/inactive**. No old grant can automatically authorize a new executor.

The script prints only sanitized booleans and the installed restic version. Keys and synthetic record canary values are not printed or uploaded.

## Essential limits

**Two folders on one ephemeral GitHub runner are NOT two independent physical failure domains.** This test measures real backup encryption, corruption detection and logical restore, not remote availability, deletion-proof retention, independent administrator accounts, service costs, actual RPO/RTO, or the ability to recover after losing the only decryption key.

It proves **D3 on a local synthetic workload**, contributes evidence to D1/D2/D6, and does **not** fulfill D4/D5/D7/D8 at deployment level. No remote provider is selected.

The same-source key must be recoverable outside the database/vault it unlocks. Later trials should use **two separate provider accounts** and a limited backup writer that cannot erase the independently protected recovery generation. Do not treat two buckets under a single superadmin identity as independent.

## Running and next step

GitHub Actions installs restic on an Ubuntu 24.04 runner and records the `restic version`. No Mac installation, payment method or account setup is necessary. A real off-site test requires separately granted access and prior approval of backend pricing/limits.

Related: [STO-001 criteria](selection-criteria.md), [synthetic snapshot prototype](README.md) and [SEC-001](../security/selection-criteria.md).
