# Security and privacy / 安全与隐私

## 首要原则：敏感信息严格保密 / Highest priority: confidentiality

This is the foremost **product constraint**. Sensitive originals must remain local: read them only for the required local processing, never publish, upload, log, copy into reports or expose in terminal/error output. Reports must provide a local viewing guide instead of the original value, including in hidden HTML, embedded JSON, attributes and CSV exports. No plaintext, masked suffix or reversible encoding is an acceptable substitute.

敏感原文只在本地按需读取；报告只提供本地查看指引，用户自行查看原文件，不显式显示敏感原文或其片段。具体包括：

- **凭据 / Credentials：** 密码、API Key、access/refresh/ID token、JWT、Cookie、认证请求头、秘密环境变量值、系统凭据库内容。
- **身份 / Identity：** 姓名、邮箱、账号/用户/组织标识，以及私人订阅、付款与账单身份信息。
- **私人配置与位置 / Private configuration and locations：** 服务商 URL、私人接口地址、配置档/提供商/环境变量名称、完整配置、计算机名/用户名、绝对文件路径、项目/工作目录与安装位置。
- **原始内容与标识 / Original content and identifiers：** 对话/提示词正文、私人代码、工具参数与输出、会话/项目标题及原始 ID、原始日志、数据库记录和服务端原始响应。

Local usage numbers, model identifiers, reasoning levels, timestamps, version numbers, quota windows and credit amounts may be shown for the requested analysis. Session, turn, project, account-pool and source relationships use report-local ordinal aliases; no original-to-alias map is saved. These statistics are still private local output and must not be uploaded or treated as safe for public sharing. New output fields require explicit privacy review before allowlisting.

**Credential transmission exception for the existing token-monitor collector, explicitly authorized by the owner:** the necessary access token and account identifier may be supplied to the installed official Codex client solely for **OpenAI official authentication** in opt-in sync. They must never go to another destination, search query, telemetry service, report, error message or command-line argument. Refresh tokens are not used. See [official synchronization](docs/OFFICIAL_SYNC.md) for the checked execution boundary.

联网不再被一概禁止：可以按报告需要获取信息，但任何请求、查询参数或上传内容都不得携带上述敏感信息，主采集器的唯一凭据例外是用户已授权的 OpenAI 官方认证；独立中转检测子项目另见下述显式启用边界。本地采集保持离线，并提供可选官方同步。用户于 2026-11-01 另行要求每次启动检查更新：启动器仅向固定的 `api.github.com/repos/3271741455CJ/Codex-Token-Usage-Monitor/releases/latest` 请求公开元数据，不读取或发送凭据、Codex 数据、Cookie、私人配置或路径，不继承代理。最多等待四秒，可用 `--no-update-check` 禁用；后台采集不检查版本。只有确认后才打开本仓库的 HTTPS 发布页，不自动执行下载内容。静态 HTML 保持离线；用户授权的本机交互页面仅访问同源更新接口。

Codex's separate “modify only explicitly requested scope” rule belongs to [AGENTS.md](AGENTS.md) and [maintenance instructions](docs/MAINTENANCE.md); it is not a product runtime constraint.

## Scope

### Separate opt-in relay-auditor subproject (2026-11-02)

The owner requested implementation of the approved [Relay Auditor plan](agent.md). This narrowly authorizes the separate subproject, after the user configures a target and explicitly starts/enables detection, to send a dedicated relay API key and generated synthetic probes only to that selected HTTPS relay. The official-reference form pins its independently supplied key to the selected fixed OpenAI, Anthropic, Google, DeepSeek, Qwen, GLM, Kimi, MiniMax, xAI or Mistral API and region. Saving may send the key to that preset for model metadata; generated tasks require explicit detection. A different provider or region requires fresh input. The app never reads or reuses ChatGPT login tokens. The existing collector's sole official-authentication credential exception, offline guard and account synchronization remain unchanged.

Provider discovery is explicit and read-only: supported CC Switch/Codex++ configuration is processed locally; only dedicated relay key slots are used, never official login token fields. Foreign SQLite is opened only on temporary copies in private output, including WAL/SHM; copies are removed after reading. No source migration, provider switch, configured command/hook or login renewal is executed. Original provider IDs/names remain in memory and are omitted from reports, database history, notifications, error text and exports. Under the subsequently approved product plan, selected target names/addresses/settings persist only in the tool's dedicated private settings file; keys default to memory and may explicitly be stored only in an exact tool-owned Windows vault item. This is not permission to persist keys in JSON or read other applications' vault entries.

On 2026-11-03 the owner requested one-click provider import, selectable models, custom test names and reasoning controls. Clicking auto-import reads only the known manager configuration location (CC Switch's fixed home directory, Codex++'s fixed home directory or explicit CODEX_PLUS_STATE_DIR); other locations require manual selection, with no recursive search. User-requested model-list refresh sends only the dedicated relay Key to the configured HTTPS model-list route, with the same no-proxy/no-redirect/size limits; it sends no business data or login token and is not a completion/token-budget event. Model IDs are bounded/validated, and supplier-reported availability is not authenticity evidence. User-entered test names may persist in private settings but never in anonymous evidence or exports; original supplier names remain private. Anonymous browser export explicitly removes UI-only maps. Import alone defaults off; the separate “import and screen” action explicitly starts one budgeted screening job.

The official-reference panel uses fixed metadata routes when available and otherwise checks a versioned model list locally. Manual DeepSeek direct assessment uses the key explicitly supplied for that target and has separate probe accounting. Existing saved reference keys with a known origin stay pinned when target protocol settings change. A legacy reference whose destination cannot be established requires fresh input. Automatic pairs require the same model and compatible settings. Reports retain bounded reason codes and counts. Target deletion removes only the matching private profile and its owned credential item. Aggregate reports and usage remain available by target ID.

