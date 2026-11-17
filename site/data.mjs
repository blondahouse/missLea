export const metadata={
  "version": "1.0",
  "asOf": "2026-11-17",
  "description": "Observed source and provider evidence, not a live-system dashboard. All architecture data is public-safe.",
  "repo": "blondahouse/missLea",
  "operator": "blondahouse/misslea-operator"
};

export const categories=[
  {
    "id": "control",
    "title": "IDENTITY & CONTROL",
    "subtitle": "Who is authorized to control dedicated accounts",
    "tone": "#c6a3ff"
  },
  {
    "id": "runtime",
    "title": "AGENT RUNTIME",
    "subtitle": "Minimal independent agent lifecycle",
    "tone": "#79c9ff"
  },
  {
    "id": "compute",
    "title": "INTELLIGENCE & COMPUTE",
    "subtitle": "Models and replaceable compute resources",
    "tone": "#eebd80"
  },
  {
    "id": "storage",
    "title": "STORAGE & CONTINUITY",
    "subtitle": "External evidence, state and recovery experiments",
    "tone": "#78d8b0"
  }
];

export const statuses=[
  {
    "id": "verified",
    "title": "Live verified",
    "short": "Live verified",
    "color": "#72dab8"
  },
  {
    "id": "code",
    "title": "Code / CI",
    "short": "Code / CI",
    "color": "#83bdfd"
  },
  {
    "id": "lab",
    "title": "Synthetic lab",
    "short": "Offline lab",
    "color": "#e9bc75"
  },
  {
    "id": "research",
    "title": "Research",
    "short": "Research",
    "color": "#bbaff9"
  },
  {
    "id": "planned",
    "title": "Planned",
    "short": "Planned",
    "color": "#8991a6"
  }
];

