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

