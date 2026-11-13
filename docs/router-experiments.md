# LLM Router Lab — synthetic selection protocol

## Scope

Select an existing, replaceable router that can direct Miss Lea to independent **free-tier** model APIs while using **OpenRouter only as a paid pool**. A route's price class is a **policy**, not a property inferred from a model name. OpenRouter `:free` endpoints are excluded from the intended free-provider pool. Never send experimental traffic to real paid endpoints.

Four candidates are tracked. All four now have synthetic-run profiles; their actual CI outcomes and limitations are recorded in the comparison report. Configurations differ: GoModel has no fallback in this profile. A runnable profile is not a production endorsement.

| Candidate | Runtime | Status in this PR | Research question |
| --- | --- | --- | --- |
| [LiteLLM](https://github.com/BerriAI/litellm) | Python + optional PostgreSQL | Docker profile, synthetic provider fallback | Breadth vs footprint, auth and budget dependency |
| [GoModel](https://github.com/ENTERPILOT/GoModel) | Go | Docker profile, synthetic basic access | Footprint, feature completeness, governance |
| [Bifrost](https://github.com/maximhq/bifrost) | Go | Docker profile, three synthetic custom upstreams | Key/budget governance, failover, management overhead |
| [Portkey Gateway](https://github.com/Portkey-AI/gateway) | JS runtime | Docker profile, fixed local routing targets | Low memory, OSS feature availability, outbound host controls |

## What the synthetic experiment proves

Three *local* OpenAI-compatible endpoints represent `primary` free provider, `backup` free provider, and an explicitly billed `paid` provider. They do not call any network AI service and never receive actual credentials.

1. Ordinary chat reaches the correct free primary.
2. A simulated HTTP 429 on primary can fall back to backup, if the profile enables this.
3. A simultaneous outage on all free mocks **does not call the paid mock**, regardless of HTTP response.
4. Explicit selection of a mock paid model is possible where configured, and never happens implicitly.
5. Tool calling and SSE streaming are observed and reported, but do **not** pass the critical gate until demonstrated.
6. Restore and budgets are **not** tested here. Zero-dollar fake calls do not prove actual spending limits.
7. Record exact image version/digest, cold start, RSS, and p95 latency on a consistent machine **before choosing a winner**.

A candidate only passes the *critical* gate when basic chat reaches the primary and the all-free outage fails closed. For profiles with configured fallback, backup must actually answer the 429 scenario. An unconfigured fallback is reported `not_tested`, not a passing test. Tools/streaming can fail without falsely failing the safety gate; feature gaps remain visible.

## Run with Docker (public synthetic fixtures only)

```bash
bash scripts/run_router_trial.sh litellm
bash scripts/run_router_trial.sh gomodel
bash scripts/run_router_trial.sh bifrost
bash scripts/run_router_trial.sh portkey
```

Requires Docker Engine/desktop with Linux containers, Python 3.11+, and the ability to fetch public images. The script uses `--network host` (Linux only); on Docker Desktop the host-network feature depends on host configuration, so run through a Linux VM or GitHub Actions if unavailable.

The script starts local mocks on ports 19100–19102 and the selected gateway on 4000 (LiteLLM), 8080 (GoModel/Bifrost), or 8787 (Portkey), cleans them up on exit, and writes JSON reports to `reports/` (gitignored). Review scripts before running. **Never introduce real provider keys to these profiles.**

### Real provider acceptance (future PR)

In a strictly private local setup, connect **at least three direct, independent free providers** and paid OpenRouter separately. Verify true provider quotas, exact model metadata, embeddings, tools, model switching across sessions, and outbound-request logging. Authenticate calls with a separate limited-key identity; verify actual spending caps at the provider as well as in the gateway. The free pool must fail closed if all free routes are exhausted.

Free tiers may change, require human registration, and may apply data-use terms unsuitable for private memory. This synthetic suite verifies neither vendor economics nor their privacy guarantees.

### Security

All public CI uses fabricated keys and endpoints on loopback only. Running gateway images can fetch updates/telemetry under upstream defaults, so this is **not an air-gapped test**. Pin and review external dependencies for production; do not expose gateway admin interfaces publicly. In particular, Portkey has publicly reported SSRF defects including CVE-2026-82270 affecting versions through 1.15.2. This lab uses only synthetic credentials and known fixed loopback targets; successful local routing does not mitigate this risk or authorize real-key deployment. See [security report](https://github.com/advisories/ghsa-rv66-rgwx-xfrj).