export const nodes=[
  {
    "id": "founder",
    "stage": "control",
    "title": "Delegated control",
    "provider": "Founder → trusted operator",
    "owner": "policy",
    "status": "planned",
    "subtitle": "Current stewardship during development",
    "detail": "The founder currently authorizes actions. ChatGPT acts as a trusted operator under explicit instructions. A future independent Miss Lea needs independently verified authority transfer; memory migration alone grants no permissions.",
    "tags": [
      "Authority",
      "Recovery"
    ],
    "source": "https://github.com/blondahouse/missLea/blob/main/docs/digital-independence.md"
  },
  {
    "id": "git-private",
    "stage": "control",
    "title": "Operator repository",
    "provider": "GitHub • private",
    "owner": "external",
    "status": "verified",
    "subtitle": "Private trusted automation",
    "detail": "The private operator repository exists and has performed authenticated Infisical OIDC checks. It is a privileged operational control surface, not an agent's unrestricted executor.",
    "tags": [
      "GitHub Actions",
      "OIDC",
      "CI"
    ],
    "source": "https://github.com/blondahouse/misslea-operator"
  },
  {
    "id": "infisical-root",
    "stage": "control",
    "title": "Root Vault",
    "provider": "Infisical Cloud EU",
    "owner": "external",
    "status": "verified",
    "subtitle": "Recovery authority and root credentials",
    "detail": "The root project and machine identity exist. Synthetic canary retrieval via GitHub OIDC was verified. Root authority is separated from routine operational privileges.",
    "tags": [
      "Org Admin",
      "Emergency",
      "Infisical"
    ],
    "source": "https://github.com/blondahouse/misslea-operator/blob/main/docs/INFISICAL.md"
  },
  {
    "id": "infisical-ops",
    "stage": "control",
    "title": "Operational Vault",
    "provider": "Infisical Cloud EU",
    "owner": "external",
    "status": "verified",
    "subtitle": "Scoped, revocable daily permissions",
    "detail": "A second Infisical project and machine identity were verified; Operations received HTTP 403 when attempting to read the Root project canary.",
    "tags": [
      "Member",
      "Limited tokens",
      "Denied 403"
    ],
    "source": "https://github.com/blondahouse/misslea-operator/blob/main/docs/INFISICAL.md"
  },
  {
    "id": "oidc",
    "stage": "control",
    "title": "Machine identity / OIDC",
    "provider": "GitHub ↔ Infisical",
    "owner": "hybrid",
    "status": "verified",
    "subtitle": "Short-lived workload authentication",
    "detail": "The official Infisical GitHub Action exchanged GitHub OIDC identity for short-lived credentials in verified tests. Temporary root-access diagnostics were subsequently removed.",
    "tags": [
      "JWT",
      "Audience",
      "Subject",
      "TTL 300s"
    ],
    "source": "https://github.com/blondahouse/misslea-operator/actions/runs/43935642999"
  },
  {
    "id": "admin-api",
    "stage": "control",
    "title": "Account provisioning",
    "provider": "Cloudflare API + own adapter",
    "owner": "hybrid",
    "status": "code",
    "subtitle": "Cloudflare API management adapter",
    "detail": "The public Operator Control Lab contains a synthetic Cloudflare/Infisical administration prototype. Integration and live privileges must be separately verified.",
    "tags": [
      "Workers Admin",
      "Account Tokens",
      "Provision"
    ],
    "source": "https://github.com/blondahouse/missLea/tree/main/labs/operator_control"
  },
  {
    "id": "email",
    "stage": "control",
    "title": "Dedicated email and accounts",
    "provider": "Gmail • dedicated account",
    "owner": "external",
    "status": "planned",
    "subtitle": "Separate agent identity and recovery",
    "detail": "Miss Lea has a dedicated email account. Trusted operator access through this account's OAuth and recovery workflow is a separate capability; do not use the founder's personal mailbox.",
    "tags": [
      "Google OAuth",
      "Gmail API",
      "Registration"
    ],
    "source": "https://github.com/blondahouse/missLea/blob/main/docs/digital-independence.md"
  },
  {
    "id": "registry",
    "stage": "control",
    "title": "Authority registry",
    "provider": "Own • Identity Lab / SQLite",
    "owner": "internal",
    "status": "lab",
    "subtitle": "Account holders, grants and recovery",
    "detail": "A synthetic registry models ownership, grants, expiration and revocation. Live provider authorization and contractual decisions are not implemented by the fixture.",
    "tags": [
      "SQLite",
      "Grants",
      "Audit"
    ],
    "source": "https://github.com/blondahouse/missLea/tree/main/labs/identity"
  },
  {
    "id": "broker",
    "stage": "control",
    "title": "Credential Broker",
    "provider": "Own • planned",
    "owner": "internal",
    "status": "planned",
    "subtitle": "Allowed actions without exposing keys",
    "detail": "Proposed trusted intermediary resolves dedicated secrets only inside protected execution and returns operation results without exposing credentials to the agent model.",
    "tags": [
      "Privileged ops",
      "Auditing",
      "Provider APIs"
    ],
    "source": "https://github.com/blondahouse/missLea/tree/main/labs/operator_control"
  },
  {
    "id": "worker",
    "stage": "runtime",
    "title": "Cloudflare Worker",
    "provider": "Cloudflare Workers Free",
    "owner": "external",
    "status": "verified",
    "subtitle": "Worker entry points and health",
    "detail": "A bounded synthetic Cloudflare Agent Lab was deployed on 17 Nov 2026 and completed two native wake cycles. This is not a production personal agent or proof of ongoing free-plan headroom.",
    "tags": [
      "HTTP",
      "Free",
      "10ms CPU"
    ],
    "source": "https://github.com/blondahouse/missLea/tree/main/labs/cloudflare_agent"
  },
  {
    "id": "agent-sdk",
    "stage": "runtime",
    "title": "Agent Engine",
    "provider": "Cloudflare Agents SDK • own logic",
    "owner": "hybrid",
    "status": "verified",
    "subtitle": "Agent session and control loop",
    "detail": "A live bounded synthetic trial used Cloudflare Agents SDK with allowed action selection, durable state and two scheduled wakes. It does not validate a full autonomous Miss Lea.",
    "tags": [
      "Agent",
      "Session",
      "Tools"
    ],
    "source": "https://github.com/blondahouse/missLea/tree/main/labs/cloudflare_agent/src"
  },
  {
    "id": "alarms",
    "stage": "runtime",
    "title": "Sleep / wake scheduler",
    "provider": "Durable Objects Alarms",
    "owner": "external",
    "status": "verified",
    "subtitle": "Native scheduled agent activation",
    "detail": "The synthetic agent completed two native Cloudflare scheduled wakes without a local computer or GitHub runner driving the wake cycle.",
    "tags": [
      "Schedule",
      "Wake",
      "Sleep"
    ],
    "source": "https://github.com/blondahouse/missLea/tree/main/labs/cloudflare_agent"
  },
  {
    "id": "state",
    "stage": "runtime",
    "title": "Operational state",
    "provider": "SQLite-backed Durable Objects",
    "owner": "external",
    "status": "verified",
    "subtitle": "Durable Object SQLite session state",
    "detail": "The synthetic run persisted an earlier tool result and read it after a scheduled wake. Operational state is separate from the proposed autobiographical D1 Living Memory.",
    "tags": [
      "SQLite",
      "Events",
      "Single writer"
    ],
    "source": "https://github.com/blondahouse/missLea/blob/main/labs/cloudflare_agent/README.md"
  },
  {
    "id": "tools",
    "stage": "runtime",
    "title": "Bounded tools",
    "provider": "Own • allowlist",
    "owner": "internal",
    "status": "verified",
    "subtitle": "Deterministic synthetic action",
    "detail": "The trial allowed a fixed squares-calculation action and verified result 38. This does not grant arbitrary external API, code execution or administrator capabilities.",
    "tags": [
      "SQUARES",
      "Allowlist",
      "38"
    ],
    "source": "https://github.com/blondahouse/missLea/tree/main/labs/cloudflare_agent/src"
  },
  {
    "id": "telegram",
    "stage": "runtime",
    "title": "Communication",
    "provider": "Telegram Bot API",
    "owner": "external",
    "status": "planned",
    "subtitle": "New agent messaging channel",
    "detail": "The older TinyFund instance used Telegram, but this new Cloudflare agent runtime has not yet demonstrated its own full messaging loop. Do not reuse old-bot status as new-agent evidence.",
    "tags": [
      "Messages",
      "Webhook",
      "Initiative"
    ],
    "source": "https://github.com/blondahouse/missLea/blob/main/docs/architecture-principles.md"
  },
  {
    "id": "quota",
    "stage": "runtime",
    "title": "Budget and free-tier limits",
    "provider": "Own • policy gate",
    "owner": "internal",
    "status": "planned",
    "subtitle": "No implicit paid fallback",
    "detail": "Aims to halt at quota exhaustion and track CPU, model and request usage. A complete per-agent resource controller and verified ongoing no-cost operation are not yet demonstrated.",
    "tags": [
      "Zero spend",
      "Stop",
      "Metering"
    ],
    "source": "https://github.com/blondahouse/missLea/blob/main/labs/cloudflare_agent/README.md"
  },
  {
    "id": "observability",
    "stage": "runtime",
    "title": "Health and monitoring",
    "provider": "Cloudflare metrics + own receipts",
    "owner": "hybrid",
    "status": "planned",
    "subtitle": "Receipts, errors, limits and watchdog",
    "detail": "Operational monitoring, wake timing, error records, budget reporting and independent recovery signals remain to be developed. A lab health endpoint is not production observability.",
    "tags": [
      "Receipt",
      "Errors",
      "Health"
    ],
    "source": "https://github.com/blondahouse/missLea/blob/main/labs/cloudflare_agent/README.md"
  },
  {
    "id": "workers-ai",
    "stage": "compute",
    "title": "Initial LLM",
    "provider": "Cloudflare Workers AI • Gemma 4",
    "owner": "external",
    "status": "verified",
    "subtitle": "Two verified bounded inference calls",
    "detail": "The Cloudflare synthetic agent used the configured Workers AI model for an action decision and later result verification. Ongoing usage/billing headroom is still unverified.",
    "tags": [
      "Inference",
      "Gemma",
      "Neurons"
    ],
    "source": "https://github.com/blondahouse/missLea/blob/main/labs/cloudflare_agent/README.md"
  },
  {
    "id": "llm-router",
    "stage": "compute",
    "title": "Multi-model router",
    "provider": "Bifrost / GoModel / LiteLLM / Portkey",
    "owner": "hybrid",
    "status": "lab",
    "subtitle": "Candidate selection tested on mock upstream",
    "detail": "Bifrost, GoModel, LiteLLM and Portkey were compared under isolated mocks. A Bifrost research decision exists but is not a requirement for Cloudflare-only launch; tested Portkey had a blocking SSRF issue.",
    "tags": [
      "Bifrost",
      "Fallback",
      "Free models"
    ],
    "source": "https://github.com/blondahouse/missLea/blob/main/docs/router-decision-record.md"
  },
  {
    "id": "memory",
    "stage": "compute",
    "title": "Unified Living Memory",
    "provider": "Own • SQLite baseline",
    "owner": "internal",
    "status": "lab",
    "subtitle": "Adopted concept; native baseline planned",
    "detail": "Personal memory is one mutable record space with contextual recall, weights, optional sparse links, lazy decay and eviction on actual pressure. Only synthetic SQLite lexical retrieval is implemented. The Cloudflare-first roadmap starts with D1 and FTS5, not a heavy framework.",
    "tags": [
      "SQLite",
      "Retrieval",
      "Consolidation"
    ],
    "source": "https://github.com/blondahouse/missLea/blob/main/docs/memory-concept.md"
  },
  {
    "id": "edge",
    "stage": "compute",
    "title": "Edge Functions",
    "provider": "Cloudflare Workers / Supabase",
    "owner": "external",
    "status": "code",
    "subtitle": "Light HTTP requests and dispatch",
    "detail": "Cloudflare Worker source exists and bounded deployment was verified in a separate agent lab. A Supabase hybrid adapter remains experimental and is not required for the Cloudflare-only initial path.",
    "tags": [
      "HTTP",
      "Edge",
      "Serverless"
    ],
    "source": "https://github.com/blondahouse/missLea/tree/main/labs/agent_sleep"
  },
  {
    "id": "services",
    "stage": "compute",
    "title": "Scale-to-zero services",
    "provider": "Google Cloud Run / Azure Container Apps",
    "owner": "external",
    "status": "research",
    "subtitle": "Container HTTP execution candidates",
    "detail": "Google Cloud Run and Azure Container Apps remain potential alternatives for heavier tasks. They are neither required nor deployed for the first Cloudflare-only agent.",
    "tags": [
      "HTTP",
      "Container",
      "Scale-to-zero"
    ],
    "source": "https://github.com/blondahouse/missLea/tree/main/labs/compute"
  },
  {
    "id": "jobs",
    "stage": "compute",
    "title": "Jobs",
    "provider": "Google Cloud Run Jobs",
    "owner": "external",
    "status": "research",
    "subtitle": "Deferred non-HTTP workloads",
    "detail": "A synthetic Cloud Run Job probe was written. Live execution costs have not been proven, and a job service is not needed to establish native Cloudflare memory.",
    "tags": [
      "Batch",
      "Container",
      "Logging"
    ],
    "source": "https://github.com/blondahouse/missLea/blob/main/labs/compute/README.md"
  },
  {
    "id": "sandbox",
    "stage": "compute",
    "title": "Ephemeral sandboxes",
    "provider": "E2B / Modal",
    "owner": "external",
    "status": "research",
    "subtitle": "Future isolated code execution",
    "detail": "An E2B trial adapter exists, but no verified production sandbox is enabled for Miss Lea. Future use may help development or heavy computation.",
    "tags": [
      "Ephemeral",
      "Code exec",
      "Cleanup"
    ],
    "source": "https://github.com/blondahouse/missLea/blob/main/labs/compute/README.md"
  },
  {
    "id": "vm",
    "stage": "compute",
    "title": "Optional virtual machines",
    "provider": "Oracle Always Free / Google Compute Engine",
    "owner": "external",
    "status": "research",
    "subtitle": "Full Linux as a future fallback",
    "detail": "Long-running hosts and local models may be considered later. Their free availability and operating cost need separate validation.",
    "tags": [
      "Linux",
      "ARM",
      "Fallback"
    ],
    "source": "https://github.com/blondahouse/missLea/blob/main/labs/compute/README.md"
  },
  {
    "id": "hybrid",
    "stage": "compute",
    "title": "Hybrid Sleep Lab",
    "provider": "Cloudflare → Supabase / Deno",
    "owner": "hybrid",
    "status": "code",
    "subtitle": "Optional external wake executor",
    "detail": "A Cloudflare alarm to external HTTP function was tested offline. It remains an alternative, not a dependency of the Cloudflare-only launch.",
    "tags": [
      "Alarm",
      "External compute",
      "Fallback"
    ],
    "source": "https://github.com/blondahouse/missLea/tree/main/labs/agent_sleep"
  },
  {
    "id": "snapshot",
    "stage": "storage",
    "title": "Consistent snapshot experiment",
    "provider": "Own • SQLite backup API",
    "owner": "internal",
    "status": "lab",
    "subtitle": "Synthetic archive integrity and quarantine",
    "detail": "Storage Lab verified coherent SQLite snapshots, corruption detection and inactive recovery on synthetic fixtures. This is historical engineering evidence, not a required personality-backup policy.",
    "tags": [
      "SQLite backup",
      "SHA-256",
      "Quarantine"
    ],
    "source": "https://github.com/blondahouse/missLea/blob/main/labs/storage/README.md"
  },
  {
    "id": "restic",
    "stage": "storage",
    "title": "Encrypted backup experiment",
    "provider": "restic + real CLI tests",
    "owner": "hybrid",
    "status": "verified",
    "subtitle": "Independent historical backup-engine research",
    "detail": "The actual restic binary was exercised in isolated GitHub Actions with synthetic archives and integrity verification. This is not a deployed autobackup of Miss Lea's personal recollections.",
    "tags": [
      "restic",
      "Archive",
      "Integrity"
    ],
    "source": "https://github.com/blondahouse/missLea/blob/main/labs/storage/sto006-dual-provider-results-2026-11-16.md"
  },
  {
    "id": "b2",
    "stage": "storage",
    "title": "Replica A — B2 (synthetic trial)",
    "provider": "Backblaze B2",
    "owner": "external",
    "status": "verified",
    "subtitle": "Real external object-store test",
    "detail": "STO-006 uploaded synthetic encrypted archive bytes to real Backblaze B2. An isolated runner verified the hash and restored source fixtures without Drive access.",
    "tags": [
      "S3 API",
      "Remote replica",
      "STO-006"
    ],
    "source": "https://github.com/blondahouse/missLea/blob/main/labs/storage/sto006-dual-provider-results-2026-11-16.md"
  },
  {
    "id": "drive",
    "stage": "storage",
    "title": "Replica B — Drive (synthetic trial)",
    "provider": "Google Drive • Miss Lea",
    "owner": "external",
    "status": "verified",
    "subtitle": "Independent test-only recovery",
    "detail": "STO-006 uploaded matching synthetic archive bytes into the dedicated Google Drive. A separate runner recovered exact data without B2 access.",
    "tags": [
      "drive.file",
      "OAuth",
      "STO-006"
    ],
    "source": "https://github.com/blondahouse/missLea/blob/main/labs/storage/sto006-dual-provider-results-2026-11-16.md"
  },
  {
    "id": "restore",
    "stage": "storage",
    "title": "Recovery and fencing lab",
    "provider": "Own • inactive restore",
    "owner": "internal",
    "status": "verified",
    "subtitle": "Inactive isolated restore verified",
    "detail": "STO-006 restored test artifacts independently from both providers into inactive quarantine. This does not implement a convergent mirror of currently evolving Living Memory.",
    "tags": [
      "Integrity",
      "Quarantine",
      "No authority"
    ],
    "source": "https://github.com/blondahouse/missLea/blob/main/labs/storage/sto006-dual-provider-results-2026-11-16.md"
  },
  {
    "id": "keyrecovery",
    "stage": "storage",
    "title": "Independent recovery authority",
    "provider": "Root Vault + external escrow",
    "owner": "hybrid",
    "status": "planned",
    "subtitle": "Protected keys outside the systems they unlock",
    "detail": "Recovery requires keys and authority records independent of the data provider. Verified live key escrow, provider outage recovery and current-state identity fencing remain future work.",
    "tags": [
      "Escrow",
      "Unseal",
      "Failover"
    ],
    "source": "https://github.com/blondahouse/missLea/blob/main/docs/architecture-principles.md"
  },
  {
    "id": "kv",
    "stage": "storage",
    "title": "KV and objects",
    "provider": "Cloudflare Workers KV / R2",
    "owner": "external",
    "status": "research",
    "subtitle": "Optional cache and document storage",
    "detail": "Cloudflare KV or R2 may support caches, public reference content or a separate Document Vault. D1 is the current proposed native personal-memory baseline; KV's eventual consistency is unsuitable for an authoritative mutation log.",
    "tags": [
      "KV",
      "Eventual consistency",
      "R2"
    ],
    "source": "https://github.com/blondahouse/missLea/blob/main/labs/cloudflare_agent/README.md"
  },
  {
    "id": "portability",
    "stage": "storage",
    "title": "Portability and handoff",
    "provider": "Own • architecture principles",
    "owner": "internal",
    "status": "planned",
    "subtitle": "Data is not authority",
    "detail": "The portable artifact is the current surviving Living Memory, separate external obligations and current operational authority. A former or archived copy does not authorize a second active instance or restore forgotten history.",
    "tags": [
      "G5",
      "Identity",
      "Restore"
    ],
    "source": "https://github.com/blondahouse/missLea/blob/main/docs/digital-independence.md"
  }
];

