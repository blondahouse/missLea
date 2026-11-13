# ADR-001 — LLM Router for Miss Lea Demo

**Status:** SELECTED for the first Demo integration; **NOT approved for deployment with real provider credentials or paid calls**  
**Decision date:** 2026-11-13  
**Choice:** **Bifrost**, using a pinned, self-hosted, governance-enabled configuration and an agent credential restricted to direct free providers. **GoModel** remains the primary replacement candidate.

## Decision scope

This is a **technology selection**, not an assertion that Bifrost is universally better or has passed a complete security audit. The initial workload is a single autonomous agent, modest compute, intermittent model requests, direct free provider APIs, tool calling and streaming. Paid OpenRouter is **not** required for the first Demo integration, and paid provider credentials must not be provisioned to the agent.

The aim is to start integrating a suitable replaceable component. We will not prolong the selection stage to resolve every hypothetical security or performance question.

## Stable selection policy

The policy is based on Miss Lea's requirements and is adopted **now**, with the existing evidence applied below. It must not be retroactively changed merely to favor a different candidate.

### Hard gates for selecting the first Demo integration candidate

1. **Functional fit (G1):** all six fixed synthetic routing tests pass: primary response, free-to-free 429 failover, no silent paid escalation on total free outage, tool calls, streaming, and explicit paid-*mock* routing.
2. **Least privilege demonstrated (G2):** a *separate non-admin, free-only agent key* reaches an allowed free provider and demonstrably cannot invoke the paid mock. Anonymous and invalid credentials are rejected. A claim in vendor documentation without a runnable proof is **UNKNOWN**, not PASS or UNSUPPORTED.
3. **No observed blocking defect in the tested profile (G3):** no failed high-risk local security check or known reproduced unmitigated vulnerability in that pinned deployment configuration. A passing local suite is **limited evidence**, not a broad security certification.
4. **Replaceability and reproducibility (G4):** available self-hosted, open-source build; pinned image; documented settings and persistent state can be exported/backed up. No bespoke gateway fork or mandatory paid control plane.
5. **Practical overhead (G5):** runs on the intended modest host without disproportionate fixed cost. Prefer smaller RAM, simpler operations and lower measured overhead *after* G1–G4; treat single-run cold starts and RAM snapshots as estimates, not binding rankings.

**No weighted score.** A candidate with unverified G2 does not win merely because it uses less RAM; a candidate with a known security blocker cannot win because it has more features. Conversely, an unverified criterion does **not** prove a product is incapable of meeting it.

### Tie-breaker

If several candidates satisfy G1–G4 on equivalent hardened profiles, choose the **simpler, lower-resource** one with adequate maintainability, portability and support. Tens of milliseconds of local gateway overhead are negligible relative to model inference; do not optimize for them over authority isolation and spending safety.

## Evidence applied — current pinned research profiles

| Candidate | G1 functional | G2 tested free-only key | G3 scoped security | Measured post-trial RAM | Decision |
| --- | --- | --- | --- | ---: | --- |
| **Bifrost** (hardened, SQLite governance) | 6/6 | **PASS** | 18 PASS / 0 FAIL / 1 untested; no blocking finding in tested profile | ~170 MiB | **SELECT for first Demo integration** |
| **GoModel** | 6/6 | **UNKNOWN** in tested profile; documented user-path/model allowlists exist | 15 PASS / 0 FAIL / 2 untested / 2 N/A | ~15 MiB | **Primary challenger; not rejected** |
| **LiteLLM** (without PostgreSQL key governance) | 6/6 | **UNKNOWN** in tested profile | 14 PASS / 0 FAIL / 3 untested / 2 N/A | ~658 MiB | Reserve alternative; extra persistence dependency/footprint |
| **Portkey** | 6/6 | Not established | 8 observed failures plus a separately reproduced legacy proxy SSRF bypass | ~81 MiB | **BLOCKED** |

Source: [19-vector security results](router-security-results-2026-11-13.md), [fair testing methodology](router-fair-comparison.md) and [CI evidence](https://github.com/blondahouse/missLea/actions/runs/43442556101). These are configuration-specific synthetic results, not product-wide rankings. The memory numbers are **single snapshots**, not peak RSS.

The GoModel project documents managed keys, user paths and model allowlists ([upstream guide](https://github.com/ENTERPILOT/GoModel/blob/main/docs/features/user-path.mdx)), but our **pinned profile** has not demonstrated the same restricted free-only identity. Its very small measured footprint is a genuine reason to keep it on the shortlist, not to bypass G2.

### Spending policy

For the first Demo deployment **no paid upstream account/key is configured at all**. A free-only routing policy and a non-admin key are the first controls; absence of paid provider credentials is the stronger independent boundary. A fallback must never silently cross into a paid cost class.

No candidate has passed a real-money budget-cap test. Specifically, GoModel documents that its budgets are **soft limits** because usage is recorded in batches and concurrent requests may overshoot ([upstream budget guide](https://github.com/ENTERPILOT/GoModel/blob/main/docs/features/budgets.mdx)). Do **not** treat gateway-side accounting as a hard loss limit for any candidate. Paid usage, if introduced later, requires independently enforced provider/account caps and an explicit owner-approved spending policy. This is a **future Live gate**, not a reason to delay free-only technology selection.

## Remaining checks are implementation acceptance, not another product tournament

Before handling **real free-provider credentials**, the selected Bifrost integration must verify only:

1. **Two independent direct free provider APIs:** successful requests plus tool calling, streaming and a real 429/quota fallback, with no unintended paid calls.
2. **Role/secret isolation:** the agent receives only its tested restricted key; operator administration, provider secrets and persistent governance state are inaccessible to it. Confirm outbound destinations and that sensitive material is not exposed through errors/logs in this deployment.
3. **Recovery and reversibility:** persist/restore Bifrost configuration and governance database, restart cleanly, and prove the restricted key remains restricted. Keep existing Miss Lea deployment untouched until an independently approved cutover.

No real credentials belong in the public repository or GitHub Actions. These are bounded checks for integrating **the chosen solution**, not a requirement to re-test all four gateways. A failure blocks rollout and triggers remediation or reconsideration; it does not silently approve a different candidate.

## When to reconsider

Revisit the choice only for a **material trigger**: the Bifrost implementation fails an acceptance gate; a confirmed unmitigated vulnerability affects its pinned profile; its persistent governance or free-provider compatibility is unacceptable; its operating cost is materially disproportionate; or GoModel demonstrates equivalent scoped authorization **and** offers a worthwhile operational benefit on the actual host.

A new version or an attractive synthetic benchmark alone is **not** a trigger to rebuild the agent.

## What this record does and does not authorize

- **Authorizes:** starting a small, reversible Bifrost integration for Demo, with direct free provider APIs and independent controls.
- **Does not authorize:** modifying the currently running Miss Lea, using real paid credentials, automatic cutover, or treating 19 synthetic security probes as a certification.
- The synthetic comparator may continue to report `winner: null` and `deployment_approved: false`. Those fields concern **production admission**, whereas this ADR records the **first integration candidate**.
