# Autonomous Cloudflare lab operations — one-time bootstrap

**Status (2026-11-17):** The synthetic lab was deployed and a two-wake cycle was **verified live** through the **private trusted operator**, not through this public repository's optional deployment workflow. [Verified operator Actions](https://github.com/blondahouse/misslea-operator/actions/runs/43979791125). The public workflow described below is a legacy alternative and has **not** been bootstrapped with Cloudflare API credentials. Do not confuse offline CI or its no-op outcome with a live deployment.

## Purpose — optional legacy deployment route

For current experiments, prefer the verified private operator using Infisical Operations OIDC. The instructions below document an alternative only; it should not be activated concurrently with the private deployer.

After one deliberate human authorization, GitHub is a **control plane**, not an agent runtime. The assistant can author and merge changes in this repository. A main-branch push within `labs/cloudflare_agent` triggers GitHub Actions to deploy a **single** synthetic Cloudflare Worker. GitHub Actions stops after deployment and a one-time start request; Cloudflare Agents SDK schedules and executes subsequent wakes.

This is a deployment bridge for **one experimental Worker**, not a general-purpose cloud account administrator or a production Credential Broker.

## One-time bootstrap — minimum privileges

1. In the separate Miss Lea Cloudflare account, confirm **Workers Free**, then create an empty dedicated Worker named `misslea-cloudflare-only-lab`. Do not touch `late-glade-5dde`. Creating a Worker initially requires product-level Admin, so the human performs this once. No paid features, payment authorizations, or production data.
2. Cloudflare **Manage account → Account API Tokens → Create Token**: create an account-owned **machine** token, scoped to **Specified Workers → misslea-cloudflare-only-lab → Editor** only. Do not grant product-level Admin, DNS, billing, API Token Provisioning, access to other Workers, or Owner's personal resources. A Worker-specific Editor can deploy and update secrets but cannot create more Workers or alter the account. Keep Cloudflare root authentication and recovery separately.
3. In GitHub repository `blondahouse/missLea`, create Environment `cloudflare-agent-lab`. Restrict deployments to **main**. The lab is intended to deploy without future owner approval, so do not configure mandatory reviewers for this laboratory Environment; instead, restrict who can merge to main and do not expose the Environment to pull requests or untrusted branches. Add these **Environment Secrets** (not in repository files, Issues, chat, screenshots, or logs):
   - `CLOUDFLARE_API_TOKEN`: Worker-specific Editor token from step 2.
   - `CLOUDFLARE_ACCOUNT_ID`: the separate Miss Lea Cloudflare account ID (an identifier, not a secret, stored here only for operational convenience).
   - `LAB_ADMIN_TOKEN`: a fresh random 32+-character **lab-only** shared secret for starting a synthetic run; unrelated to Cloudflare management token or existing `MISSLEA_TASK_SECRET`.
   Optionally set Environment **Variable** `CLOUDFLARE_LAB_URL` to the verified URL of this Worker, e.g. `https://<YOUR-ACTUAL-WORKER>.workers.dev`. Do **not** infer the URL or point to the existing Worker.
4. Once the secrets are configured, a new source change merged into main (or an authorized manual workflow dispatch) deploys **only** `misslea-cloudflare-only-lab`. If `CLOUDFLARE_LAB_URL` is configured, the workflow sends one authenticated `/start` request; actual scheduled wakes then happen exclusively inside Cloudflare. Public `/status` reports only synthetic outcomes. CI without secrets is a harmless no-op.

## Boundaries and limitations

- **No direct Cloudflare connection to the chat:** edits are mediated by GitHub with an account-owned worker-scoped token. This is operational automation after bootstrap, not an assertion that ChatGPT possesses any account token.
- **The connected assistant can change source files, but the deployed agent itself does not gain GitHub write authority by default.** An autonomous Miss Lea must later receive a carefully scoped, revocable action broker. No agent-editable Worker may receive a Cloudflare root/account administrator secret.
- On this **public research repository**, whoever can change executable code or deployment workflows on main can potentially abuse CI credentials. The Cloudflare Editor token intentionally limits damage to the **synthetic lab Worker**. Keep real memory, owner accounts and the production credential broker elsewhere. Main protections and deployment permissions must be reviewed before expanding the scope.
- This workflow doesn't create arbitrary new Workers (that needs separately authorized provisioning), spend money, accept user memory, or manage other Cloudflare products. It does not run on PR events, forks, or feature branches.
- Worker edits may read its own runtime secrets; do not bind broader account credentials to it. A runtime secret is not a boundary against someone who can deploy replacement code.
- Secrets are never echoed. If the deployment token is revoked, deployment fails safely. A zero-value bootstrap skips rather than silently claiming a real Cloudflare run.
- Repeated pushes can restart the bounded synthetic experiment; avoid storing consequential tasks in this lab. The research stop condition remains two actual wakes and two LLM calls with a measured free-tier receipt.

Official Cloudflare documentation (2026-11-16):
- https://developers.cloudflare.com/workers/authorization/workers/
- https://developers.cloudflare.com/changelog/post/2026-09-15-granular-worker-permissions/
- https://developers.cloudflare.com/fundamentals/api/get-started/account-owned-tokens/
- https://developers.cloudflare.com/workers/ci-cd/builds/configuration/
