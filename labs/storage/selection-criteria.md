# STO-001 — Where Miss Lea's memory and backups should live (PROPOSED)

**Recorded:** 2026-11-15 · **Decision type:** research and architecture selection, NOT migration or production deployment · **Decision:** DEFER selection until minimum evidence · **Criteria owner:** project discussion; proposed thresholds require confirmation before comparative trials.

## What is being preserved?

Do **not** treat memory, index, state, secrets and backup as one undifferentiated database.

| Data plane | Examples | Durability and authority |
| --- | --- | --- |
| **Primary records / history** | Original messages, observations, source evidence, events, commitments, decisions and their rationales | Durable source of truth; append/change with provenance; preserved through model changes |
| **Operational state** | Work queue, pending jobs, inventories, provider resource IDs, budgets, grants and revocations | Transactional; concurrency/fencing needed; restored copy must not resume action |
| **Derived memory** | Summaries, embeddings, knowledge graph, retrieval indexes | Rebuildable from retained source/evidence; track derivation and versions |
| **Artifacts** | Code snapshots, files, reports and model data | Content-addressable or manifest-verified; independent ownership and retention |
| **Secrets / decryption authority** | Vault keys, account tokens, archive unlock credentials | **Not** stored in agent-visible memory or unencrypted backups; managed under [Security Lab](../security/selection-criteria.md) |
| **Recovery snapshots** | Encrypted copies of consistent primary state and original sources | Multiple independent storage failure domains; never grant active authority when restored |

**Memory Lab** chooses extraction, consolidation and retrieval; **Storage Lab** chooses durable location, consistency, backup and recovery. The live source of truth should remain **single-writer**, not a distributed multi-master memory by default.

## Proposed mandatory gates and evidence

Use PASS / FAIL / NOT TESTED per **configuration**, not per product marketing. Do not choose a winner with unresolved mandatory NOT TESTED.

| ID | Type | Criterion | Evidence needed / veto |
| --- | --- | --- | --- |
| D1 | Mandatory | Original evidence, decisions, unclosed obligations and state can be exported without loss of ordering/provenance | Synthetic round trip across two environments; FAIL for inaccessible or silently truncated fields |
| D2 | Mandatory | Crash-safe coherent write/snapshot for one authoritative writer | Simulated interrupted write and consistent restore; FAIL if successful reports hide data loss |
| D3 | Mandatory | Encrypted and authenticated backups using **existing maintained software** before leaving a trusted host | Restore and tamper-failure test; current plaintext hash fixture is **not sufficient** |
| D4 | Mandatory | Primary host loss **and** corruption/unavailability of one backup location still permit recovery | Two physically/account independent destinations and a rehearsed restoration; two folders on one disk do not qualify |
| D5 | Mandatory | Backup/restore credentials cannot erase every independently protected generation; unlock key is outside its own backups | Credential and failure-domain diagram; negative access and recovery test |
| D6 | Mandatory | Restored state starts isolated: no second live agent, no recycled grant, no implicit financial/compute authorization | Restore into quarantine + independent current-authority check; FAIL on uncontrolled simultaneous execution |
| D7 | Mandatory | Demo design has an achievable **zero-new-subscription-cost** configuration; no implicit upgrade, credit card or chargeable service | Provider pricing, quota behavior and limits verified for actual planned usage |
| D8 | Mandatory | No founder device/LLM model is required for routine backups, and migration/export path is practical | Simulated transfer to independently provisioned host; FAIL on irreplaceable login/host |
| T1 | Trade-off | Storage capacity, recurring requests/egress and measured restore time | Measure on equivalent workloads, record missing costs as unknown |
| T2 | Trade-off | Maintenance, rate limits, migration tooling and vendor dependence | Runbook size, dependencies, documented restrictions |
| T3 | Optional | Geographic spread, deduplication, retained history search and cold dormant-mode cost | Only test if it would change the decision |

**Proposed Demo recovery target:** no more than **24 hours of primary record loss (RPO)** in a rehearsed single-site failure; actual restore time (RTO) must be measured, not assumed. This is a *research target*, not a claim about running TinyFund or permission to relax its current backups. Revisit after measurements or a stricter requirement. No mandatory storage spending is approved.

**Stopping rule:** stop when one primary + backup configuration passes D1–D8 and a viable fallback is documented, or when the smallest untested mandatory blocker is isolated. Do not implement vector databases or multi-primary replicas merely to increase apparent sophistication.

