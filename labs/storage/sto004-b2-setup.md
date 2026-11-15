# STO-004 — Real Backblaze B2 connection, one-time trial (SETUP REQUIRED)

**State:** prepared but not executed; this trial needs the user's explicit one-time configuration of a GitHub Actions **protected environment** and credentials. **No keys or test bytes have been read/written to B2 by this PR.**

This trial is deliberately narrower than the final [STO-001 requirements](selection-criteria.md): it validates only **one actual provider** (`misslea-storage-lab-b2`, EU Central) with a short-lived restricted bucket-specific application key. A second provider and independently stored recovery keys remain mandatory future work.

## Why this temporary approach?

The permanent Credential Broker from Security Lab has **not** been implemented or accepted yet. GitHub Actions environment secrets provide encrypted-at-rest storage and a human approval gate for an *isolated seven-day laboratory key*, but **are not a secure vault against malicious workflow code**: approved jobs can access secrets and could exfiltrate them if the workflow were modified. Therefore:

- Use **only a B2 Application Key** restricted to the one disposable laboratory bucket and expiring in seven days; never a master key.
- Protect GitHub environment **`sto004-b2`** with allowed deployment branch `main` and an explicit human required reviewer. The founder can approve their own run for this experiment if GitHub's `Prevent self-review` is disabled.
- Before approving, inspect [the exact workflow](../../.github/workflows/storage-sto004-real-b2.yml) **as committed to `main`**, not a suggested edited copy. The workflow has only `workflow_dispatch` (no `push` or `pull_request` triggers) and repository permission `contents: read`.
- Never put these secrets in Git files, PRs, chat, outputs, screenshots or ordinary repository variables.
- Revoke/delete the temporary B2 key and remove environment secrets after the test (or let the B2 key expire), **not** before the second-runner recovery finishes. No production data.
- Do not grant the agent or any arbitrary code contributor automatic ability to run jobs with environment secrets. This experiment is founder-approved and **not** the future autonomous secret architecture.

## Required manual setup (user, GitHub UI)

After this PR is merged:

1. Go to `blondahouse/missLea → Settings → Environments → New environment`. Name **`sto004-b2`**.
2. Restrict **Deployment branches and tags** to **Selected branches and tags → `main`**. Configure **Required reviewers** with the repository owner; keep `Prevent self-review` **off** if only that account will manually trigger and approve the trial.
3. Under **Environment secrets** (NOT repository variables or code), save:
   - `STO004_B2_KEY_ID` — Backblaze B2 `keyID` / S3 access key ID.
   - `STO004_B2_APPLICATION_KEY` — Backblaze B2 `applicationKey` / S3 secret access key.
4. Navigate `Actions → STO-004 B2 isolated provider probe (MANUAL ONLY) → Run workflow`, choose `main`. Review and approve the environment deployment. GitHub may ask for approval for **both jobs** independently.

If there are no `Environment secrets` controls, or branch restriction/reviewer settings cannot be configured, **do not paste the secrets elsewhere**; report that UI discrepancy.

## What the workflow really does

- First fresh GitHub runner: creates synthetic SQLite source+attachment; makes a consistent snapshot; uses real restic and a public **synthetic-only test password** to encrypt the snapshot and send it via Backblaze's S3 API to `s3.eu-central-003.backblazeb2.com` in `misslea-storage-lab-b2/sto004/<run-id>/`. A GitHub artifact contains **only the expected SHA-256 manifest**.
- Second, different runner: receives no original database, only the manifest, installs restic, reads the encrypted data from the same real B2 bucket, verifies its integrity and restores the exact source records into non-authoritative quarantine.
- The test repository remains in the lab bucket, under its dedicated run-id prefix, for later second-provider comparison; **no automatic deletion of the whole bucket**, no lifecycle or Object Lock changes. Only tiny synthetic files are written.
- The RESTIC_PASSWORD constant is deliberately public because test data are public. **Never** reuse this repo password for actual data. Encryption does not make this fixture confidential.

**PASS is limited to a single real B2 provider, real S3 access, encrypted snapshot and separate-runner restore.** It does not establish independent provider failover, overwrite-/deletion-resistant retention, a production Credential Broker, permanent key recovery, or cash cost on scale. B2's bucket encryption is defense-in-depth but does not replace restic client-side encryption with a separately protected key.

## After successful B2 connection

Second provider: the separate Google account belonging to Miss Lea, or a different low-cost provider independent of Backblaze. Credentials must be isolated in a different protected environment and must not reuse B2's administrative identities. A successful cross-provider test requires surviving loss of B2, restoration without the original runner, and separate unlock/owner recovery material. This remains **pending**.

References:
- [GitHub: environment secrets and manual reviewer approval](https://docs.github.com/en/actions/reference/workflows-and-actions/deployments-and-environments)
- [GitHub: configure environments](https://docs.github.com/en/actions/how-tos/deploy/configure-and-manage-deployments/manage-environments)
- [Backblaze: B2 S3-Compatible Application Keys](https://www.backblaze.com/docs/cloud-storage-s3-compatible-app-keys)
