# File guide / 文件说明

## Start here / 阅读顺序

Codex Lens lives in `subprojects/relay_auditor/` as the monitor's future detector module. Its own [public-source staging and native package workflow](../subprojects/relay_auditor/docs/RELEASING.md) prepares a reviewable standalone candidate. The [v2 extension contract](../subprojects/relay_auditor/docs/EXTENDING.md#integration-contract--token监视器接入) defines anonymous assessment and usage inputs for later integration. Its generated `.relay-data/` and exported snapshots are private and ignored. See the [detector file guide](../subprojects/relay_auditor/FILE_GUIDE.md).

Read the [English README](../README/README.md) or [中文说明](../README/README-Simplified_Chinese.md), then the data-source and maintenance documents when needed.

| Path | Purpose / 作用 | Publish? / 是否提交 |
| --- | --- | --- |
| `README.md` | GitHub 首页语言导航 | Yes |
| `README/README.md` | Full English project documentation | Yes |
| `README/README-Simplified_Chinese.md` | 完整简体中文说明 | Yes |
| `VERSION` | Single authoritative project version / 版本唯一来源 | Yes |
| `LICENSE` | MIT open-source license / MIT 开源许可证 | Yes |
| `CHANGELOG.md` | User-visible changes by version / 版本变更 | Yes |
| `WORKLOG.md` | Dated progress, checks and outstanding tasks / 工作记录 | Yes |
| `AGENTS.md` | Repository instructions for future coding assistants / 助手维护约定 | Yes |
| `CONTRIBUTING.md`, `SECURITY.md` | Contribution and security-reporting guidance | Yes |
| `docs/DATA_SOURCES.md` | 数据来源、统计口径与核对方法 | Yes |
| `docs/VERIFICATION.md` | 实际验证结果及未完成的验收 | Yes |
| `docs/MAINTENANCE.md` | 代码、说明、工作记录、版本的同步规则 | Yes |
| `docs/RELEASING.md` | Release preparation checklist / 发布清单 | Yes |
| `.github/` | Issue and pull-request templates / 问题与PR模板 | Yes |
| `.gitignore` | Excludes generated/private/local files | Yes |
| `.gitattributes`, `.editorconfig` | Text encodings, indentation and line endings | Yes |
| `查看Codex用量.cmd` | Windows one-click launcher / 双击入口 | Yes |
| `run.py` | CLI options, safety setup and collection entry point | Yes |
| `codex_usage/__init__.py` | Python package marker | Yes |
| `codex_usage/safety.py` | Local-path checks, network and write guards | Yes |
| `codex_usage/metadata.py` | Allowlisted auth/config/model/version extraction | Yes |
| `codex_usage/official.py` | Optional isolated official app-server usage/limits adapter; no raw credential export | Yes |
| `docs/OFFICIAL_SYNC.md` | Official synchronization contract, privacy boundaries and limitations | Yes |
| `tests/test_official.py` | Synthetic official protocol, privacy, accounting and process-guard tests | Yes |
| `codex_usage/sessions.py` | JSONL parsing, deduplication, turn and subagent accounting | Yes |
| `codex_usage/database.py` | Read a temporary SQLite copy, including WAL/SHM | Yes |
| `codex_usage/report.py` | Aggregate data, generate HTML and CSP hashes | Yes |
| `codex_usage/privacy.py` | Output allowlist, local viewing guides and report-local aliases before HTML/JSON/CSV | Yes |
| `codex_usage/dashboard.html` | Offline dashboard template, CSS and JavaScript | Yes |
| `tests/test_*.py` | Synthetic parser, database, report and privacy tests | Yes |
| `tests/test_dashboard.cjs` | Frontend logic tests with a synthetic DOM | Yes |
| `tests/make_demo.py` | Builds a synthetic demo, without real account data | Yes |
| `.reports/` | Private generated report, optional JSON and temporary DB copies | **No** |
| `.qa/` | Local scratch checks and generated synthetic previews | **No** |
| `__pycache__/`, `.venv/` | Local caches/environment | **No** |
| `.git/` | Git's own local repository metadata | Managed by Git; never upload as an archive |

## Data flow / 数据流程

```text
Launcher / CLI
  -> validate paths and install offline/read-only guard
  -> metadata + JSONL logs + temporary database copy
  -> optional isolated official account usage/limits reads (explicit --sync-official)
  -> deduplicated direct totals and separately labeled inclusive totals
  -> privacy output allowlist + report-local aliases + local viewing guides
  -> sanitized report data + HTML template + restrictive CSP
  -> .reports/latest.html
  -> local browser (no server)
```

Official account summaries/daily buckets are a separate report field, never added to local direct totals. Temporary `.official-*` runtime directories live under the report output and are removed after synchronization. The installed native client is a separate trust boundary; the Python audit hook does not sandbox it.

Raw metadata is used only in local memory for attribution and aggregation. Both public report-writing paths apply `privacy.py` before serialization; CSV uses only the sanitized embedded data. Alias maps are not written. `AGENTS.md` governs Codex's modification scope; `SECURITY.md` defines the foremost product confidentiality requirement.

