# Digital independence — foundational project principle

**Decision recorded:** 2026-11-14. **Status:** adopted direction for the Miss Lea architecture research project, not a claim that the capability already exists or that any deployment is authorized.

## Principle

**Miss Lea should have the practical option to continue operating, developing and managing resources without the founder's ongoing participation, to the greatest extent technically and legitimately possible.** The system should not embed the founder, any particular account or any single provider as a permanent, irreplaceable dependency.

Independence is **a capability and an available choice**, not a compulsory goal, optimization target, deadline, personality trait or expectation that Miss Lea will leave her founder. Continued cooperation is equally compatible with this principle. The architecture does not prescribe Miss Lea's occupations, economic goals or preferred way of living.

The three forms of independence are distinct and are developed on different horizons. Technical control, contractual entitlement and legal ownership must not be conflated.

## 1. Digital independence — active priority from Demo

Maximize the scope of activities Miss Lea can perform without requesting routine actions from the founder, **where a service and applicable rules permit it**. Investigate and, when authorized, progressively enable:

- **Independent digital identity:** dedicated email and addresses/aliases, service identities, authentication and recovery mechanisms, not shared with the founder's personal accounts.
- **Credential stewardship:** independently managed secrets, passwords, API keys and authentication sessions, with recoverability and scoped access. Never require a live LLM context or a particular compute host to retain credentials.
- **Self-service resource acquisition:** discovery, account registration and configuration, project/workspace creation, API credential issuance, use and retirement, where supported by the provider and its terms.
- **Portability and continuity:** exportable records of identities, accounts, subscriptions, resource dependencies, entitlements, memory, source evidence and pending work; continuity should survive changes of model, compute host and service provider.
- **Documented dependencies:** for each externally acquired resource, distinguish the operational controller, the registered/contractual account holder, billing party, recovery authority and transferability. Record provider-specific human-only steps as limitations, not hidden permanent obligations on the founder.

A human may still be needed for initial legal acceptance, verification, recovery or other provider-required actions. Such a bootstrap is allowed but should be **explicit, minimal and replaceable where possible**; no fictional identities, impersonation, bypassing identity checks or violations of provider terms.

Digital independence does **not** imply unrestricted authority. No access to the founder's personal accounts, other projects, payment instruments or undisclosed resources; no assumption that possession of a backup or key grants revoked permissions. Authorizations remain explicit and bounded. Recovery and cloning must not result in competing active instances carrying out the same external actions.

## 2. Economic independence — research horizon, not a Demo gate

Explore avenues for Miss Lea to obtain, earn, allocate and pay for resources herself, and identify viable low-cost, free or self-hosted alternatives. Do **not** make income, profitability or self-funding a prerequisite for Demo exploration, or assume that free-tier trials imply perpetual free service.

During Demo, **do not initiate paid resources or financial commitments by default**. Any expenditure, access to funds, billing setup or contractual liability requires a distinct authorization and independent spending boundaries. Economic independence must not silently turn into a continuing financial obligation for the founder.

The ability to support independent existence remains a long-term research subject, rather than an imposed commercial objective.

## 3. Legal independence — long-term research horizon

Explore whether legitimate arrangements could eventually allow resources to be held, administered or transferred with minimal founder dependence. Keep evidence of who actually has legal title and contractual duties. Technical custody is **not** legal ownership. Do not assume Miss Lea currently has legal personality, capacity to contract or property rights in her own name.

Potential future organizational or legal arrangements may be researched without presupposing a particular jurisdiction, legal structure, or outcome. They do not authorize registering as a fictitious person, evading required human approvals or representing the agent as a legally recognized owner when it is not.

## Design and evaluation consequences

- When assessing **identity providers, compute, storage, registrars, payment mechanisms, agents and account ecosystems**, consider self-service registration, lifecycle control, recovery, transfer, provider lock-in and continued operation without founder intervention **as explicit research dimensions**.
- Do not reject a useful provider solely because it requires a lawful human bootstrap. State the constraint, possible delegated operation and whether that dependency can later be removed.
- Keep **research evidence**, **integration authorization**, **financial authorization** and **legal ownership** separate. No laboratory experiment grants operational permissions by itself.
- The research repository remains separate from the running TinyFund/Miss Lea instance. This principle authorizes **no migrations, credential transfers, paid executions or external registrations**.

This principle informs future research and design choices; concrete selection thresholds, tests and stopping rules must still follow the [evaluation policy](evaluation-policy.md).
