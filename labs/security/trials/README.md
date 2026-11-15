# SEC-001 — First isolated vendor evidence

These are **real vendor services on ephemeral GitHub Actions runners**, not mocks of their health and API endpoints. Inputs, accounts, keys and project data are **synthetic only**. No cloud credentials, user accounts or Miss Lea memory are used.

## Comparable question and explicit limitations

| Item | OpenBao | Infisical |
| --- | --- | --- |
| Version used | `ghcr.io/openbao/openbao:2.7.2` | `infisical/infisical:v0.167.10` + ephemeral PostgreSQL/Redis |
| Actual operation in initial trial | Mount KV-v2, create narrow read policy, issue a synthetic scoped machine token, verify prohibited operations and revoke | Start server and verify the real `/api/status` endpoint; no user signup |
| What it proves | An isolated OpenBao dev instance **actually enforces** synthetic token scopes and revocation | A self-hosted Infisical **can start** under the tested setup |
| What it does **not** prove | Durable/AppRole identity, unseal after host loss, safe LLM broker, code-deploy isolation | **Any machine identity, scoped policy, revocation, secrets API or recovery** |
| Evidence comparability | Scoping/revocation tested | Scoping/revocation **NOT TESTED** — no head-to-head security winner |

The tests are deliberately unequal in scope because Infisical self-host first requires a database and initial administrative signup/project bootstrap. We do **not** manufacture a passing result by mocking its APIs. A later, minimal Infisical identity trial is necessary **only if documentary gating does not rule out the intended Free configuration**.

## Initial documentary gate on Infisical Cloud Free

Current [official pricing](https://infisical.com/pricing) lists a Free plan with **5 identities**, while **Access Controls**, **Secret Rotation** and **30-day audit log retention** are listed under Pro. Consequently the hosted *Free* plan cannot be presumed to satisfy SEC-001 S2, S3 and S6 without a separately implemented Broker and independent audit. This is a documented feature constraint, not a proof that Infisical self-hosted cannot work.

The [OpenBao dev server](https://openbao.org/docs/concepts/dev-server/) is an insecure, memory-only test mode; it must never be used to hold real Miss Lea credentials. A green scoped API trial is not an endorsement of the production seal/unseal, persistence or backup configuration.

## How to run without the user's computer

Both isolated jobs are defined in [security-vault-trials.yml](../../../.github/workflows/security-vault-trials.yml). PR changes to the trial trigger GitHub Actions; the workflow also supports explicit manual dispatch after merging.

**Expected output:** two evidence artifacts with sanitized booleans and a list of **NOT TESTED** gates. Their presence means the jobs completed, **not** that a selected vault is safe for real keys. The workflows remove the containers; no stored Cloudflare or login tokens.

## Next decision gate

Only after reviewing these results against [SEC-001 criteria](../selection-criteria.md) should we decide whether to:
- test Infisical Free's actual machine authentication and authorization with a temporary permitted account (not yet authorized); or
- prefer the self-managed OpenBao route and test protected deployment, AppRole, durable storage, independent unseal/recovery and an isolated credential Broker on a synthetic dataset.

**Selection status: DEFER**, while mandatory recovery, code-deployment separation, and LLM-safe Broker gates remain NOT TESTED.
