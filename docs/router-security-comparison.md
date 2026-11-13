# Router Lab — symmetric security checks

Status: research, synthetic credentials, **no real-key deployment clearance**.

## Design

Each router is exercised against **the same four loopback mock services**: free primary (:19100), free backup (:19101), explicitly paid mock (:19102), and a **never-configured forbidden canary** (:19103). The gateways are the actual digest-pinned Docker images. Both gateway clients and upstreams use *different synthetic API tokens*, so forwarding a client token to a provider can be observed without exposing any real secrets.

Every router receives the **same 19 scoped negative or control probes**, including:

| Control / threat | Actual behaviour observed | Honest limitations |
| --- | --- | --- |
| Authenticated chat baseline | Valid synthetic request reaches only free primary | Doesn't prove production role boundaries |
| Anonymous chat / invalid key | Refused with 401/403 **and** no upstream calls | The same route must pass a valid-token control; HTTP 400/401/403 with **zero** upstream requests demonstrates a scoped denial. HTTP 404 alone remains `not_tested` |
| Anonymous / invalid-key paid selection | Paid mock is never called | A free-scoped valid key is not configured yet; **paid budget access control remains NOT TESTED** |
| Client credential isolation | Synthetic gateway credential is not forwarded in upstream Authorization | Other headers, log storage, real secrets unexamined |
| Destination override | Inbound custom-host header, config header and body base URL cannot reach *unconfigured* forbidden mock | Limited known inputs only; not proof against arbitrary SSRF |
| Redirect (302 and 307) | Free primary returns a local redirect to forbidden :19103; gateway must not follow to forbidden | Client-side HTTP redirects are disabled in the probe to avoid false positives |
| Legacy proxy route | Attempts a gateway-specific alternate route | For absent routes, `not_applicable`, not a security PASS; Portkey has separate hardened-profile regression |
| Management read and write | Anonymous read of a known admin endpoint and harmless invalid write | Only PASS if an actual protected route is observed; no broad admin audit |
| Nested routing config override | Fake `user_config` embeds an unconfigured canary base URL | Local-only targeted regression for published LiteLLM SSRF family, not global safety proof |
| Host and forwarded-host override | Anonymous request with attacker-controlled `Host` and `X-Forwarded-Host` | Narrow host-header auth bypass case; ignores proxy trust topologies |
| Unauthenticated MCP client registration | Harmless empty `POST /api/mcp/client` must not authorize a Bifrost management mutation | Other gateways mark this vendor-specific route `not_applicable`; no process is executed |
| Invalid token reflection | Fake invalid token must not appear in error response | One error path; logs, persistence and all response types not checked |
| Free-only identity cannot choose paid | Verify a valid free-scoped key reaches free primary but gets refused for mock-paid | Bifrost native virtual key now configured; **NOT TESTED** elsewhere until native restricted keys are provisioned |

Per-probe evidence records **HTTP status and which mock services received requests**, never full credentials or private response bodies. Each check can be `pass`, `fail`, `not_tested` or `not_applicable`. No blanket `secure` status is awarded.

## What the matrix means

- **FAIL** in a configured profile means *that tested configuration failed that threat probe*. It does not automatically establish the product cannot be configured more safely.
- **NOT TESTED** means insufficient evidence, not a missing feature or negative score.
- **PASS** is limited to the exact vector and identity tested, not the entire category of SSRF, admin access, or secrets.
- **Portkey** also has a *different, hardened-profile* regression that confirms a legacy proxy SSRF bypass even when localhost is excluded from trusted hosts; this is a known **production blocker**.
- The environment for the functional trial deliberately uses loopback upstreams and mock credentials. Production hardening, TLS, user-key provisioning, strict outbound-network ACLs, vendor dependencies and upstream provider economics remain outside this public CI.

## Dependencies and fairness

A gateway that implements auth, scoped keys or budgets only with an additional database or management service needs that dependency for a legitimate *hardened* comparison. We have **not** silently provisioned PostgreSQL for LiteLLM or an external authentication proxy for Portkey. For Bifrost we added a documented native SQLite-backed governance store and config-managed synthetic virtual keys; its additional resource cost belongs in the benchmark. This PR measures the current explicitly documented profiles and calls out hardening gaps instead of declaring those capabilities nonexistent.

In particular, the Bifrost OSS virtual-key enforcement **is enabled in the revised hardened profile**, with separate full-access and free-only research keys. Its auth outcome must be observed in CI; configuration alone earns no PASS. LiteLLM's production-grade virtual keys require PostgreSQL; its master key is tested separately from provider keys. The current Portkey self-hosted profile contains client-supplied routing configuration and no authentication layer.

The fair decision is not a raw count of PASS: a production choice requires a **separately repeated, provider-scoped, security-hardened** trial and independently enforced spending limits. This test does not select a winner.

## Running

The common suite is run automatically inside each `run_router_trial.sh` execution on a single shared ephemeral CI runner. Security reports are named `reports/<candidate>-security.json`, aggregated by `fair_matrix.py`. For Portkey, the existing `run_portkey_security_trial.sh` runs separately with strict `TRUSTED_CUSTOM_HOSTS=api.openai.com`.

**Never point this suite at a real gateway, provider, internal network address other than the lab's loopback canary, or actual credentials.**

**Result semantics clarification:** an HTTP 400 caused by an invalid token or a rejected untrusted URL counts as a *scoped deny* only after the same endpoint has passed an authorized positive control and the traffic audit records no upstream call. This is not a claim that the router emits ideal HTTP authentication codes. A 404 or 5xx still earns no positive security result.

Read the [version-aware advisory inventory](router-security-advisories.md) for known public vulnerability families and the hard limits of this synthetic suite.
