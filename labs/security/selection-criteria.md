# SEC-001 — Choosing secret custody for a sustainable Miss Lea (PROPOSED)

**Recorded:** 2026-11-15 · **Decision type:** component research, NOT installation or production authorization · **Decision:** DEFER selection pending evidence · **Criteria owner:** project discussion; thresholds below are proposed for confirmation before any comparative trials.

## Actual problem

Miss Lea needs to use credentials for her own accounts without sending raw values into LLM prompts, untrusted tools, source repositories or memory. In Demo, this includes the dedicated Cloudflare account, and later email, storage and other services. Human bootstrap remains possible where required by the provider; **routine operation should not depend on the founder's computer or session**.

Three distinct roles must not be collapsed:

1. **Secret custody:** store/revoke/rotate sensitive material and issue narrowly scoped access to an independently authenticated service.
2. **Credential Broker:** interpret a limited operation request, authorize it in *trusted code*, perform the provider operation and return a non-secret result. Merely placing tokens in a vault does NOT prevent an LLM from obtaining them if the agent may call a raw-secret read API.
3. **Recovery root:** independently recover a lost vault or server without using the system it is meant to recover. Backups of memory, vault state and active permissions are different objects.

The existing [Identity Hub](../identity/README.md) uses an unauthenticated synthetic caller and is **not** an authentication boundary. The [manual Cloudflare Worker](README.md) proves only restricted task submission with its own Worker Secret, **not** a vault or Cloudflare account-token custody system.

## Prospective selection gates (proposal; do not retrofit to observed results)

The unit of comparison is **vault + feasible credential-broker deployment**, not vault brands alone. For each gate use PASS / FAIL / NOT TESTED; unknown remains **NOT TESTED**, never assumed PASS.

| ID | Type | Requirement | Minimum evidence for PASS / FAIL |
| --- | --- | --- | --- |
| S1 | Mandatory | Agent/model never receives raw provider or root credentials, even via errors or malicious tool-output instructions | Synthetic secret and attempted exfiltration through the broker; FAIL on any secret exposure |
| S2 | Mandatory | Independent service-to-service authentication and least-privilege policies; no founder login required per routine operation | Official docs plus local isolated test of a dedicated machine identity; FAIL if only an interactive founder session works |
| S3 | Mandatory | Server-side action/resource allowlist, budget guards and provider-level revocation; root/provisioning tokens isolated from ordinary operations | One positive and multiple forbidden operations, token replacement/revocation; FAIL if ordinary worker can self-grant unrestricted rights |
| S4 | Mandatory | Recover from host loss with separate retained credentials and **no circular unlock**; a restored snapshot cannot reactivate revoked authority | Documented unlock dependency graph and synthetic recovery; FAIL if recovery requires only the lost machine or deleted KMS |
| S5 | Mandatory | Demo can be studied without committing to a paid subscription; no automatic spend/upgrade | Published plan/hosting terms and setup requiring no payment method; FAIL if paid access is mandatory for required gates |
| S6 | Mandatory | Auditable operations without storing tokens/passwords in logs, traces or LLM-visible memory | Masking and independent log review; FAIL on any actual credential leak |
| S7 | Mandatory | Portability of secret metadata, policies and re-provisioning plan; lawful holder and operator distinguishable | Recreate equivalent grants using a second install/provider; FAIL on a non-exportable, unreplaceable root dependency |
| S8 | Mandatory | Revocation and identity fencing survive stale backups and parallel workers | Denial of a revoked token after recovery; exactly one externally authorized active executor |
| T1 | Trade-off | Operational effort, moving parts, manual unseal, upgrade burden | Steps and failure points to install and recover a single small Demo instance |
| T2 | Trade-off | Resource footprint, recurring cost, storage and egress | Measured minimal footprint and current documented plan limits |
| T3 | Trade-off | Vendor dependence and automated rotation | Supported auth/rotation patterns and dependencies; score only after mandatory gates |

**Safety veto:** any real secret reaching an LLM; use of the founder's personal identity/payment instruments; automatic creation of chargeable services; an agent-accessible root/unseal key; or recovery that silently revives revoked access.

**Decision rule:** reject a candidate with a demonstrated mandatory FAIL; do not select one with mandatory NOT TESTED. Among passing configurations, prefer the least operational dependence and cost, then easiest migration. Stop after one fully passing configuration has evidence and one credible alternative is documented, or after all remaining mandatory unknowns have a stated minimum resolving test. Doing nothing is allowed.

