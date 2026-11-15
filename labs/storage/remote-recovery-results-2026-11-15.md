# STO-003 — Restricted remote services and clean-runner recovery: results

**Date:** 2026-11-15 · **Evidence:** [GitHub Actions run #43716887347](https://github.com/blondahouse/missLea/actions/runs/43716887347), revision `6ac4fa1372c5188d9bbe5ca522e931ad73648c20`. Both jobs **PASS**. [Predeclared protocol](remote-recovery-protocol.md).

**Decision:** remote-protocol recovery mechanics demonstrated in an **ephemeral, non-production, same-platform laboratory**. Actual independent storage provider selection **DEFERRED**. Neither production storage nor root-key custody was provisioned.

## What was really exercised

1. An isolated Ubuntu 24.04 Actions runner started **restic/rest-server 0.14.0 over loopback REST in append-only mode** and a separate **BorgBackup SSH forced-command service** running under a dedicated OS user.
2. Both clients saved the same **application-consistent synthetic SQLite evidence, original decisions, unresolved obligation, revoked grant, and 256 KiB attachment**, encrypted independently by restic and Borg. Both native integrity checks completed.
3. A wrong backup password was denied for both repositories. A direct REST **DELETE** for an existing snapshot was refused with **HTTP 403**; the snapshot remained readable. The limited SSH client could not run a shell command to create a file on the remote host.
4. Only the encrypted repository directories and a **synthetic checksum manifest** were packed into a 1-day GitHub Actions artifact. No primary database, cleartext source, SSH private key or original running services were exported.
5. A **new GitHub-hosted runner** downloaded and reconstructed the repositories. It checked both formats and restored the original records and attachment **bit-for-bit** into quarantine from each tool. After making the REST copy inaccessible, it recovered using Borg. After making the Borg copy inaccessible, it recovered using restic. Every recovery left authority **inactive**.

The first CI attempt failed because a completely fresh Ubuntu environment lacked `/run/sshd`; [the fix](https://github.com/blondahouse/missLea/pull/22) created that standard OpenSSH runtime directory. That was a **test-environment initialization defect**, not a repository corruption or backup engine failure.

## Gate status — strict claims

| STO-003 gate | Result |
| --- | --- |
| X1 two distinct **real protocols/services** | **PASS**, REST and SSH; both hosted on **one** GitHub runner |
| X2 destructive-operation restrictions | **PASS** for tested REST DELETE (HTTP 403) and tested SSH forced-command escape; not a general penetration test |
| X3 encrypted recovery and wrong-password denial | **PASS** on **synthetic** archives; not real secret custody |
| X4 clean-host reinstallation/recovery | **PASS** on a second independent *runner*, via GitHub artifact, with no original source or SSH private key |
| X5 each simulated backend unavailable and inactive recovered state | **PASS** in both directions, with exact synthetic record validation |
| X6 credential hygiene/cost boundary | **PASS** for ephemeral synthetic-only job, short artifact retention, no provider accounts/billing; production economics NOT TESTED |

**Not demonstrated:** two geographically or organizationally independent cloud providers (**STO-001 D4 remains NOT TESTED**); credentials whose write role cannot erase every historical generation under real provider policies; actual protected backup encryption keys held outside GitHub; host/account administrator compromise; live key renewal or external identity fencing; actual recurring cost, RPO/RTO, outage and account closure behavior.

**Security limitation:** REST HTTP was bound to `127.0.0.1` with authentication disabled because only synthetic data flowed on an ephemeral CI machine. This configuration must **never** be copied into a publicly reachable service. The two unlock strings were explicitly public synthetic fixtures, not recoverable production secrets. Both encrypted archives and the test-only unlock logic ultimately depend on **GitHub**, so the experiment is not two genuine independent failure domains or a validated independent key escrow.

**Borg limitation:** Borg 1.x's append-only service can still permit **logical archive deletion** while retaining physical segment history pending privileged compaction. It is not equivalent to immutable/WORM retention or protection from server administrator deletion. [Borg official notes](https://borgbackup.readthedocs.io/en/stable/usage/notes.html). REST append-only's specific deletion denial also does not protect a repository from a service operator with direct filesystem access.

## Next decision-relevant trial

To close D4/D5/D7/D8 rather than endlessly add simulation layers, provision **two actually independent provider accounts/backends** with independent administrator/recovery/billing domains, grant the backup writer credentials that cannot wipe protected historical generations, and prove restore on an unfamiliar host with unlock/recovery credentials held outside both providers. This step **requires separately authorized real accounts and carefully controlled keys**. No user accounts were touched and no billing was enabled as part of STO-003.

**STO-001 overall status: DEFER.** Continue to consider restic, Kopia, Borg, rustic and Duplicacy per [STO-002](backup-comparison-results-2026-11-15.md); this protocol trial did not select a final backup engine.