## Candidate topologies — desktop research, not selection

| Configuration | Benefit | Critical unknown/trade-off | Status |
| --- | --- | --- | --- |
| **SQLite on a persistent Linux host + restic to two independent backends** | Simple, portable primary; existing [Storage Lab](snapshot.py) validates synthetic SQLite-consistent snapshots. restic encrypts/authenticates and supports diverse repositories | Requires an always-on durable host; actual cloud backend credentials and offline unlock/recovery untested | NOT TESTED as deployed system |
| **Cloudflare D1 as the primary + independently exported encrypted backups** | Serverless SQL database accessible from Workers; usable while avoiding a long-lived VM in an early experiment | Cloudflare dependence and export frequency; Workers Free limits (500 MB per database and 5 GB total account storage as of Oct 2026), and limits can stop writes until quota reset. D1 point-in-time recovery is **not** a second-provider backup | NOT TESTED |
| **PostgreSQL on a separate host + independent encrypted backups** | Strong transactional base if multiple services eventually write | Higher cost/operational overhead than needed before concurrent writes are a demonstrated requirement | DEFERRED / NOT TESTED |
| **restic with distinct SFTP/object/other supported remotes** | Established encrypted backup, data integrity and verification, multi-backend portability | Separate backend lifecycle, permissions, retention, credential deletion rights and recovery keys must be tested | CANDIDATE only |
| **Cloudflare R2 as one destination** | S3-compatible object storage; published included free usage | R2 **requires adding an R2 subscription/checkout**, which can bill beyond free usage; do not enable it without separate authorization. Also **not independent** from D1/Workers when used as the only backup | NOT AUTHORIZED |

Where two storage backends share a provider account, login, root token, decryption key, billing policy or deletion authority, **do not count them as independent failure domains** merely because they are two buckets.

## Smallest useful evidence plan

1. **No provider calls:** agree on synthetic dataset (event ordering, changed decisions, unresolved obligations, attachments, one stale grant), size profile and a portable export schema. The [existing Storage Lab](README.md) only proves a basic **unencrypted** SQLite snapshot and two *same-disk* mirrors; it is not sufficient for D3–D5.
2. **Primary decision:** test portable SQLite on a persistent test host against D1/D2/D6; test D1 serverless export only if eliminating the always-on VM would change the result. Do not use a Worker runtime filesystem as the durable database.
3. **Backups:** use established restic in isolated ephemeral CI/container to encrypt a synthetic consistent snapshot, make two independently keyed repository copies, corrupt one, restore another, and validate all original records. Root recovery material is supplied outside the test repositories. No real data or public CI secrets.
4. **Only then test real free storage providers** after separate account, cost and permissions approval. Verify that backup credentials cannot erase protected generations; simulate loss of the primary host and one provider. Measure RPO, RTO, storage/egress/requests, and what a free-tier exhaustion does.
5. **Decision:** SELECT / REJECT / DEFER with measured evidence, missing facts, rollback and explicit Demo integration authorization. Do not move the running TinyFund memory based on research alone.

## Continuity and independence constraints

- **One active writer;** standby/restore cannot start external operations until current independently verified authority is granted.
- **Not everything needs online storage:** operational primary data stays accessible to the executing agent; immutable original evidence and encrypted recovery copies can be remote. Derived embeddings/graph indexes can be regenerated.
- **Founder may initially bootstrap legal accounts/recovery but must not be a permanent daily operator.** Each storage account records holder, operator, billing party, recovery and transferability.
- **No recursive lockout:** a vault must not require a secret recoverable only from a backup it decrypts. Independent emergency recovery must be tested before production.
- **Dormancy:** allow durable archival storage with compute turned off when credits run out, without silently creating debts.

## Official references (checked 2026-11-15)

- [Cloudflare D1 free limits and Time Travel](https://developers.cloudflare.com/d1/platform/limits/)
- [D1 free daily limits enforcement, September 2026](https://developers.cloudflare.com/changelog/post/2026-09-01-d1-free-tier-limit-enforcement/)
- [Cloudflare R2 requires subscription](https://developers.cloudflare.com/r2/get-started/)
- [restic encrypted repository security model](https://restic.readthedocs.io/en/stable/100_references.html)
- [restic check, copy, restore commands](https://restic.readthedocs.io/en/stable/manual_rest.html)
- [Project evaluation policy](../../docs/evaluation-policy.md)
