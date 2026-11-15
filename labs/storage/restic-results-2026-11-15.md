# STO-001 — First real encrypted-backup findings (2026-11-15)

**Scope:** isolated ephemeral GitHub Actions on **one** Ubuntu 24.04 runner; no cloud accounts, real memory or real keys. **Result:** PASS_ENCRYPTED_LOCAL_ONLY, not distributed backup acceptance.

## Reproducible evidence

[GitHub Actions workflow run #43706296868](https://github.com/blondahouse/missLea/actions/runs/43706296868) succeeded on revision `82e435c3108ec74098b8ddd62296351d9ac2eee8`. Ubuntu `apt` supplied **restic 0.16.4** (this is the tested version, not the newest upstream release).

Test passed:
- SQLite coherent snapshot of original evidence/provenance, decision, unresolved obligation and a revoked grant.
- Two **real encrypted** restic repositories, initialized with separately generated keys.
- Wrong repository password rejected; inspected archive files contained no synthetic plaintext canary.
- Modified one encrypted data pack: `restic check --read-data` detected corruption.
- Destroyed original DB and snapshot; used **other** repository to recover the records.
- Verified exact contents, event order and provenance, and restored only to quarantine without activating permissions.

## Gate impact (not a production pass)

| Criteria | Evidence status |
| --- | --- |
| D1 original evidence/provenance export | PARTIAL PASS on one synthetic SQLite fixture |
| D2 coherent crash-safe snapshots | PARTIAL PASS on SQLite backup API; interrupted write/cross-host recovery not newly tested |
| D3 encryption and authenticated backups | PASS on local synthetic restic archives and tamper rejection; provider integration NOT TESTED |
| D4 lose host + one independent provider | **NOT TESTED**: two directories on one CI host do NOT count as independent |
| D5 independent deletion authority and unlock recovery | NOT TESTED |
| D6 no restoration of active grants | PARTIAL PASS: quarantine restore; independent fencing NOT TESTED |
| D7 zero-cost real remote provider config | NOT TESTED |
| D8 migration without founder machine | PARTIAL: executable test was on cloud CI, real operator recovery NOT TESTED |

**Decision:** restic is a **technically demonstrated backup tool candidate**, not yet a selected two-provider topology. The next decision-blocking experiment is a cost-authorized pair of genuinely independent stores plus a recoverable offline unlock plan, including a backup-writer identity that cannot erase every retained generation.

These results do not include real TinyFund data, external provider storage or authorizations.
