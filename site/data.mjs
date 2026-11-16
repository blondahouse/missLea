export const metadata={
  "version": "1.0",
  "asOf": "2026-11-16",
  "description": "Observed source and provider evidence, not a live-system dashboard. All architecture data is public-safe.",
  "repo": "blondahouse/missLea",
  "operator": "blondahouse/misslea-operator"
};
export const categories=[
  {
    "id": "control",
    "title": "IDENTITY & CONTROL",
    "subtitle": "Кто имеет полномочия и управляет аккаунтами",
    "tone": "#c6a3ff"
  },
  {
    "id": "runtime",
    "title": "AGENT RUNTIME",
    "subtitle": "Минимальная автономная жизнь Miss Lea",
    "tone": "#79c9ff"
  },
  {
    "id": "compute",
    "title": "INTELLIGENCE & COMPUTE",
    "subtitle": "Модели и заменяемая вычислительная мощность",
    "tone": "#eebd80"
  },
  {
    "id": "storage",
    "title": "STORAGE & CONTINUITY",
    "subtitle": "Память, резервирование, восстановление",
    "tone": "#78d8b0"
  }
];
export const statuses=[
  {
    "id": "verified",
    "title": "Проверено реально",
    "short": "Live verified",
    "color": "#72dab8"
  },
  {
    "id": "code",
    "title": "Код + CI",
    "short": "Code / CI",
    "color": "#83bdfd"
  },
  {
    "id": "lab",
    "title": "Лаборатория",
    "short": "Offline lab",
    "color": "#e9bc75"
  },
  {
    "id": "research",
    "title": "Исследовано",
    "short": "Research",
    "color": "#bbaff9"
  },
  {
    "id": "planned",
    "title": "Запланировано",
    "short": "Planned",
    "color": "#8991a6"
  }
];
export const nodes=[
  {
    "id": "founder",
    "stage": "control",
    "title": "Делегирование управления",
    "provider": "Олег → доверенный оператор",
    "owner": "policy",
    "status": "verified",
    "subtitle": "Полномочия на этапе разработки",
    "detail": "Олег — текущий владелец и делегирующий субъект. ChatGPT действует как оператор по явным поручениям. Для дальнейшего самостоятельного агента нужен проверенный механизм передачи полномочий, а не просто перенос памяти.",
    "tags": [
      "Полномочия",
      "Recovery"
    ],
    "source": "https://github.com/blondahouse/missLea/blob/main/docs/digital-independence.md"
  },
  {
    "id": "git-private",
    "stage": "control",
    "title": "Operator Repository",
    "provider": "GitHub • private",
    "owner": "external",
    "status": "verified",
    "subtitle": "blondahouse/misslea-operator",
    "detail": "Приватный репозиторий существует и доступен оператору. GitHub Actions уже выполнял автоматические OIDC-проверки Infisical. Он пока не является проверенным исполнителем реальных Cloudflare-административных действий.",
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
    "subtitle": "misslea-root • prod",
    "detail": "Корневой проект и машинная идентичность misslea-root-operator созданы. Подтверждено чтение синтетического ROOT_ACCESS_CANARY через GitHub OIDC. Настоящие мастер-ключи пока не внесены.",
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
    "subtitle": "misslea-operations • prod",
    "detail": "Второй проект и машинная идентичность misslea-ops-operator. Живой тест подтвердил: Operations не входит в Root-проект и получает HTTP 403 при чтении его canary.",
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
    "title": "Machine Identity / OIDC",
    "provider": "GitHub ↔ Infisical",
    "owner": "hybrid",
    "status": "verified",
    "subtitle": "Без статических Client Secrets",
    "detail": "Официальный Infisical GitHub Action реально обменял короткоживущий GitHub OIDC JWT на полномочия Root и Operations. Диагностические workflows с корневым доступом после теста удалены.",
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
    "title": "Account Provisioning",
    "provider": "Cloudflare API + own adapter",
    "owner": "hybrid",
    "status": "code",
    "subtitle": "Создание Workers и выпуск токенов",
    "detail": "В публичной исследовательской лаборатории есть Python-прототип работы с Infisical и Cloudflare API. Реальный управляющий канал не подключён, мастер-токен Cloudflare не проверен.",
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
    "title": "Почта и новые аккаунты",
    "provider": "Gmail • отдельный аккаунт",
    "owner": "external",
    "status": "planned",
    "subtitle": "Identity / Recovery / регистрация",
    "detail": "Отдельная почта Miss Lea существует. Работа через доверенный операторский контур и OAuth именно этого аккаунта ещё не подключена; использование личной почты владельца не планируется.",
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
    "title": "Реестр полномочий",
    "provider": "Own • Identity Lab / SQLite",
    "owner": "internal",
    "status": "lab",
    "subtitle": "Учёт владельца, грантов и восстановления",
    "detail": "Реализован синтетический реестр ресурсов, сроков, отзывов и полномочий. Пока нет реальной авторизации внешнего клиента, управления соглашениями или активного credential broker.",
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
    "subtitle": "Команды вместо выдачи ключей",
    "detail": "Предполагаемый доверенный посредник: принимает допустимую операцию, временно разрешает секрет в защищённой среде, обращается к API и отдаёт результат без ключа. Не развёрнут и не протестирован с настоящими мастер-ключами.",
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
    "status": "code",
    "subtitle": "HTTP entrypoint / start / health",
    "detail": "Исходники отдельного анонимного лабораторного Worker собраны в CI; не развёрнуты как полноценный новый агент в Cloudflare. 10 ms CPU Free — ключевой риск, проверяется только реальным запуском.",
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
    "status": "code",
    "subtitle": "Агентная сессия и цикл",
    "detail": "Синтетический AnonymousFreeAgent на Agents SDK делает выбор разрешённого действия, сохраняет результат и готовит повторное пробуждение. Работоспособность в облаке не подтверждена.",
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
    "title": "Сон / пробуждение",
    "provider": "Durable Objects Alarms",
    "owner": "external",
    "status": "code",
    "subtitle": "Self-wake без постоянной VM",
    "detail": "В коде лаборатории предусмотрены два пробуждения с интервалом и повторный запуск по расписанию. Настоящие Cloudflare Alarms ещё не проходили end-to-end.",
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
    "title": "Оперативное состояние",
    "provider": "SQLite-backed Durable Objects",
    "owner": "external",
    "status": "code",
    "subtitle": "История, события, next wake",
    "detail": "Данные синтетической агентной сессии сохраняются в состоянии Durable Object. Живое сохранение в облаке и восстановление после сна пока не подтверждены.",
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
    "title": "Инструменты агента",
    "provider": "Own • allowlist",
    "owner": "internal",
    "status": "code",
    "subtitle": "Ограниченный безопасный action",
    "detail": "В лаборатории разрешено только вычисление квадратов чисел 2,3,5. Это тест решения и выполнения инструмента, а не свободный программный или административный доступ.",
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
    "title": "Общение / входящие",
    "provider": "Telegram Bot API",
    "owner": "external",
    "status": "planned",
    "subtitle": "Новый агент: канал ещё не подключён",
    "detail": "Telegram используется старым TinyFund, но в новом репозитории Miss Lea новый автономный коммуникационный контур ещё не развёрнут. Не переносить статус старого бота на новую систему.",
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
    "title": "Бюджет / бесплатные квоты",
    "provider": "Own • policy gate",
    "owner": "internal",
    "status": "planned",
    "subtitle": "Никаких неявных платных fallback",
    "detail": "Цель: запуск на Free, остановка при исчерпании квоты, учёт нейронов/CPU/внешних запросов. В лабораторном коде платные интеграции отсутствуют, но автономный бюджетный контроллер ещё не реализован.",
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
    "title": "Здоровье / мониторинг",
    "provider": "Cloudflare Metrics + own receipts",
    "owner": "hybrid",
    "status": "planned",
    "subtitle": "Heartbeat, errors, quota, alerts",
    "detail": "Реальный мониторинг нового агента, тайминги пробуждений, журнал отказов, метрики ресурсоёмкости и независимый watchdog запланированы. Публичные /health лаборатории — не production-мониторинг.",
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
    "title": "Первичная LLM",
    "provider": "Cloudflare Workers AI • Gemma 4",
    "owner": "external",
    "status": "code",
    "subtitle": "Два вызова модели в лаборатории",
    "detail": "Исходники вызывают модель @cf/google/gemma-4-26b-a4b-it: первый выбирает инструмент, второй сверяет сохранённый результат. Фактические вызовы модели на Cloudflare ещё не проверены.",
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
    "title": "Мультимодельный Router",
    "provider": "Bifrost / GoModel / LiteLLM / Portkey",
    "owner": "hybrid",
    "status": "lab",
    "subtitle": "4 провайдера сравнивались на mock upstream",
    "detail": "Реальные Docker-бинарники проверены на синтетических upstream. Bifrost выбран ADR для первоначальной Demo-интеграции, но self-hosted маршрутизатор не развёрнут и может быть отложен ради Cloudflare-only старта. У протестированного Portkey есть блокирующий SSRF.",
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
    "title": "Long-term Memory",
    "provider": "Own • SQLite baseline",
    "owner": "internal",
    "status": "lab",
    "subtitle": "Источники, решения, retrieval",
    "detail": "Работает базовый поиск по SQLite на синтетических сценариях, без семантической памяти. Извлечение опыта, сжатие, обновление фактов и проверка понимания первоисточников остаются открытыми задачами.",
    "tags": [
      "SQLite",
      "Retrieval",
      "Consolidation"
    ],
    "source": "https://github.com/blondahouse/missLea/tree/main/labs/memory"
  },
  {
    "id": "edge",
    "stage": "compute",
    "title": "Edge Functions",
    "provider": "Cloudflare Workers / Supabase",
    "owner": "external",
    "status": "code",
    "subtitle": "Короткие запросы, API и dispatcher",
    "detail": "Cloudflare Worker реализован в коде; существуют и отдельные ручные synthetic Security Lab испытания. Supabase adapter для гибридного вычисления написан, но не развёрнут. Основной старт — Cloudflare.",
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
    "title": "Scale-to-zero Services",
    "provider": "Google Cloud Run / Azure Container Apps",
    "owner": "external",
    "status": "research",
    "subtitle": "Контейнерные HTTP-сессии",
    "detail": "Кандидаты для более тяжёлого Agent Engine и длительных HTTP-вызовов. Не подключены и не нужны для первого Cloudflare-only старта, если Worker укладывается в Free.",
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
    "subtitle": "Длительные задачи без HTTP",
    "detail": "Реализован исследовательский CLI для синтетической Cloud Run Job (создать → вычислить → получить logs → удалить), но live-испытание и расходы не подтверждены. Не обязательны на старте.",
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
    "title": "Ephemeral Sandboxes",
    "provider": "E2B / Modal",
    "owner": "external",
    "status": "research",
    "subtitle": "Изоляция выполнения кода",
    "detail": "Есть код экспериментального E2B-пробника, но подтверждённого живого развертывания нет. Позже пригодится для программирования, анализа и установки пакетов.",
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
    "title": "Временные / постоянные VM",
    "provider": "Oracle Always Free / Google Compute Engine",
    "owner": "external",
    "status": "research",
    "subtitle": "Полный Linux-хост как резерв",
    "detail": "Не требуется для первого облачного запуска. Возможность будущего размещения инструментов, локальной LLM или долгих демонов; бесплатность и доступность ресурсов отдельно проверяются.",
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
    "title": "Гибридный Sleep Lab",
    "provider": "Cloudflare → Supabase / Deno",
    "owner": "hybrid",
    "status": "code",
    "subtitle": "Альтернативный внешний исполнитель",
    "detail": "Схема Cloudflare Durable Object Alarm → внешняя HTTP-функция реализована и проходит офлайн-тесты. Реальное двухоблачное пробуждение не проверено. Deno Deploy — только временный совместимый вариант.",
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
    "title": "Consistent Snapshots",
    "provider": "Own • SQLite backup API",
    "owner": "internal",
    "status": "lab",
    "subtitle": "Хэш, quarantine, inactive restore",
    "detail": "Синтетические консистентные снимки SQLite, контроль повреждения, восстановление в карантин реализованы и проверены офлайн. Это не production-шифрование или живой data pipeline.",
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
    "title": "Шифрование / Backup Engine",
    "provider": "restic + real CLI tests",
    "owner": "hybrid",
    "status": "verified",
    "subtitle": "Единый синтетический архив",
    "detail": "Реальный restic использовался в GitHub Actions: один зашифрованный синтетический снимок создан и восстановлен. Тестовый пароль публичен, поэтому это НЕ защита настоящей памяти.",
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
    "title": "Replica A • B2",
    "provider": "Backblaze B2",
    "owner": "external",
    "status": "verified",
    "subtitle": "Реальная внешняя копия",
    "detail": "STO-006: одинаковый архив загружен в настоящий B2; отдельный runner без Google-доступа сверил SHA-256, проверил restic и восстановил синтетические данные.",
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
    "title": "Replica B • Drive",
    "provider": "Google Drive • Miss Lea",
    "owner": "external",
    "status": "verified",
    "subtitle": "Второй независимый провайдер",
    "detail": "STO-006: тот же архив загружен в Google Drive через drive.file; отдельный runner без ключа B2 восстановил байт-в-байт. Реальная долговременная политика хранения не доказана.",
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
    "title": "Recovery / Fencing",
    "provider": "Own • inactive restore",
    "owner": "internal",
    "status": "verified",
    "subtitle": "Восстановить, но не оживить копию",
    "detail": "В STO-006 оба отдельных чистых runner успешно восстановили идентичные записи и вложение в неактивном карантине. Не проверены реальная потеря GitHub, WORM и отзыв старых полномочий при восстановлении.",
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
    "title": "Независимый Recovery Key",
    "provider": "Root Vault + external escrow",
    "owner": "hybrid",
    "status": "planned",
    "subtitle": "Доступ после потери провайдера",
    "detail": "Нужно независимо сохранять ключи расшифровки и способы восстановления Root Vault, не замыкая цепочку на Gmail/Infisical/GitHub. Для реальных данных не выполнено.",
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
    "title": "KV / Objects",
    "provider": "Cloudflare Workers KV / R2",
    "owner": "external",
    "status": "research",
    "subtitle": "Нефундаментальное хранилище",
    "detail": "Cloudflare KV не отвергнут: возможен для конфигурации, справочников, кэша, архивов. Для согласованного агентного состояния первым кандидатом выбран SQLite Durable Objects.",
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
    "title": "Portability & Handoff",
    "provider": "Own • architecture principles",
    "owner": "internal",
    "status": "planned",
    "subtitle": "Данные ≠ разрешение действовать",
    "detail": "Нужны миграция памяти, первоисточники, перенос полномочий и проверка единственного активного экземпляра. Архитектурный принцип принят; сквозного live-теста переезда нет.",
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
    "label": "делегирует"
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
    "label": "исполняет"
  },
  {
    "from": "infisical-root",
    "to": "admin-api",
    "label": "аварийные права"
  },
  {
    "from": "infisical-ops",
    "to": "admin-api",
    "label": "рабочие токены"
  },
  {
    "from": "admin-api",
    "to": "worker",
    "label": "деплой / create"
  },
  {
    "from": "email",
    "to": "registry",
    "label": "идентичность"
  },
  {
    "from": "registry",
    "to": "broker",
    "label": "handles"
  },
  {
    "from": "broker",
    "to": "admin-api",
    "label": "операции"
  },
  {
    "from": "worker",
    "to": "agent-sdk",
    "label": "запускает"
  },
  {
    "from": "agent-sdk",
    "to": "alarms",
    "label": "следующий wake"
  },
  {
    "from": "alarms",
    "to": "agent-sdk",
    "label": "пробуждает"
  },
  {
    "from": "agent-sdk",
    "to": "state",
    "label": "читает / пишет"
  },
  {
    "from": "agent-sdk",
    "to": "workers-ai",
    "label": "LLM запрос"
  },
  {
    "from": "workers-ai",
    "to": "agent-sdk",
    "label": "решение"
  },
  {
    "from": "agent-sdk",
    "to": "tools",
    "label": "действие"
  },
  {
    "from": "tools",
    "to": "state",
    "label": "событие"
  },
  {
    "from": "telegram",
    "to": "worker",
    "label": "webhook • план"
  },
  {
    "from": "agent-sdk",
    "to": "quota",
    "label": "расходы"
  },
  {
    "from": "worker",
    "to": "observability",
    "label": "метрики"
  },
  {
    "from": "agent-sdk",
    "to": "memory",
    "label": "retrieval • план"
  },
  {
    "from": "memory",
    "to": "snapshot",
    "label": "snapshot • план"
  },
  {
    "from": "state",
    "to": "snapshot",
    "label": "snapshot • план"
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
    "label": "заменяемый backend"
  },
  {
    "from": "agent-sdk",
    "to": "edge",
    "label": "исполняется"
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