## Candidate inventory and current documentary evidence

This is **not a benchmark or winner ranking**; each cell is a documentation lead, not proof of integration.

| Candidate | Why examine it | Material caveat / open question | Present status |
| --- | --- | --- | --- |
| **Infisical Cloud Free** | Hosted secret manager and machine identities; no self-hosted VM needed initially | Free plan currently advertises **up to 5 identities**; advanced Access Controls, Secret Rotation and audit retention are associated with paid plans. Can the free plan actually enforce S2/S3/S6 with an independent broker? | NOT TESTED |
| **OpenBao (self-hosted)** | Path-based deny-by-default policies, auth methods, audit and KV; avoids a SaaS-only vault | Sealing/unsealing and root-key recovery are non-trivial; KMS auto-unseal introduces a dependency whose permanent loss can prevent recovery even from backup. Minimum small-VM operability unknown | NOT TESTED |
| **SOPS + age (encrypted files)** | Portable, established encryption and multiple recovery recipients; small operational footprint | No resident machine-identity or action-broker service on its own. A compromised executor with decryption key may reveal all readable secrets; rotation/audit must be built around it | BASELINE / NOT TESTED |
| **Cloudflare Worker Secrets / Secrets Store** | Already use one Worker Secret; account Secrets Store beta enables reusable per-account secrets | Useful for isolated Worker operations; binding to Cloudflare and a beta service is poor as the **only** portable recovery root. Secrets are available to code inside the bound Worker | COMPONENT / NOT GENERAL VAULT |

**Important:** plan limits/prices and product behavior must be rechecked on the day of an integration decision. No keys, account tokens or private identities are to be committed as evidence.

## Least expensive next evidence, in order

1. **Document-only gate review:** identify account types, free/paid feature boundaries, machine identity, grant/revoke API, export and recovery for each candidate. Mark gates, not vanity scores. Exclude candidates with a documented mandatory blocker in the intended Demo configuration.
2. **Broker contract (synthetic):** define requests of the form `execute(resource_id,operation,parameters)` and return sanitized results. No `read_secret`, `issue_root_token` or arbitrary HTTP forwarding exposed to LLM. Simulate prompt injection, wrong actor, stale grant, compromised provider response, revocation and multi-instance conflict.
3. **Two minimum isolated candidate trials**, only if still needed to decide: authenticate a machine identity, perform one permitted operation, refuse forbidden action, revoke the identity, restart on a second host, restore from synthetic evidence and verify a stale clone stays inactive. Pin versions/configurations and provide a clean exit/teardown.
4. **Review decision and publish ADR outcome**: SELECT / REJECT / DEFER with unresolved blockers and rollback. Only later request authorization to place a real Cloudflare management token in the selected trusted host.

Do not enlarge the trial because a tool has attractive features. Security work remains independent from running TinyFund and actual paid Cloudflare operations.

## Custody and recovery ownership

- **Day-to-day keys:** held by the chosen service, accessible only to an independently authenticated, narrowly scoped broker.
- **Foundational/provisioning key:** distinct from Worker task secret; unavailable to general-purpose tools/LLM. A trusted provisioning service may be authorized *later*.
- **Emergency key/recovery shares:** separate physical/logical failure domain, never included with the encrypted data they unlock. Founder may bootstrap initially; replacing founder dependence is an explicit later criterion, not a claim already achieved.
- **Live state, grants, secret store and backups** require independent recovery paths. A database copy alone confers no executable authority.

## Source-of-record references (checked 2026-11-15)

- [Infisical pricing and free-plan feature boundaries](https://infisical.com/pricing)
- [Infisical machine identity authentication](https://github.com/Infisical/infisical/blob/main/docs/documentation/platform/identities/machine-identities.mdx)
- [OpenBao policies](https://openbao.org/docs/concepts/policies/)
- [OpenBao seal, unseal and KMS failure modes](https://openbao.org/docs/concepts/seal/)
- [SOPS supported formats/key providers](https://github.com/getsops/sops/blob/main/README.rst)
- [Cloudflare account Secrets Store (beta)](https://developers.cloudflare.com/secrets-store/)
- [Cloudflare Worker secret bindings](https://developers.cloudflare.com/workers/configuration/secrets/)
- [Cloudflare Secrets Store limits](https://developers.cloudflare.com/secrets-store/manage-secrets/)
- [Project evaluation policy](../../docs/evaluation-policy.md)