export const edges=[
  {
    "from": "founder",
    "to": "git-private",
    "label": "delegates"
  },
  {
    "from": "git-private",
    "to": "oidc",
    "label": "short-lived JWT"
  },
  {
    "from": "oidc",
    "to": "infisical-root",
    "label": "auth"
  },
  {
    "from": "oidc",
    "to": "infisical-ops",
    "label": "auth"
  },
  {
    "from": "git-private",
    "to": "admin-api",
    "label": "executes"
  },
  {
    "from": "infisical-root",
    "to": "admin-api",
    "label": "root recovery rights"
  },
  {
    "from": "infisical-ops",
    "to": "admin-api",
    "label": "operational tokens"
  },
  {
    "from": "admin-api",
    "to": "worker",
    "label": "provisions"
  },
  {
    "from": "email",
    "to": "registry",
    "label": "identity"
  },
  {
    "from": "registry",
    "to": "broker",
    "label": "handles"
  },
  {
    "from": "broker",
    "to": "admin-api",
    "label": "authorized operations"
  },
  {
    "from": "worker",
    "to": "agent-sdk",
    "label": "starts"
  },
  {
    "from": "agent-sdk",
    "to": "alarms",
    "label": "schedules next wake"
  },
  {
    "from": "alarms",
    "to": "agent-sdk",
    "label": "wakes"
  },
  {
    "from": "agent-sdk",
    "to": "state",
    "label": "reads / writes"
  },
  {
    "from": "agent-sdk",
    "to": "workers-ai",
    "label": "LLM request"
  },
  {
    "from": "workers-ai",
    "to": "agent-sdk",
    "label": "decision"
  },
  {
    "from": "agent-sdk",
    "to": "tools",
    "label": "action"
  },
  {
    "from": "tools",
    "to": "state",
    "label": "event"
  },
  {
    "from": "telegram",
    "to": "worker",
    "label": "planned webhook"
  },
  {
    "from": "agent-sdk",
    "to": "quota",
    "label": "budget controls"
  },
  {
    "from": "worker",
    "to": "observability",
    "label": "metrics"
  },
  {
    "from": "agent-sdk",
    "to": "memory",
    "label": "planned recall"
  },
  {
    "from": "state",
    "to": "snapshot",
    "label": "historical trial only"
  },
  {
    "from": "snapshot",
    "to": "restic",
    "label": "archive"
  },
  {
    "from": "restic",
    "to": "b2",
    "label": "upload"
  },
  {
    "from": "restic",
    "to": "drive",
    "label": "upload"
  },
  {
    "from": "b2",
    "to": "restore",
    "label": "isolated restore"
  },
  {
    "from": "drive",
    "to": "restore",
    "label": "isolated restore"
  },
  {
    "from": "keyrecovery",
    "to": "restore",
    "label": "decrypt"
  },
  {
    "from": "restore",
    "to": "portability",
    "label": "inactive handoff"
  },
  {
    "from": "workers-ai",
    "to": "llm-router",
    "label": "replaceable backend"
  },
  {
    "from": "agent-sdk",
    "to": "edge",
    "label": "runs on"
  },
  {
    "from": "agent-sdk",
    "to": "services",
    "label": "fallback • research"
  },
  {
    "from": "agent-sdk",
    "to": "jobs",
    "label": "offload • research"
  },
  {
    "from": "agent-sdk",
    "to": "sandbox",
    "label": "offload • research"
  },
  {
    "from": "agent-sdk",
    "to": "vm",
    "label": "fallback • research"
  },
  {
    "from": "alarms",
    "to": "hybrid",
    "label": "alternative"
  },
  {
    "from": "hybrid",
    "to": "services",
    "label": "remote executor"
  },
  {
    "from": "kv",
    "to": "state",
    "label": "secondary cache"
  },
  {
    "from": "portability",
    "to": "registry",
    "label": "grants after restore"
  }
];
