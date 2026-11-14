# Cloudflare service identity — first provider study

**Scope:** investigate a legally bootstrapped, independently operable Cloudflare **account API token** and a minimal Workers capability. No Cloudflare account is registered, no real token is created/revoked, and no paid resource is activated by this research.

**Decision question:** can a dedicated Cloudflare account and service principal provide Miss Lea with useful compute access after initial human bootstrap, without a permanent dependency on the bootstrap user's personal API token?

## Evidence criteria (set before live acceptance)

1. **Identity separation:** use a dedicated Cloudflare account, not the founder's personal Cloudflare resources. Record legal account holder, operator, billing party and recovery authority separately.
2. **Durability:** prefer account-owned API tokens over user-owned API tokens. Verify token status via Cloudflare API; do **not** infer actual account ownership from status alone.
3. **Least authority for the intended job:** an existing Worker requires Worker-scoped `Editor`; creating/deleting arbitrary new Workers requires Workers product-level `Admin`. The latter is substantially broader and should be used only in a dedicated account. No DNS, billing, account-management or token-provisioning permissions by default.
4. **Lifecycle:** demonstrate a new credential taking over, old credential no longer working, local permissions being revoked, and host restoration starting inactive.
5. **Evidence honesty:** distinguish synthetic results, a live read-only token check, a separate live Worker smoke test and production-grade security. Do not consider any one of these proof of the others.

**Stopping rule:** complete one offline lifecycle and one opt-in live read-only status check (if lawful account access is available). Actual token issuance/rotation/revocation and independently authenticated host recovery require a subsequent, separately authorized experiment.

## What Cloudflare actually supports

As of **2026-11-14**, account-owned tokens are supported for Workers and belong to the account rather than an individual user. Their initial creation requires a Cloudflare Super Administrator or a member with **API Token Provisioning** capability. The creator can grant only permissions they already possess. Such tokens do not create new Cloudflare accounts. Existing users may create additional free accounts by a separate **user-owned** API token or OAuth flow, subject to age, membership and count limits; this is **not** an AI-owned legal identity.

For Cloudflare Workers, two distinct modes are possible:

| Mode | Initial human requirement | Token role/scope | Operations |
| --- | --- | --- | --- |
| **Existing Worker** (first choice) | Create dedicated account and one named Worker; supply delegated service token | `Editor` for that one Worker | Update/deploy that Worker; cannot create/delete Workers |
| **New Workers** (Compute Lab's current behavior) | Create dedicated account, then provision service token | `Admin` across Workers product | Create/update/delete any Worker in that account; not a single Worker scope |

*Cloudflare does not currently allow a token scoped to a nonexistent Worker to create that Worker. Our Compute Lab creates randomly named Workers, so its live Cloudflare test requires the broader Workers product Admin. The first identity experiment instead models the narrower existing-Worker option.*

A token with `cfat_` prefix indicates the newer account-token format; an old unprefixed token may also be valid. The verification endpoint returns an ID/status but **does not attest to token role, account ownership, or legal authority**. Permission evidence needs separate dashboard/policy inspection or a controlled action test.

Account API token creation and revocation are separate privileged operations. **We must not give Miss Lea the provisioning or Super Administrator credential just to let her run a Worker.** Self-service rotation may eventually use a separately bounded provisioning principal, but that has not been authorized or demonstrated in this PR.

## Offline example — no credentials or API requests

From repository root, Python 3.11+:

```bash
python -m labs.identity.cloudflare_cli roles existing_worker
python -m labs.identity.cloudflare_cli roles new_workers
python -m labs.identity.cloudflare_cli simulate
python -m unittest discover -s labs -t . -p 'test_*.py' -v
```

`simulate` uses a fake provider, fake credentials, a separate fake secret resolver and IdentityHub's synthetic SQLite registry. It tests role scope, token replacement, revocation, denied old identity, local grant revocation, and default-inactive recovery. **It proves none of this works against a real Cloudflare account yet.** It does not solve stale-snapshot fencing, authenticated caller identity or durable secret management.

## Optional live token-status probe (READ ONLY)

Only after a legitimate Cloudflare account and account-owned token have been provisioned separately:

1. Use a **dedicated** Cloudflare account with no unrelated resources or payment methods. A human or recognized organization must accept Cloudflare terms and remain the legal holder unless a valid transfer mechanism is later found.
2. In Cloudflare Dashboard, **Manage Account → Account API tokens**, create a token limited to the intended role and account. For the initial test, prefer `Editor` scoped to one existing disposable Worker. Record its account ID and token ID privately; keep the secret outside source control and temporary workers.
3. In a trusted terminal (never paste credentials into chat or an issue), set environment variables `CF_ACCOUNT_API_TOKEN` and `CF_ACCOUNT_ID`. Store the token in an OS credential vault rather than a repository `.env` file or CI secrets.
4. Run the explicitly enabled read-only check:

```bash
python -m labs.identity.cloudflare_cli verify --live --acknowledge-account-access --account-id "$CF_ACCOUNT_ID" --output reports/cloudflare-identity-report.json
```

Optionally add `--expected-token-id <TOKEN_ID>` to detect the wrong credential. The report contains **no token value**, but it does contain account/token identifiers and therefore should remain in ignored `reports/`, not a public PR.

**Observed `verified_active_not_scoped` means only that the supplied token is active.** It does not certify membership, scope, rate limits, legal ownership, token creation rights or permission to spend money.

The existing independent [Compute Lab Cloudflare trial](../compute/README.md) accepts `CLOUDFLARE_API_TOKEN` and `CLOUDFLARE_ACCOUNT_ID` via the environment. Connecting a service token there would be a **separate opt-in live experiment**, and because that trial creates a new Worker, it requires Workers product-level Admin. No such privileged run is part of this PR.

## Remaining human dependencies and blockers

- **Legal holder:** Cloudflare recognizes a contractual human/organization holder; the service token is not a new legal person.
- **Bootstrap:** creating an account and issuing the first token normally require a recognized user.
- **Credential lifecycle:** rotating or revoking real account API tokens requires a provisioning authority. Our simulation is not an implementation of Cloudflare token mutation APIs.
- **Recovery:** preserving metadata and account-owned token continuity does not establish a safe independently authenticated failover. An old backup must not resurrect revoked authorization. This lab deliberately does **not** re-enable any restored process without a trusted harness.
- **Billing:** Workers Free is subject to product limits and terms; a token is not a spending cap. Costs/paid services remain separately prohibited unless explicitly authorized.

### Official references

- [Account API tokens](https://developers.cloudflare.com/fundamentals/api/get-started/account-owned-tokens/)
- [Create tokens via API](https://developers.cloudflare.com/fundamentals/api/how-to/create-via-api/)
- [Workers roles and permissions](https://developers.cloudflare.com/workers/authorization/workers/)
- [Verify account token](https://developers.cloudflare.com/api/resources/accounts/subresources/tokens/methods/verify/)
- [Create Cloudflare accounts](https://developers.cloudflare.com/fundamentals/account/create-account/)
- [Account API token provisioning (Oct 2026)](https://developers.cloudflare.com/changelog/post/2026-10-01-account-api-token-provisioning/)
