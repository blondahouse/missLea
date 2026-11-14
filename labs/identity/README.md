# Identity & Capability Hub — Lab 1

This is an **offline, synthetic first slice** of the [digital independence principle](../../docs/digital-independence.md). The research repository is not the running Miss Lea. This lab does not register accounts, access real email, use genuine credentials, spend money, or provide production authentication.

## Research question and acceptance criteria

Can a portable inventory describe digital resources and explicitly delegated authority without revealing credentials to an agent, while denying unauthorized actions and preserving an auditable record?

Acceptance criteria for this slice:

1. Describe **legal account holder, operational controller, billing party, recovery authority, human bootstrap and transferability** independently. Unknown fields are not inferred.
2. Grant only a specific **subject + resource + action**, with expiry and revocation. No wildcard, paid or account-creation authority.
3. Keep credentials out of agent-visible inventory, audit logs and SQLite snapshots. The registry contains an opaque credential *handle* only; a separate mock broker holds a fake secret in memory.
4. Restore the SQLite record consistently without automatically enabling execution for a restored process.
5. Demonstrate synthetic compute, denial and revocation with **zero external calls**.

**Stop condition:** stop this PR after the offline evidence passes. New accounts, email, phone, browser registration, real keys, wallets and cards require distinct, explicitly authorized experiments. No provider winner or production readiness is claimed. See the [project-wide evaluation policy](../../docs/evaluation-policy.md).

## Included

- `hub.py`: SQLite resource registry, scoped grants, expiry/revocation, audit and consistent snapshot.
- `SyntheticBroker`: mock demonstration of a mediated `compute.run` action. Other action scopes are not implemented, even if present in the policy vocabulary.
- `cli.py`: disposable synthetic run, revoked-access denial, snapshot and inactive restore.
- `tests/`: offline acceptance checks; automatically discovered by existing CI.

From the repository root (Python 3.11+, standard library only):

```bash
python -m labs.identity.cli demo
python -m unittest discover -s labs -t . -p 'test_*.py' -v
```

## Security and authority limits

**This is not an authentication or secret-management boundary.** The caller identity and privileged setup are not authenticated; Python code with access to the process or database can create grants or enable the local test session. The fake secret resides in process memory, not in a secure vault. A SQLite snapshot includes grants, but **must not confer permission for a second active instance**. The default-inactive restore is just a research safeguard; independent cryptographic authority and single-instance fencing remain future work.

Real integration will need independently authenticated callers, protected secrets and an isolated broker, provider-specific least-privilege permissions, reliable recovery and single-active-instance rules. Do **not** give this prototype a real API key, connect it to TinyFund or expose it as an agent tool.

## Cloudflare service identity — next research slice

[Cloudflare service identity protocol](cloudflare-study.md) compares an account-owned token scoped to an **existing Worker (Editor)** with a wider Workers product **Admin** token required for the current Compute Lab's create/delete test.

```bash
python -m labs.identity.cloudflare_cli simulate
python -m labs.identity.cloudflare_cli roles existing_worker
```

The optional real token *status verification* is read-only, requires two explicit flags, and does **not** prove the actual token's permissions or ownership. No live accounts or secrets are used by GitHub CI.

## Next narrowly scoped experiment

With separate authorization and a lawfully provisioned **dedicated** account, conduct a live read-only service-token verification and controlled existing-Worker deployment. Test real credential replacement and host fencing only after independently authenticated provisioning and secret custody are available. No account registration, financial commitment or provider mutation is authorized by this PR.
