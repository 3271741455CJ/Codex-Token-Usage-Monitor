# Changelog / 版本变更

User-visible changes are recorded here. `VERSION` is the version source of truth.
Versions use `MAJOR.MINOR.PATCH`; tags use `vMAJOR.MINOR.PATCH`. A heading is not proof of publication.

## Unreleased / 待发布变更

## 0.2.0 — Desktop distribution / 桌面分发

Publication is evidenced by the matching GitHub Release, not this heading.

- Added bounded startup checks against public stable GitHub Releases, update consent, `--no-update-check` and `--version`; local refresh workers never prompt.
- Added native standalone Windows installer/portable ZIP, macOS Intel/Apple Silicon DMGs and Linux x64/ARM64 DEB/tar.gz, bundled Python/export dependencies and an OFL Chinese font.
- Added per-user installed output, frozen worker dispatch and default-browser launch across desktop platforms.
- Supported macOS packaged resource links with a read-only executable-bundle boundary; source path and write restrictions remain in force.
- Added clean native CI, standalone and Windows install/uninstall checks, complete-release publication and SHA-256 inventories.
- Added optional verified Windows code signing and timestamps, non-elevated installation, version metadata and unpacked/no-UPX bundles; unsigned/new apps may still warn. macOS builds are not notarized.
- Compatibility: startup now makes a public version request unless disabled; guarded collection and saved HTML remain offline. Optional official sync remains Windows-specific.


- Adopted the MIT License for public distribution.

- Added whole-snapshot DOCX/PDF reports, XLSX records and PNG/JPEG/WebP/SVG overview exports alongside filtered CSV.
- Added a loopback-only interactive launcher and in-page full-batch refresh; failed generations retain the previous snapshot. Export libraries must already be installed locally; no automatic downloads.

- Made confidentiality the foremost product constraint in `SECURITY.md`; separately documented Codex's explicit-scope/minimal-change rule in `AGENTS.md` and contributor instructions. Networking is permitted for required report data under that confidentiality boundary; only necessary credentials/account ID may be used for OpenAI official authentication.
- Removed sensitive originals and credential fragments from HTML/embedded JSON, JSON exports, CSV and CLI output. Identity/private configuration now have local viewing guides; sessions, turns, projects and sources use report-local anonymous references without a saved mapping. Usage accounting and the official synchronization protocol are unchanged.
- Compatibility change: exports no longer contain original identity/title/path/ID fields; `--show-api-key` now prints only a local viewing guide. Existing copies saved elsewhere are not automatically rewritten.
- Added opt-in `--sync-official` through the installed Windows official Codex app-server, with isolated in-memory authentication, no credential refresh, allowlisted account summaries/daily buckets/limits, and explicit failure states.
- Added a separate official account dashboard with daily visualization and quota bars. Official totals never add to local totals or change with local filters; missing remote details remain unavailable.
- Guarded collection and saved HTML remain offline. Live website parity is not established.

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
