# Miss Lea Operator Control Plane — V1

**Current status: source and synthetic tests only. Real vault, trusted runner, Cloudflare and Gmail credentials are NOT connected; no actual account-admin operation was performed.** This code is published solely to bootstrap a separate, immutable-to-agent **private trusted operator** environment. Never add real secrets to this public research repository, its Actions, issues, files, branches, or chats.

## Goal

Give the **operator** authority to administer the dedicated Miss Lea accounts (including root-level recovery powers), while ordinary agent/model code only receives results of authorized operations, not secrets. Full emergency credential *custody* is intended; full authorization is subject to the provider's actual contractual and technical controls, which cannot be conjured by one API key.

One root vault is not enough: a `Root Vault` and an `Operational Vault` hold credentials, a trusted runner resolves them **just in time**, and a metadata-only registry tracks accounts and recovery authority. The operator's root authority is broad; routine tasks use operational credentials. All remote provider calls use fixed HTTPS origins. **Never grant future agent control over this runner's source or root identity.**

## Vault choice for bootstrap

**Infisical Cloud Free**, provisioned under a **dedicated operator-managed Miss Lea account**, is the first candidate. $0 up to five human/machine identities as documented in Nov 2026. Free does not include advanced Access Controls, automatic rotation or durable audit retention, so separate projects/machine identities and an isolated trusted runner are essential. Use https://eu.infisical.com if available under the EU free organization; select the matching `MISSLEA_INFISICAL_REGION` at execution.

Create **two projects**, each with environment `prod`:
- `misslea-root` — account recovery details, master login credentials and powerful provisioning keys; **one Root machine identity** can read this, and has permission to write new operational secrets into `misslea-operations`. An independent emergency recovery copy must exist outside Infisical; not in the same encrypted archive or dependent on this account's Gmail.
- `misslea-operations` — revocable service credentials, Gmail OAuth token, and routine API tokens. **One Ops machine identity** is a project identity for *only* this project, not root. The trusted operator Root identity can additionally write here, only for credential provisioning.

Free's basic project role boundaries need a real denial test: an Ops identity attempting to fetch a Root canary must be rejected before storing any actual master credentials. This is mandatory. If Free fails, **stop root-secret onboarding** and switch vault/isolation; do not assume folder names or convention provide security.

### Deposit securely without sharing with ChatGPT

1. You log in to Infisical **directly** in your browser (not via ChatGPT or a link with an encoded token) using the dedicated Miss Lea-controlled organization; verify the HTTPS origin.
2. In `misslea-root`, add values via **Add Secret → Name / Value**:
   - `CLOUDFLARE_PROVISIONING_TOKEN` — high-privilege account-owned API token with Account API Tokens Write and intended provisioning powers. **Not necessarily** equivalent to Cloudflare web account Super Administrator;
   - `CLOUDFLARE_RECOVERY_LOGIN`, `CLOUDFLARE_RECOVERY_PASSWORD`, `CLOUDFLARE_RECOVERY_CODES` if available;
   - `GOOGLE_ACCOUNT_RECOVERY` and recovery codes/instructions for `missLea931@gmail.com`. Full recovery of the Google account is not granted by Gmail OAuth.
3. In `misslea-operations`, add `CLOUDFLARE_ACCOUNT_ID`, `CLOUDFLARE_WORKERS_ADMIN_TOKEN` (account-wide Workers Admin for normal provisioning, **not** Cloudflare root), and later `GOOGLE_OAUTH_CLIENT_ID`, `GOOGLE_OAUTH_CLIENT_SECRET`, `GMAIL_REFRESH_TOKEN`. The last three must be acquired with a one-time genuine OAuth grant from the Miss Lea Google account, **not** your currently connected personal Gmail.
4. Create **Root** and **Ops** Infisical machine identities with Universal Auth and assign them as above. Bootstrap credentials for the *runner itself* go into its own protected environment, not into `misslea` agent runtime. The free Infisical UI is the only normal ingestion path; no tokens are pasted in ChatGPT, logs, source, screenshots, or CLI arguments.
5. Record only the Infisical project IDs, role boundaries, operational status and secret *names* in the metadata registry. Do **not** publish actual private account IDs, user-identifying recovery details, Client ID/Client Secret or credential values in this repository.

