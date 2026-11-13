# LLM Router Lab — four candidate comparison

The same deterministic synthetic providers are used for LiteLLM, GoModel, Bifrost and Portkey. A **PASS** always requires observed mock-provider traffic; a configured feature alone cannot earn a passing grade.

| Criterion | LiteLLM | GoModel | Bifrost | Portkey |
| --- | --- | --- | --- | --- |
| Primary chat | PASS (PR #2) | PASS (PR #2) | PASS | PASS |
| Primary 429 → free backup | PASS | NOT TESTED | PASS | PASS |
| Free outage → zero paid calls | PASS | PASS | PASS | PASS |
| Tool calling | PASS | PASS | PASS | PASS |
| SSE streaming | PASS | PASS | PASS | PASS |
| Explicit synthetic paid route | PASS | NOT TESTED | PASS | PASS |
| Peak RAM / cold start | NOT MEASURED | NOT MEASURED | NOT MEASURED | NOT MEASURED |
| Budget enforcement with real keys | NOT TESTED | NOT TESTED | NOT TESTED | NOT TESTED |
| Localhost SSRF security diagnostic | NOT TESTED | NOT TESTED | NOT TESTED | **VULNERABLE** |

This table begins with the verified results of PR #2, not guessed results for new candidates. The new candidates have been exercised and verified in [PR #3 CI](https://github.com/blondahouse/missLea/actions/runs/43417421036); the previous candidates were also rerun successfully. More tests are still needed before choosing a router. Do not infer ranking from one CI run or raw latency across independently allocated runners.

Each gateway runs as its own Docker image against **three fake local model APIs**. No real provider calls or charges. Reports in GitHub Actions artifacts include per-case results, simulated paid-request counter, and a single CPU/RAM snapshot (not peak usage). Images of all four gateways are pinned to digests in the repository after CI validation.

**Security qualification:** Portkey releases through 1.15.2 have published SSRF advisories concerning routing through custom hosts; see [CVE-2026-82270](https://github.com/advisories/ghsa-rv66-rgwx-xfrj) and [CVE-2026-110719](https://www.vulncheck.com/advisories/portkey-ai-gateway-1.14.0-through-1.15.2-ssrf-via-x-portkey-custom-host-header). Do not reuse this synthetic test setup with real keys, expose it on the public network, or treat observed test success as a security audit.

## New candidates: observed sample (2026-11-13)

| Observation | Bifrost | Portkey |
| --- | ---: | ---: |
| First chat (ms) | 110.15 | 23.02 |
| Free 429 → backup (ms) | 15.25 | 21.46 |
| All-free outage (ms) | 2.84 | 6.06 |
| Unexpected simulated-paid calls during outage | 0 | 0 |
| Separate explicitly selected paid-mock calls | 1 | 1 |

Bifrost initially produced `404` without sending any mock-provider requests because the configured base URLs incorrectly included `/v1` twice. After correcting the origin URLs, its six checks passed. This illustrates why actual integrations must be tested, not assumed.

Latency samples are from independent GitHub Actions runner jobs and are **not** meaningful cross-gateway performance rankings. See the workflow artifacts for the individual JSON reports and a single Docker resource snapshot, which is not peak RSS.

## Decision

No selected winner or production deployment is implied. All three multi-upstream configurations (LiteLLM, Bifrost and Portkey) passed the functional fallbacks; GoModel fallback was **not configured or tested**. Portkey has unresolved public security concerns that require independent investigation before real-key trials. Next: uniform cold-start and resource measurements, real free-provider interoperability under bounded keys, and verified spending controls.


## Security regression diagnostic (Portkey)

A dedicated CI job exercises the **pinned** Portkey image with fake credentials and a local-only canary provider. It deliberately configures `TRUSTED_CUSTOM_HOSTS=api.openai.com`, then compares the protected `/v1/chat/completions` route with the deprecated `/v1/proxy/v1/chat/completions` route when both are asked to reach the *same untrusted localhost mock*. Expected secure behaviour is rejection by **both** routes and no traffic to the mock.

The diagnostic reports one of `VULNERABLE`, `NOT_REPRODUCED` or `INCONCLUSIVE`. **A successful CI execution is not a successful security gate**: if the published report says `VULNERABLE`, Portkey is disqualified from real-key use until an upstream fix is verified and this test reports `NOT_REPRODUCED`. The CI warning and artifact make this visible without conflating diagnostic execution with production eligibility.

The original official advisory [CVE-2025-66405](https://github.com/Portkey-AI/gateway/security/advisories/GHSA-hhh5-2cvx-vmfp) lists 1.14.0 as a fix for the first version of this issue. A later public report, [CVE-2026-82270 / Issue #1718](https://github.com/Portkey-AI/gateway/issues/1718), identifies missing validation on the deprecated route. A separate [CVE-2026-110719](https://www.tenable.com/cve/CVE-2026-110719) identifies unsafe trusted-host defaults. Current upstream source (2026-11-13) still contains both the unvalidated legacy route and localhost defaults. None of these observations is proof of **all** possible SSRF paths: redirects, other providers and authentication are outside this diagnostic.

Run on a disposable Linux host with Docker and Python 3.11+: `bash scripts/run_portkey_security_trial.sh`. **Never run this diagnostic against a real gateway or send real tokens.**

### Confirmed pinned-image security result — 2026-11-13

The [local-only regression run](https://github.com/blondahouse/missLea/actions/runs/43418959178) executed the **exact pinned Portkey Docker image** with `TRUSTED_CUSTOM_HOSTS=api.openai.com`, no provider keys, and a mock server on `127.0.0.1:19100`.

| Route | HTTP result | Unexpected calls to localhost mock |
| --- | ---: | ---: |
| `/v1/chat/completions` (validated route) | 400 | 0 |
| `/v1/proxy/v1/chat/completions` (legacy route) | 200 | **1** |

**Verdict: VULNERABLE / production gate BLOCKED.** The host validator rejects localhost on the normal route but was bypassed through the legacy route. We did not send real provider credentials or test other possible bypasses (for example redirects), and do not claim arbitrary credential theft was reproduced.

This diagnostic publishes an explicit **security failure** in the JSON report and a CI warning. Its job exits successfully when the vulnerability is conclusively detected because it is a *research diagnostic*, not a production-approval check. **Do not interpret a green CI job as a secure Portkey version.** A future patched build must return rejected requests and zero mock hits for both routes, and must be independently reviewed for the default-host and redirect issues.
