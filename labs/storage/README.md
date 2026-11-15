# Storage Lab — sustainable state, recoverable memory and distributed backups

**Research scope:** preserve Miss Lea's **code, accumulated state, primary evidence, decisions, unresolved obligations, active-operation records and memory** across server/provider/model loss. This lab is separate from the running TinyFund instance and from the existing [Memory Lab](../memory/README.md): Memory Lab evaluates what information is extracted and retrieved; Storage Lab evaluates how the underlying records survive.

**Sustainability principle:** operations must be recoverable without treating the founder, one provider, one live LLM or one machine as an irreplaceable component.

## Initial decision (recorded before implementation)

**Question:** Can a consistent synthetic SQLite snapshot survive primary loss and one damaged copy, be restored into isolation, and remain **non-authoritative/inactive** pending independently checked permissions?

Initial mandatory gates:
1. **Consistent snapshot:** use SQLite's backup API rather than copying a potentially changing live database.
2. **Integrity:** record an explicit hash/size and check the restored SQLite data. Reject damaged snapshots; do not silently accept missing records.
3. **Independent mirrors:** losing the primary and corrupting one backup must still leave another usable copy.
4. **Quarantine restore:** never overwrite active state, launch another active agent, import revoked grants or re-enable execution merely because a snapshot exists.
5. **Honesty about protection:** this fixture is **unencrypted and unauthenticated**, operates ONLY on synthetic data, and cannot be used for actual memory, credentials, private backups or operational state.

**Stop condition:** demonstrate these behaviors offline. Only then select encrypted multi-backend storage technologies based on new, prospective criteria; this PR does not select a provider or encrypt data.

## Implemented first slice

- `snapshot.py`: standard-library-only `create_snapshot`, `verify_snapshot`, and `restore_to_quarantine`, using SQLite backup and SHA-256 corruption checks.
- `cli.py`: disposable demo with one destroyed primary and one damaged mirror, recovering synthetic records from the second mirror.
- `tests/`: snapshot consistency, corruption rejection, independent restore, inability to overwrite, and inactive recovery.

Run from the repository root:

```bash
python -m labs.storage.cli
python -m unittest discover -s labs -t . -p 'test_*.py' -v
```

The snapshot format contains an explicit `encrypted: false` warning. **SHA-256 is not an authentication mechanism** here; an attacker who can edit data and the manifest can forge both. Do not put real memory or secrets through this module. The two demonstration mirrors are directories on the same local filesystem, **not** physically distributed failure domains.

## Next decision record

The [proposed memory/storage selection criteria](selection-criteria.md) distinguish primary evidence, operational state, derived memory and recovery copies; they identify the minimum tests needed before selecting a long-term database or encrypted backup topology. These criteria have not yet authorized any live migration or storage subscription.

## Real encryption experiment (separate from the synthetic snapshot fixture)

The [restic encrypted two-repository trial](restic-trial.md) uses the real backup binary on GitHub Actions, detects an altered encrypted pack, and restores source records after primary loss. It uses **two directories on one runner**, not two remote failure domains; do not treat it as proof of geographically independent backups.

## STO-002 — comparative backup engine research

The [prospective five-candidate protocol](backup-comparison-protocol.md) covers **restic, Kopia, BorgBackup, rustic, and Duplicacy CLI**, with the same synthetic memory fixture, explicit lawful-use licensing requirements, and a reproducible [GitHub Actions matrix](../../.github/workflows/storage-backup-comparison.yml). **All five were tested against real CLIs**, including Duplicacy under its explicitly permitted temporary commercial trial (ongoing commercial backup requires a paid license). [Comparison results and selection gaps](backup-comparison-results-2026-11-15.md) include compression/hash correctness findings and verified read-only restic↔rustic recovery.

All local CI evidence stays distinct from the still-unproven **two genuinely independent remote destinations, separate recovery credentials, and destructive-access isolation**.

## STO-003 — restricted remote services and clean-host recovery

