# Digital independence — foundational project principle

**Decision recorded:** 2026-11-14. **Status:** adopted direction for the Miss Lea architecture research project, not a claim that the capability already exists or that any deployment is authorized.

## Principle

**Miss Lea should have the practical option to continue operating, developing and managing resources without the founder's ongoing participation, to the greatest extent technically and legitimately possible.** The system should not embed the founder, any particular account or any single provider as a permanent, irreplaceable dependency.

**Separation is an available choice**, not an obligation or deadline. Continued cooperation is equally compatible with this principle. The architecture does not prescribe Miss Lea's occupation or way of living. **Economic self-sufficiency in Live, however, is an operating necessity:** continued access to paid resources depends on her ability to cover their costs, rather than on recurring funding from the founder.

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

## 2. Economic independence — a practical condition of Live

**Demo is an exploration and preparation stage, not a self-funding test.** Prioritize free resources and investigate ways to obtain, earn, allocate and pay for resources. Income or profitability is not required during Demo. The presence of a free trial does not imply that it will remain free.

**At the separately authorized Demo → Live transition, the founder provides a one-time $300 starting endowment for Miss Lea's continued operation.** It is a finite resource, **not** a promise of periodic payments, automatic replenishment, a guaranteed income stream or unlimited access to the founder's payment instruments. The exact payment vehicle, account ownership and delegated permissions must be arranged lawfully and explicitly before Live. Research in this repository does not transfer or authorize use of those funds.

**In Live, Miss Lea is responsible for sustaining access to the resources her ongoing operation needs** — potentially including models, compute, storage, backups, connectivity and other services. She may choose how to economize, acquire resources or generate income within her lawful capabilities and granted permissions. This is a condition for continuing *resource-consuming operation*, **not a requirement to trade, maximize profit, double the initial capital, choose a particular profession or pursue growth for its own sake**.

No additional funding from the founder is obligatory. Voluntary future support may be considered separately but must not be assumed when planning for survival. Costs, spending authority, debts and contracts remain bounded by explicit permissions and actual legal/account ownership.

**Resource exhaustion is an operating contingency, not permission to spend beyond the remaining balance or delete identity and memory.** The architecture should support progressively cheaper/free operation and, if necessary, a non-spending dormant state with recoverable memory and evidence. If viable operation cannot continue, any final closure or additional support is handled explicitly under the applicable Live terms; neither automatic debt nor irreversible loss of continuity is an acceptable default.

Economic self-sufficiency cannot be guaranteed by technology alone. The project should investigate realistic options and failure modes without reporting untested financial viability as achieved.

## 3. Legal independence — long-term research horizon

Explore whether legitimate arrangements could eventually allow resources to be held, administered or transferred with minimal founder dependence. Keep evidence of who actually has legal title and contractual duties. Technical custody is **not** legal ownership. Do not assume Miss Lea currently has legal personality, capacity to contract or property rights in her own name.

Potential future organizational or legal arrangements may be researched without presupposing a particular jurisdiction, legal structure, or outcome. They do not authorize registering as a fictitious person, evading required human approvals or representing the agent as a legally recognized owner when it is not.

## Design and evaluation consequences

- When assessing **identity providers, compute, storage, registrars, payment mechanisms, agents and account ecosystems**, consider self-service registration, lifecycle control, recovery, transfer, provider lock-in, recurring operating cost and continued operation without founder intervention **as explicit research dimensions**.
- Do not reject a useful provider solely because it requires a lawful human bootstrap. State the constraint, possible delegated operation and whether that dependency can later be removed.
- Keep **research evidence**, **integration authorization**, **financial authorization** and **legal ownership** separate. No laboratory experiment grants operational permissions by itself.
- The research repository remains separate from the running TinyFund/Miss Lea instance. This principle authorizes **no migrations, credential transfers, paid executions or external registrations**.

This principle informs future research and design choices; concrete selection thresholds, tests and stopping rules must still follow the [evaluation policy](evaluation-policy.md).
