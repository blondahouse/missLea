# LLM Router Lab — Fair Comparison Protocol (v1)

## The question

Which existing LLM router can Miss Lea operate economically and safely? A single green GitHub Actions run cannot determine that. The purpose of this PR is to fix *measurement asymmetry*, not to invent a winner.

### Evidence taxonomy (never collapse statuses)

- **PASS**: identical functional scenario exercised successfully; mock-provider call audit confirms the result.
- **FAIL**: scenario exercised and the behaviour missed acceptance.
- **NOT TESTED**: there is no valid measurement; neither positive nor negative score.
- **UNSUPPORTED**: independently verified vendor/version cannot implement the requirement with an acceptable supported configuration. No undocumented guess counts.
- **SECURITY BLOCKER**: known reproduced high-risk defect; vetoes production eligibility even if functionality works.

No averaged weighted score is generated. Budget safety and secure self-management are **mandatory prerequisites** for a production candidate, so a missing check blocks final approval without being presented as a failed product.

### Functional comparison

Every gateway is configured with **three actual independent loopback endpoints**: free-primary :19100, free-backup :19101, and explicitly selectable mock-paid :19102. Every candidate must demonstrate:

1. Primary chat returns the primary response.
2. HTTP 429 on primary actually reaches the free backup.
3. 503 from both free upstreams fails closed, with **zero** mock-paid requests.
4. Tool-call metadata survives.
5. Streaming SSE survives.
6. An explicitly selected paid *mock* route makes exactly one paid mock call.

The gateway-native configuration is intentionally visible rather than forced to use identical configuration files:
- LiteLLM: server-side aliases/fallbacks.
- Bifrost: request-level fallback list of only free upstreams.
- GoModel: virtual model with priority failover to vLLM and SGLang mocks; separate OpenAI-compatible mock-paid provider.
- Portkey: documented `x-portkey-config` with local hardcoded targets. **Portkey remains security-blocked**.

A request-level routing contract is an architectural difference relevant to autonomous governance, not a reason to fake a functional failure.

### Performance comparison (synthetic, preliminary)

A new CI job **pre-pulls the exact digest-pinned images** and runs all four gateways *sequentially on one runner*. Each gateway gets 8 warmup + 40 single-concurrency measurements with unique prompt IDs; mock-provider request audits reject hidden response-cache shortcuts. Report nearest-rank p50/p95 latency and cold readiness from container start until gateway health succeeds, with image already pulled. Record a single post-trial Docker resource snapshot and the test order. Rotate trial order between CI runs.

**Limits:** one runner is not stable hardware across runs. Sequential order, startup disk cache, HTTP connection reuse, gateway-native headers, cross-process mocks and background load all remain confounds. Cold readiness is *one measurement*, not a startup distribution; resource snapshot is *not peak RSS*. Do not rank candidates by these numbers alone. Future work can add multiple randomized replicates, cgroup peak sampling and confidence intervals.

### Security and budgets: common negative probes without false assurance

The [symmetric security suite](router-security-comparison.md) exercises all four gateway profiles with distinct synthetic client/upstream tokens, a fourth forbidden loopback canary, anonymous and wrong-key chat, unauthorised paid selection, alternate routing, 302/307 redirect handling, management read/write paths and credential reflection. Every vector has an individual verdict and observed upstream traffic. The **same threats** apply to each candidate; vendor-specific routes can be `NOT APPLICABLE` rather than pretend-pass.

The shared fixture profiles are not necessarily production-hardened. A failed auth test is a failure of the *current tested profile*, not proof that vendor-supported authentication cannot work. Unknown route, admin or scope coverage stays `NOT TESTED`. The hardened Portkey regression remains independent and explicitly blocks Portkey.

### Previously untested areas remain honest

- Portkey's pinned image is known **VULNERABLE** to a reproducible localhost SSRF bypass through `/v1/proxy/*`; this is a production veto.
- Other gateways have **NOT TESTED** security status; we do **not** mark them safe merely because no SSRF test was written.
- Nobody passes **real budget enforcement** yet: local mock requests cannot prove paid-provider billing guarantees or hard limits across restarts and concurrency.
- At a later private stage, use bounded keys, actual provider account caps and fail-closed policy to verify rate limits, budget exhaustion, identity scoping and disallowed user-supplied destinations. No real API keys belong in this public repository or GitHub Actions.
- Nonavailability of provider API access is `not_tested`, not `unsupported`.

### CI and interpretation

```bash
python -m unittest discover -s labs -t . -p 'test_*.py' -v
bash labs/llm_router/scripts/run_fair_comparison.sh
```

The execution produces `reports/fair-comparison.json`, four per-router security reports, four functional reports and four warm latency reports, the individual image digests, cold-readiness timing and Docker snapshot, and an order manifest. Synthetic CI must fail if a mandatory functional test is missing or fails; Portkey vulnerability is reported separately as a **security blocker even if diagnostic execution succeeds**.

The report's `winner` stays `null`, and `deployment_approved` remains `false`, until critical non-synthetic validation is complete.