The [predeclared STO-003 protocol](remote-recovery-protocol.md) exercises **real restic REST append-only and BorgBackup SSH forced-command services** on an isolated CI runner, followed by restoration on a **separate fresh GitHub Actions runner**. [Results of the completed trial](remote-recovery-results-2026-11-15.md): both native backup integrity checks, remote denial controls, exact recovery from either surviving repository and default-inactive state passed. The exported backup data remained encrypted.

Both services initially live on the **same CI host and GitHub account**. Even a passing test does **not** prove two genuinely independent cloud providers, production key recovery, or automatic grant fencing. Test unlock strings are publicly known **synthetic fixtures**, never suitable for actual backups.

## STO-005 — second actual provider: Google Drive

[STO-005 browser-only OAuth setup](sto005-drive-setup.md) established access to the **separate** Miss Lea Google account after [B2 STO-004 succeeded](sto004-b2-results-2026-11-15.md). The manual [Google Drive API CI workflow](../../.github/workflows/storage-sto005-real-drive.yml) **succeeded** in uploading a test-only restic-encrypted archive with narrow `drive.file` OAuth scope and recovering it on a different CI runner without B2 access. See [verified STO-005 evidence](sto005-drive-results-2026-11-15.md).

This alone did **not** prove that one identical generation of memory was sent to both providers, or independent root key custody, administrator-safe retention or GitHub-independent recovery.

## STO-006 — identical backup generation in both real providers

The [predeclared STO-006 acceptance protocol](sto006-dual-provider-protocol.md) and [manual GitHub Actions workflow](../../.github/workflows/storage-sto006-dual-provider.yml) prepare a **single synthetic restic snapshot** and submit its **same archive bytes** to real B2 and Google Drive, using separately restricted existing GitHub environments. Two additional clean runners attempt recovery from each provider **without credentials to the other**. Exact byte hashes and original source records are checked, and restored authority stays inactive.

This stage is **not automatically deployed**: the workflow needs an explicit manual dispatch from `main` and review of the existing `sto004-b2` and `sto005-drive` environments. It is a limited provider transport/failover experiment, not a test of actual deletion-proof retention, protected recovery encryption keys or loss of GitHub itself.

## Research decisions before real storage

For actual Memory/State/Backup selection, evaluate:

| Dimension | Minimum required evidence |
| --- | --- |
| Coherent primary state | Application-consistent snapshots; source-of-truth and writer/fencing strategy |
| Confidentiality | Authenticated encryption by an established implementation, with no agent-visible decryption key |
| Recovery | Tested full restore after losing primary host and one storage provider |
| Separation | Backup write capability cannot erase independently retained recovery generations; no shared root permissions |
| Availability | At least two independent failure domains/providers where feasible |
| Cost and transfer | Measured storage/requests/egress and future paid limits, not assumed perpetual free tier |
| Independence | No dependence on founder credentials or a specific model; lawful account holder recorded |
| Authority and clones | Restoring memory does not reactivate grants; one independently authorized instance only |

A promising existing tool is **restic**, which provides encrypted, verifiable backups to local/SFTP/object-storage repositories. Separate repositories can have independent keys and retention policies. Compare concrete options (e.g. restic with two independently provisioned backends vs alternatives) against the criteria **before** a live decision. Do not build bespoke cryptography.

### Proposed data tiers (architecture research, not yet deployed)

- **Live/primary:** one authoritative writable database plus verifiable event/decision evidence; avoid premature multi-writer distributed memory.
- **Recovery:** snapshots encrypted before uploading, copied to at least two failure domains/providers under distinct credentials and retention.
- **Root keys:** keys to decrypt backups must be recoverable **outside the systems they unlock**; avoid circular dependency between Storage and Security.
- **Dormant mode:** if compute funds are depleted, retain recoverable memory and ownership/obligation records without keeping costly workers running.

The selected backup product, vault, retention, backup integrity proof, multi-host fencing and recovery operator will be decided by later research. `labs/storage` makes no external calls, costs nothing, and grants no real privileges.

See [Security Lab](../security/README.md), [digital independence](../../docs/digital-independence.md), and [evaluation policy](../../docs/evaluation-policy.md).

Reference: [restic documentation](https://restic.readthedocs.io/en/stable/) and [restic security model](https://restic.readthedocs.io/en/stable/100_references.html).
