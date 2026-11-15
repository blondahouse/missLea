# STO-005 — Second real provider: Google Drive (browser-only bootstrap)

**State:** prepared but **not yet authorized or run**. This is a short-lived **synthetic-only** experiment; no real Miss Lea memory, files, payment method, B2 credentials or permanent secrets are used. [STO-001 criteria](selection-criteria.md), [prior B2 success](sto004-b2-results-2026-11-15.md).

## Fixed experimental objective

Use **a different storage provider and a different account from Backblaze**. A Google OAuth client belonging to the dedicated Miss Lea Google account grants the **non-sensitive** scope `https://www.googleapis.com/auth/drive.file`, restricted by Google to files this OAuth application created/opened. No full `drive` scope.

A manual [GitHub Actions workflow](../../.github/workflows/storage-sto005-real-drive.yml), behind a **separately protected environment** `sto005-drive`, will:
1. Generate deterministic synthetic evidence, decision, pending obligation, revoked grant and attachment. Take an application-consistent SQLite snapshot.
2. Back up with **real restic client-side encryption** and package **only encrypted restic repository files** in one compressed archive. Restic's test password is intentionally public; no real data are confidential in this test.
3. Upload that archive via the **official Google Drive API and Python library** to the dedicated Miss Lea account; retain only checksum evidence and private file ID for the next job.
4. On a new CI runner with **no B2 credentials and no original database**, fetch the file from Google Drive, verify its SHA-256, unpack safely, run restic integrity verification and restore into quarantined inactive state. Verify source records and attachment exactly.

This proves real **single-provider Google Drive** transport + recovery. It does **not** yet prove a single *identical backup generation* replicated across B2+Drive, independent recovery key custody, immutable retention, separate provider-wide deletion authority or operational authorization fencing. Those remain to close STO-001 D4/D5/D7/D8.

## Minimal manual browser steps (do not copy secrets to chat)

### 1. Create a Google Cloud OAuth client — under Miss Lea's Google account only

At [Google Cloud Console](https://console.cloud.google.com/), confirm the active account is the separate Google identity of **Miss Lea**, NOT the founder's personal Google Drive. Create a new **project**, e.g. `misslea-storage-lab`, then enable **Google Drive API** under APIs & Services → Library. Creating an API project and enabling Drive API is not permission to activate paid services; **stop if billing/card enrollment is requested**.

Open **Google Auth Platform** (some consoles call it OAuth consent screen):
- Branding/app display name: `Miss Lea Storage Lab`.
- Audience: **External** (personal Gmail accounts are not Workspace internal). In Testing, add only Miss Lea's Google account as a **test user**.
- Data access: add **only** `https://www.googleapis.com/auth/drive.file`. Do not add full Drive, Gmail or unrelated scopes.
- Clients: **Create client → Web application**, name `Miss Lea STO-005 OAuth`. Under **Authorized redirect URIs**, enter exactly `https://developers.google.com/oauthplayground`. Save. Do not put OAuth client secret in GitHub source or ChatGPT.

*Why Web application?* It is the appropriate redirect-capable client for using the official Google OAuth Playground entirely in a browser; a Desktop client normally waits for a localhost redirect listener. With **Testing** status, Google may expire the refresh token in **7 days**. That is fine for this one-off experiment; making an app permanent requires a separate security and lifecycle decision.

### 2. Obtain an offline token via Google's first-party OAuth Playground

Visit [Google OAuth 2.0 Playground](https://developers.google.com/oauthplayground) in a browser under Miss Lea's Google account. Open the top-right gear:
- Enable **Use your own OAuth credentials**, enter the new OAuth Client ID/Secret, choose **OAuth flow: Server-side** and **Access type: Offline**.
- At Step 1, enter the exact single scope `https://www.googleapis.com/auth/drive.file`. Authorize APIs, select **Miss Lea's** account and consent.
- At Step 2, click **Exchange authorization code for tokens**. Copy the **refresh token** directly to its intended protected GitHub secret. Do not paste it into a message, GitHub issue, PR, screenshot or public file.
- If no refresh token appears, revoke the temporary consent in the separate Google account and redo with Offline access; do **not** substitute the short-lived access token.

### 3. Protect the GitHub secrets

Create a **separate** GitHub environment at `blondahouse/missLea → Settings → Environments` named `sto005-drive`. As with B2, select **only `main`** for deployment; enable **Required reviewers** with the founder account, **Prevent self-review off** for this manual trial, and **Admin bypass off**. Save rules.

Under this environment's **Environment secrets** (never repository variables), add exactly:

| Secret name | Value |
| --- | --- |
| `STO005_DRIVE_CLIENT_ID` | OAuth Web Application **Client ID** |
| `STO005_DRIVE_CLIENT_SECRET` | OAuth Web Application **Client secret** |
| `STO005_DRIVE_REFRESH_TOKEN` | OAuth Playground **refresh token** |

Do **not** reuse `sto004-b2` environment or paste its B2 keys here. The Google OAuth refresh token is a bearer credential; GitHub Actions code approved for this environment can use it, so this temporary manual system is not a production Credential Broker.

### 4. Manual launch after the PR is merged

Go to [STO-005 workflow](https://github.com/blondahouse/missLea/actions/workflows/storage-sto005-real-drive.yml) → **Run workflow**, choose **main**, approve both environment deployments if requested. Expected two green jobs: `upload-drive` and `clean-runner-drive-recovery`.

Success writes a small encrypted **synthetic-only** file named `misslea-sto005-synthetic-<run-id>.tar.gz` to the **root of Miss Lea's Google Drive**, visible in its web UI. There is **no automatic deletion** of unrelated files. This file remains available until we decide and verify remote cleanup. The SHA manifest GitHub artifact expires after **one day**.

### Security and known limitations

- A successful test validates OAuth+provider transport, not secure permanent credential ownership. The one-off GitHub environment is approved only after examining the exact workflow code on `main`. Malicious approved workflow code could still misuse the `drive.file` credential to access files created by this OAuth app. Delete the environment secrets and revoke Google OAuth approval after completing the comparison.
- Provider isolation: B2 and Google Drive are independent accounts/services; **GitHub is still a common compute/metadata/credential-orchestration failure domain**. This experiment does not prove standalone recovery after GitHub loss.
- Data confidentiality: the restic password is a **public synthetic fixture** checked into workflow YAML, NOT suitable for private memories; actual protected backup requires a strong independently recoverable encryption key outside GitHub/Drive/B2.
- Scope limitation: `drive.file` should access **only app-created/opened** files, which also limits the trial's recovery to those specific files. A later production system needs either a more complete design or vetted third-party client; no broad Drive permissions are requested in this lab.
- **Google Drive API does not have a special paid subscription for this trial**; use existing free account storage and stop if any UI requests billing. Storage and API limits could change.
- Google OAuth consent **Testing** status can cause a 7-day refresh-token expiry; publishing and verification are **not** part of this experiment.

Official references: [Drive API scopes](https://developers.google.com/workspace/drive/api/guides/api-specific-auth), [Google OAuth offline access](https://developers.google.com/identity/protocols/oauth2/web-server), [Google upload](https://developers.google.com/workspace/drive/api/guides/manage-uploads), [Drive downloads](https://developers.google.com/workspace/drive/api/guides/manage-downloads), [OAuth Playground](https://developers.google.com/oauthplayground).