### Separate trusted execution environment

**Required before live credentials.** Create a new **private** `misslea-operator` repository controlled only by the current trusted operator/owner, not editable by the running agent, and migrate the `labs/operator_control` package. The present connected GitHub tooling cannot create a new repo; the operator can later use an authorized code-hosting GUI/connector or request one owner bootstrap. A private repository by itself is not a sufficient security boundary: enforce branch protections, runner/environment restrictions, and prevent any agent-owned token from updating its workflows or code. GitHub Free restrictions on private Environment protections may require a different executor; do not use a privileged runner until these controls are verified.

The trusted runner obtains Infisical machine credentials from its protected environment (or Workload Identity/OIDC, when supported), calls Infisical and provider APIs, and reports **sanitized** responses only. Any access to `Root` occurs in a separate admin operation, is written to an independent audit log, and does not return a root secret to an agent. Both runner source integrity and independent auth are mandatory. Do not make the runner's privileged API public without authentication.

Commands are **non-secret JSON**, e.g.:
```json
{"operation":"cloudflare.workers.list"}
```
```json
{"operation":"cloudflare.worker.create","name":"misslea-test"}
```
```json
{"operation":"cloudflare.token.issue","name":"New lab token","permission_group_id":"<official Cloudflare permission group ID>","resource_scope":"com.cloudflare.api.account.<account ID>","secret_name":"CLOUDFLARE_NEW_WORKER_TOKEN"}
```
The third command creates a token **only once an actual verified policy and account ID** are provided and stores the token directly in `misslea-operations`. It never returns the secret. If saving fails it attempts to revoke; an uncertain revocation is reported without secret values. This is privileged, and must not be directly callable from ordinary agent input.

Run read-only manifest validation without any credentials:

```sh
python -m labs.operator_control.cli --list-accounts
python -m unittest discover -s labs/operator_control -p 'test_*.py' -v
```

The eventual trusted executor accepts `--command-file` and uses these runtime-only environment identifiers:
- `MISSLEA_INFISICAL_REGION` (eu/us/legacy)
- `MISSLEA_OPS_INFISICAL_CLIENT_ID`, `MISSLEA_OPS_INFISICAL_CLIENT_SECRET`, `MISSLEA_OPS_INFISICAL_PROJECT_ID`
- `MISSLEA_ROOT_INFISICAL_CLIENT_ID`, `MISSLEA_ROOT_INFISICAL_CLIENT_SECRET`, `MISSLEA_ROOT_INFISICAL_PROJECT_ID`

`Operator Control Plane v1` deliberately lacks: a live trusted runner, web-based account registration, Gmail OAuth bootstrap, role-policy verification, secure persistent audit storage, independent vault recovery test, token rotation, Gmail mail send/read, automated Chrome/browser provisioning and autonomous handoff to the agent. These are *next integration tasks*, not results established by this synthetic PR. A private isolated operator endpoint is required before any real master key gets connected.

## Boundary to future Miss Lea

The future agent may be delegated tool operations and eventually management of her own accounts, including an independently controlled emergency path, **but must not be able to replace the trusted executor's security policy and code with malicious instructions**. Human intervention should not be required for routine cloud provisioning after initial account creation; provider-imposed identity verification/billing acceptance may still be unavoidable.

### Official documentation

- https://infisical.com/pricing
- https://infisical.com/docs/documentation/platform/identities/machine-identities
- https://infisical.com/docs/documentation/platform/identities/universal-auth
- https://infisical.com/docs/api-reference
- https://developers.cloudflare.com/fundamentals/api/get-started/account-owned-tokens/
- https://developers.cloudflare.com/api/resources/accounts/subresources/tokens/methods/create/
- https://developers.google.com/workspace/gmail/api/auth/web-server
