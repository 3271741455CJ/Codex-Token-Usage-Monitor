# Changelog / 版本变更

User-visible changes are recorded here. `VERSION` is the version source of truth.
Versions use `MAJOR.MINOR.PATCH`; tags use `vMAJOR.MINOR.PATCH`. A heading is not proof of publication.

## Unreleased / 待发布变更

- Adopted the MIT License for public distribution.

- Added whole-snapshot DOCX/PDF reports, XLSX records and PNG/JPEG/WebP/SVG overview exports alongside filtered CSV.
- Added a loopback-only interactive launcher and in-page full-batch refresh; failed generations retain the previous snapshot. Export libraries must already be installed locally; no automatic downloads.

- Made confidentiality the foremost product constraint in `SECURITY.md`; separately documented Codex's explicit-scope/minimal-change rule in `AGENTS.md` and contributor instructions. Networking is permitted for required report data under that confidentiality boundary; only necessary credentials/account ID may be used for OpenAI official authentication.
- Removed sensitive originals and credential fragments from HTML/embedded JSON, JSON exports, CSV and CLI output. Identity/private configuration now have local viewing guides; sessions, turns, projects and sources use report-local anonymous references without a saved mapping. Usage accounting and the official synchronization protocol are unchanged.
- Compatibility change: exports no longer contain original identity/title/path/ID fields; `--show-api-key` now prints only a local viewing guide. Existing copies saved elsewhere are not automatically rewritten. Version remains 0.1.0, unreleased.
- Added opt-in `--sync-official` through the installed Windows official Codex app-server, with isolated in-memory authentication, no credential refresh, allowlisted account summaries/daily buckets/limits, and explicit failure states.
- Added a separate official account dashboard with daily visualization and quota bars. Official totals never add to local totals or change with local filters; missing remote details remain unavailable.
- Default operation and generated HTML remain offline. This feature is unreleased; live website parity is not established.

## 0.1.0 — Initial baseline / 初始版本（尚未发布）

Baseline documented on 2026-10-29. The initial local implementation was verified on 2026-10-26. No release date or GitHub tag has been created.

### Added / 新增

- Offline, read-only collection and a Windows one-click launcher.
- Account/configuration metadata, local version information and cached model capabilities.
- Response deduplication and legacy cumulative-token accounting; per-project/session/turn breakdowns and subagent rollups.
- Historical limits, source paths and line numbers, coverage warnings and database-only records.
- Standalone Chinese dashboard with filters, pagination and CSV export.
- Network/write guards, credential redaction, temporary SQLite copies and restrictive HTML CSP.
- Synthetic-data tests and bilingual project documentation, file guide and maintenance rules.

### Known limitations / 已知限制

- Local records cannot supply complete cloud billing, live quotas or missing logs.
- Session creator identity is not proof of every request's billing identity.
- Automatic visual acceptance remains outstanding; other operating systems have not been validated.
- One Windows symlink test was skipped for insufficient privileges in the recorded validation.
- License selection and GitHub publication remain pending.
