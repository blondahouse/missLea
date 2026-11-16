# Miss Lea — Architecture Atlas

Public-facing, synthetic-safe **architectural atlas**, not a monitor of production resources.

- **Source**: `site/index.html`, `site/style.css`, `site/app.mjs`, `site/data.mjs`.
- **Data basis**: public `missLea` laboratory README/evidence files and sanitized results of the private `misslea-operator` OIDC isolation canary. No actual secret values, recovery details, access tokens or personal account credentials are included.
- **Status semantics**: **Проверено реально** only denotes narrowly scoped actual-provider trial evidence, not overall production readiness; **Код + CI** means source/test present but no live deploy; **Лаборатория** means controlled synthetic/mock validation; **Исследовано** means candidate only; **Запланировано** means not implemented.
- **Maintenance**: edit node status and source references in `site/data.mjs` when a lab changes. New external providers are represented as candidates until there is real evidence. Do not mark the Cloudflare-only Agent Lab as live until two actual Cloudflare alarms, two model calls and persisted state were observed with free-quota receipts.
- **Source of truth**: lab documentation remains authoritative. This site is a dated public snapshot, not an automatically refreshed operational inventory.
- **Hosting**: GitHub Pages for public `blondahouse/missLea`; `.github/workflows/architecture-atlas.yml` validates JS modules and publishes a standalone no-build artifact. GitHub Pages must be enabled once in repository Settings → Pages → Source = GitHub Actions (if not already).
- **No sensitive permissions**: the workflow only checks committed static files then uses GitHub's pages deploy token. It does **not** read Infisical, Gmail, Cloudflare or any workflow Environment secret.
- **Local usage**: static source uses ES modules, so serve `site/` through a local HTTP server. Opening `index.html` directly from `file://` may fail module loading. No external JS libraries or backend are required. Google Fonts in CSS is optional; system fallbacks work offline.
