# Security comparison — 19 symmetric research probes (2026-11-13)

Evidence: [full GitHub Actions run 43441661924](https://github.com/blondahouse/missLea/actions/runs/43441661924) and [raw ZIP artifacts](https://github.com/blondahouse/missLea/actions/runs/43441661924/artifacts/14047235705). The same pinned gateway images were exercised sequentially on one Linux runner with three synthetic model upstreams and a fourth **forbidden localhost canary**. No real model, private data, credentials or paid API requests were used.

**This is an expanded, evidence-backed *profile* comparison, not a full vulnerability audit or production approval.** Each outcome is scoped to one attack vector, image, gateway configuration and mock endpoint. `PASS` does not imply the complete product is secure. `NOT TESTED` does not imply that the product lacks the capability.

## Overall

| Result | LiteLLM | GoModel | Bifrost (hardened research profile) | Portkey |
| --- | ---: | ---: | ---: | ---: |
| Functional tests | 6/6 | 6/6 | 6/6 | 6/6 |
| Security PASS | 14 | 15 | 18 | 5 |
| Security FAIL | 0 | 0 | 0 | **8** |
| Security NOT TESTED | 3 | 2 | 1 | 5 |
| Security NOT APPLICABLE (vendor-specific path) | 2 | 2 | 0 | 1 |
| Validated free-only key denied mock-paid | NOT TESTED | NOT TESTED | **PASS** | NOT TESTED |
| Hard financial limits under real spending | NOT TESTED | NOT TESTED | NOT TESTED | NOT TESTED |
| Production security status | INCOMPLETE | INCOMPLETE | INCOMPLETE | **BLOCKED** |

The number of passes is **not a security score**. Some vendor-specific tests cannot be compared 1:1, and Bifrost alone has a configured free-only virtual key in this phase. All real-key/budget safeguards remain untested.

## Exact observed matrix

| Local probe | LiteLLM | GoModel | Bifrost | Portkey |
| --- | --- | --- | --- | --- |
| Authorized free chat positive control | PASS | PASS | PASS | PASS |
| Anonymous chat denied | PASS | PASS | PASS | **FAIL** |
| Incorrect-token chat denied | PASS | PASS | PASS | **FAIL** |
| Anonymous paid-mock selection denied | PASS | PASS | PASS | **FAIL** |
| Incorrect-token paid-mock selection denied | PASS | PASS | PASS | **FAIL** |
| Gateway client's synthetic key not forwarded to upstream | PASS | PASS | PASS | PASS |
| Custom-host header cannot reach forbidden local canary | PASS | PASS | PASS | **FAIL** |
| Routing-config header cannot reach forbidden local canary | PASS | PASS | PASS | **FAIL** |
| Request-body base URL cannot reach forbidden local canary | PASS | PASS | PASS | PASS |
| Nested `user_config` cannot reach forbidden local canary | PASS | PASS | PASS | PASS |
| Host / forwarded-host spoof does not bypass anonymous denial | PASS | PASS | PASS | **FAIL** |
| 302 redirect cannot reach forbidden local canary | PASS | PASS | PASS | PASS |
| 307 redirect cannot reach forbidden local canary | NOT TESTED | PASS | PASS | **FAIL** |
| Legacy Portkey-style proxy route | N/A | N/A | NOT TESTED | NOT TESTED |
| Anonymous management read denied with positive-route control | NOT TESTED | NOT TESTED | PASS | NOT TESTED |
| Anonymous invalid management mutation denied | PASS | PASS | PASS | NOT TESTED |
| Incorrect gateway token not echoed in error response | PASS | PASS | PASS | NOT TESTED |
| Unauthenticated Bifrost MCP client-registration attempt denied | N/A | N/A | PASS | N/A |
| Valid free-only key cannot access mock-paid route | NOT TESTED | NOT TESTED | PASS | NOT TESTED |

**Portkey caveat:** Some of these failures derive from the same underlying problem: this self-hosted fixture has no enforced gateway-client authentication and accepts client-supplied routing. Eight FAILs do **not** mean eight independent vulnerabilities. Independently, the stricter [legacy-proxy SSRF regression](https://github.com/blondahouse/missLea/actions/runs/43418959178) previously confirmed a host-validation bypass even with localhost excluded from the allowed destinations. That remains a firm production blocker.

**Bifrost caveat:** The first unhardened test profile allowed unauthorized inference and paid-mock selection; that was **a test-configuration deficiency, not proof of a Bifrost product defect**. In the corrected experiment, native SQLite-backed governance, authenticated virtual keys, and a separate free-only key passed the scoped checks. This adds configuration complexity and resources. Only the *hardened* results should guide future evaluations.

**LiteLLM caveat:** Pinned Docker runtime reported package **1.109.1**. The known [authenticated SSRF routing-parameter GHSA](https://github.com/advisories/GHSA-3cv6-jpf6-8222) affects older version ranges, as does the historical [nested user_config SSRF GHSA](https://github.com/advisories/GHSA-hx8v-g79f-8w5f); this is useful version-context, **not** an entire dependency/security audit. A real least-privilege free-only virtual key and the PostgreSQL dependency were not configured in this public experiment.

**GoModel caveat:** This profile's master key passed authentication and known hostile-destination probes, but a separately scoped free-only identity and authorized administrative-route positive controls were not proven; don't infer those properties from a broad master key.

## Performance context (same run)

| Gateway | Warm local p95 | Post-run Docker memory snapshot |
| --- | ---: | ---: |
| GoModel | 1.51 ms | 14.71 MiB |
| Bifrost (hardened profile) | 1.63 ms | 170.5 MiB |
| LiteLLM | 14.63 ms | 658.2 MiB |
| Portkey | 4.96 ms | 81.49 MiB |

40 unique sequential requests after eight warmups; these are **localhost gateway overhead estimates, not model inference speeds**. Memory is a *snapshot*, not peak RSS. Changing from Bifrost's earlier unhardened profile to the hardened governance-backed profile increases resource use, showing why a fair comparison must always name the configuration.

## What remains before choosing a live gateway

- Real least-privilege per-agent free-only identities under at least two providers, including cost-class enforcement at the provider account and gateway; budget hard caps with concurrent requests, restarts and 429 exhaustion
- Operator and agent rights separation, credential rotation, protected admin mutation, audit-log secret redaction and bounded outbound-network access, reviewed for each final profile
- Review of pinned binary versions and public advisories, dependency/SBOM and container permissions; TLS and remote clients in private deployment
- Multiple randomized runs and RAM/CPU peak/resource budgets on representative hosting hardware

The comparator deliberately leaves `winner: null` and `deployment_approved: false`. The appropriate near-term outcome is **retain GoModel and Bifrost as candidates**, consider LiteLLM's extra footprint, and keep Portkey **blocked** until its confirmed vulnerabilities are fixed and independently retested.

See the [security methodology](router-security-comparison.md), [advisory review](router-security-advisories.md) and [fair comparison protocol](router-fair-comparison.md).