The approved quality-product plan adds a dedicated `private/settings.json` separate from anonymous `audit.sqlite`, and optional exact UUID-owned `RelayAuditor/v1/` Windows Credential Manager items. Keys reside only in memory or in their exact owned vault item. Import offers explicit opt-in to the same vault item. A restored locked target accepts a freshly pasted key on Start. The app reads manager configuration through the explicit import action. Restart leaves periodic and queued work off. All calls, including reference failures, retain shared persistent budgets. Queue cancellation cannot retract in-flight requests. Generated responses are data for local grading. Ordinary tasks store only synthetic seeds, versions, aggregate counts and statistics. Standalone HTML/JSON exports omit private names, endpoints, credentials and business text, and remain private aggregate data. Calibration collection is a separate explicit command requiring independent official keys and budgets. A statistical candidate requires further review.

Only aggregate allowlisted results, numeric features and budgets persist in ignored private output. No original business conversations/code/logs/reports or raw model responses are uploaded or serialized. The loopback UI uses strict Host/Origin, a random session path and same-origin assets. Detection defaults off and can be disabled or rescheduled without affecting usage collection. Usage attribution requires request evidence: current login/configuration or provider metadata rewritten by another app cannot prove historical origin. This source prototype has not been calibrated on real models and does not certify model identity.

The requested Windows desktop wrapper keeps that same loopback boundary inside WebView2. Native file/folder actions require the same Origin/header/session checks, never return selected paths, and write exports only into the private per-user output directory with exclusive creation. No arbitrary filesystem JS bridge is exposed. The packaged offline reader is a fixed sibling executable, hidden when spawned, with the original offline guard; closing stops its process and future observation. Desktop data is separate from the executable and source prototype history. WebView2 gets a private temporary profile, disabled password/autofill/debug/download features and local-session-only page navigation/resource handlers; best-effort cleanup cannot guarantee cache removal after crashes, and the system WebView2 component is not an OS network sandbox. Build dependencies may be installed only on the developer's builder; the portable app never installs or downloads dependencies. No tray process, startup registration, updater or official-login credential access is added.

The collector is designed for local, read-only source inspection, offline by default. The owner explicitly authorized optional official account synchronization; see [its execution and credential boundary](docs/OFFICIAL_SYNC.md). It uses application-level network/write restrictions and restrictive HTML CSP. These protections are not an OS sandbox or a firewall for other apps. See the READMEs and `codex_usage/safety.py` for the boundary.

No release-support schedule is established yet. Version 0.2.0 adds standalone distribution; do not infer security guarantees for future versions from this document.

## Reporting a vulnerability

Do not post credentials, real logs, reports, account identifiers or exploit details in a public issue. Share a synthetic reproduction, the project version, environment and affected code path through a private channel agreed with the repository owner. Once a GitHub repository exists, use its private vulnerability-reporting feature **only if the owner has enabled it**. No reporting address or private endpoint has been configured by this project yet.

If no private channel is available, ask the owner to provide one without disclosing sensitive details publicly. For ordinary non-sensitive bugs, use the bug-report template.

## Safe sharing

- Never commit `auth.json`, Codex `config.toml`, `.env` files, session JSONL, SQLite databases/sidecars, generated reports or CSV exports.
- `.gitignore` prevents ordinary addition of matching untracked files; it does not remove files already tracked or clean earlier Git history.
- Use synthetic data for tests and screenshots. Avoid including real usernames, email addresses or project paths. `--show-api-key` now prints only a local viewing guide, never a key or its suffix.
- If a secret has already been published, stop sharing it, revoke/rotate it through the relevant provider, and review affected Git history. Deleting the current file alone does not remove earlier copies.

## Future changes

Any change to authentication handling, file writes, SQLite access, output fields or browser resource loading requires appropriate regression checks and synchronized security/accounting documentation. Do not enable upload or cloud CI with private data as a convenience feature. `--sync-official` sends only the authentication required by the official client and reads account usage; it must never send local logs or reports. It uses ephemeral credentials, an isolated home, checked effective configuration, fixed error statuses and no inherited proxy/API-key environment. Native-client traffic is outside the Python audit hook; do not claim this is an OS sandbox or an absolute guarantee against compromised clients.

## Authorized local report service

The owner requested in-page refresh and multi-format exports on 2026-10-30. This authorizes a loopback-only service and fixed collector subprocesses; it does not authorize private uploads. See [the service boundary](docs/INTERACTIVE_REPORTS.md). Static reports retain network-disabled CSP. Live responses allow only same-origin refresh, require a random session path, exact Host and POST Origin/header checks, and never log request URLs or raw errors. All new document/image formats share the privacy output filter.

## Build and distribution boundary

The requested release workflow runs on clean GitHub-hosted builders with public source and synthetic fixtures only. Build-time dependency and pinned font-source downloads are separate from installed runtime behavior. No local reports, credentials, configuration, logs or databases are uploaded. Windows signing credentials, when configured, stay in runner secrets and temporary files removed after signing. Desktop bundles write reports to validated per-user data directories. See [installation](docs/INSTALLATION.md) and [Windows trust](docs/WINDOWS_TRUST.md).

Frozen macOS apps use PyInstaller's internal Frameworks/Resources links for templates and libraries. The audit hook permits only read-only opens whose original and resolved paths both remain inside the running executable's bundle. Links escaping that bundle and all bundle writes remain blocked. Explicit source/data/output path checks still reject symlinks, including links inside the app when presented as user input. This exception is for packaged runtime resources, not Codex source data.
