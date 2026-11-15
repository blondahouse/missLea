# STO-003 — Restricted remote backends and clean-host recovery

**Prospective criteria written 2026-11-15 before implementation.** Scope: experimental **STO-001 D4/D5/D8 mechanics** with genuine backup daemons / SSH protocol on disposable GitHub Actions machines. Not approval to handle real Miss Lea memory or buy storage.

## Decision

Can two different, independently configured backup protocols accept encrypted synthetic snapshots while an untrusted backup client cannot trivially destroy retained history, and can a **new, separate GitHub Actions runner** recover after simulated loss of the original compute host and one backup endpoint?

No privately held SaaS accounts/provider credentials are available. This trial therefore **cannot** establish D4's two independent production providers or D5's real deletion protection. A network service on localhost is remote *in protocol*, not independent *in failure domain*. Artifacts transfer encrypted repos between distinct CI runners through **the same GitHub platform**. Synthetic unlock passwords are intentionally deterministic test fixtures in code; this is **not an escrow design**.

## Fixed gates for this experiment

| ID | Proof demanded | PASS only when | What remains outside scope |
| --- | --- | --- | --- |
| X1 | Two real remote protocols | restic over REST appending to its own daemon + Borg over SSH forced-command server, distinct repository directories and client transports | Different real cloud providers and legal account holders |
| X2 | Credential / destructive-operation restriction | REST appender refuses a destructive REST operation, SSH credential cannot run a shell command; published backup snapshots still recover afterwards | Defense against root/provider admin and ransomware on shared runner |
| X3 | Encrypted recovery | Both repositories contain encrypted synthetic records; wrong unlock credentials cannot recover data; authenticated reads and checks pass | Off-host secret manager / emergency key custody |
| X4 | Separate clean runner | Recovery is performed in a different Actions job/runner using only exported **encrypted repository archives**, test-only keys and checked-in code; original SQLite, original runtime and source files unavailable | Provider outage, independent geographic durability |
| X5 | One backend loss and quarantine | Make one recovered backup location unavailable and restore exact source evidence, decision, obligation and revoked grant via the remaining repository; **never activate authority** | Independent current-authority lease/fencing |
| X6 | Audit & finite use | Sanitized reports log allow/deny and hashes, no real creds, no paid accounts, no new durable services; cleanup stops every daemon and user | Real RPO/RTO or recurring cost |

### Acceptance and stop

CI must provide **two successful jobs** (prepare and clean-host recovery), demonstrate the named negative checks, and preserve full source integrity in quarantine. If a tool's documented append-only mode allows *logical* deletion or overwriting, record that limitation instead of mislabeling it as durable retention. Failed service launch or CLI mismatches mean **environment/test failure**, not product disqualification.

Stop as soon as X1–X6 are demonstrated for the ephemeral topology. **Do not attempt real independent cloud accounts without separate provider/account authorization.** The still-open production-level D4/D5/D7/D8 requirements remain NOT TESTED.

## Components under investigation

- [rest-server REST backend](https://github.com/restic/rest-server) with `--append-only` in an ephemeral loopback-only Docker container; authenticate transport and TLS not evaluated since the fixture has no real secrets.
- [BorgBackup 1.x](https://borgbackup.readthedocs.io/en/stable/usage/serve.html) over localhost-only OpenSSH forced command with `--append-only`. Warning: [Borg 1.x append-only](https://borgbackup.readthedocs.io/en/stable/usage/notes.html) **can permit logical delete**, although physical segment history survives until server-admin compaction. It is **not equivalent to WORM**.
- REST and Borg repos are different formats and use distinct unlock passwords. This trial does not imply cross-format compatibility or give one writer credentials for the other service.

Related: [STO-001 criteria](selection-criteria.md), [STO-002 results](backup-comparison-results-2026-11-15.md) and [Security Lab](../security/selection-criteria.md).