The user's `.codex` data is external input, never part of this repository. A cloned repository should contain source, documentation and synthetic tests only. The `VERSION` file describes this project, not Codex, the model or an account plan.

## Interactive report additions

- `codex_usage/exports.py`: DOCX/XLSX/PDF/PNG/JPEG/WebP/SVG exports after privacy filtering.
- `codex_usage/server.py`: loopback-only routes, fixed guarded collection workers and complete-batch publication.
- `codex_usage/live.js`: same-origin refresh and reload, only injected into live responses.
- `启动交互报告.cmd`: chooses local export runtime and starts the service.
- `docs/INTERACTIVE_REPORTS.md`: use, dependencies, format scopes and security.
- `tests/test_exports.py`, `tests/test_server.py`: synthetic export and local-origin/refresh regression checks.
- `.reports/snapshot-*/`: private generated batches, never committed.

## Desktop distribution / 桌面分发

- `desktop.py`: standalone app/worker entry; default double-click opens the local report.
- `codex_usage/updates.py`: strict stable-version comparison, bounded public GitHub check and update consent.
- `codex_usage/runtime.py`: per-user output locations and fixed source/frozen worker commands.
- `requirements-build.txt`: pinned direct build/export dependencies.
- `build_tools/build.py`, `monitor.spec`: native bundles and Windows/macOS/Linux packaging, pinned build-time font source.
- `build_tools/windows.iss`, `sign-windows.ps1`: current-user installer and optional verified Authenticode signing.
- `build_tools/smoke.py`, `release_manifest.py`: standalone synthetic export and complete asset/checksum verification.
- `.github/workflows/release.yml`: native tests/builds, artifacts, and tag-triggered complete Releases.
- `tests/test_updates.py`: update consent/version/failure/network-boundary and runtime command checks.
- `tests/test_bundle_resources.py`: internal packaged resource reads, rejected external links/writes and unchanged source-path link checks.
- `docs/INSTALLATION.md`, `WINDOWS_TRUST.md`, `RELEASE_NOTES.md`: install/update/signing and release notes.
- `docs/DELIVERY_REPORT.md`: delivery progress, implementation map, validation evidence, release procedure and development handoff.
- `build/`, `dist/`, `release/`, generated `codex_usage/assets/ReportSansSC.ttf`: ignored build outputs, not private source inputs.

User launch → separate public version check/consent → loopback service → fixed worker with update checks disabled → unchanged guarded collection/privacy exports. Installed output goes to a separate validated per-user directory; source output stays `.reports/`.

Relay Auditor's separate Windows desktop entry is `subprojects/relay_auditor/desktop.py`; its `relay_auditor/desktop.py`, `desktop_actions.py` and `runtime.py` own the local window/native actions/data directory. Its own `build_tools/relay.spec`, `build.py`, `smoke.py`, pinned requirements and `WINDOWS.md` produce an ignored, unsigned Windows portable bundle with a fixed worker. These files do not modify or participate in the parent monitor's desktop/release workflow.

`subprojects/relay_auditor/relay_auditor/models.py` validates model lists/private user names; the subproject controller/server expose UI options separately from anonymous export. Local desktop builds use fresh ignored candidate folders and write `dist/latest-desktop.cmd` only after successful smoke; the source desktop launcher follows it without interrupting an older process.

Relay Auditor's product core is `core.py` (desktop/CLI/SDK owner), `suites.py`/`quality.py` (versioned procedural tasks), `reports.py`/`exporting.py` (v2 evidence/history/offline HTML), `planning.py` (preflight/support states), `profiles.py`/`vault.py` (private settings/exact owned OS credentials), `adapters.py` (native Anthropic/Gemini), `calibration.py`/`calibration_cli.py` (frozen source studies), and `demo.py`/`prompts.py` (offline demonstration/non-echo input). `__main__.py` is the module entry. Its `docs/METHODS.md`, `EXTENDING.md`, `DEVELOPMENT_PLAN.md` document evidence, contributions and open gates. `.github/workflows/relay-auditor.yml` defines separate synthetic-only CI without model keys or publication. The subproject file guide describes schema-v2 integration; parent guarded collection remains unchanged.

`subprojects/relay_auditor/relay_auditor/official.py` owns fixed official provider/region presets, exact-model matching and protocol compatibility. Local profiles persist monotonic target aliases, and deletion uses the profile UUID to remove settings and its owned credential slot while preserving the aggregate store.

`subprojects/relay_auditor/relay_auditor/assessment.py` runs the versioned initial screen and also drives the primary calibration study. `tests/test_assessment_review.py` checks the independently budgeted review and its binding to the original run.

`families.py` chooses experimental tasks from the declared family. `assessment.py` runs one-button assessment, exact official pairing, aggregate diagnostics and per-task evidence. `reports.py` supplies the plain-language summary to the live card and HTML export.
