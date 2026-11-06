# Changelog / 版本变更

User-visible changes are recorded here. `VERSION` is the version source of truth.
Versions use `MAJOR.MINOR.PATCH`; tags use `vMAJOR.MINOR.PATCH`. A heading is not proof of publication.

## Unreleased / 待发布变更

- Prepared Codex Lens module release candidates with a cross-platform native build matrix, app icon, public-source archive and mathematical principles document. Added separate anonymous v2 assessment and usage routes for future Token Usage Monitor integration.

- Relay Auditor desktop adds a light detection workbench with a target picker, a compact model toolbar and side-by-side official scores. The report separates the observed gap from its evidence limits and keeps detailed statistics available on demand. Fixed the summary using official counts in place of relay counts.

- Relay Auditor fixes restarting imported targets: import offers opt-in Windows vault storage, and a pasted relay key can unlock and start an existing target from one click. The versioned assessment separates correct, incorrect and unscorable responses and offers an opt-in fresh paired review with a request preview. Calibration studies run the desktop assessment engine.

- Relay Auditor adds a separate official-reference form with 16 presets across 10 providers, exact-model matching and one-click paired assessment. Target cards can be deleted with their app-owned keys while retaining history and usage.

- Relay Auditor desktop now offers one-button assessment with a request preview, plain-language verdict, per-task official comparison and expandable evidence. Added declared-family test selection, experimental DeepSeek Chat, fixed DeepSeek references, separate direct API usage and explicit response failure reasons. Estimate failures can be retried in place.

- Relay Auditor now shares a Python engine across desktop/CLI/SDK, with reproducible procedural quality/context/reasoning tasks, schema-v2 four-dimensional experimental evidence, same-condition history, queues/cancellation/progress, budget/cost preflight and anonymous offline HTML reports. Added private target settings, opt-in owned Windows vault items and disabled/locked restart behavior; custom names remain excluded from evidence/exports.
- Added experimental native Anthropic/Gemini text/stream adapters, a support matrix separating connection/evaluation/reference/calibration, an offline synthetic demo, frozen controlled-study tooling and source/synthetic CI plus bilingual contribution/method docs. No real calibration, verified-model claims, parent runtime integration or public release is implied.

- Relay Auditor: fixed native import-dialog filters and visible error feedback; added known-location CC Switch/Codex++ import, explicit import-and-screen, model dropdowns from configuration/relay listing, private custom test names and per-target reasoning controls. Changed model/effort invalidates the live result and pauses periodic detection; anonymous history and budgets persist.

- Added an independent Windows x64 desktop window and local unsigned portable build for Relay Auditor, with native configuration/folder selection, private-data exports, optional taskbar reminders and a bundled fixed offline worker. Detection remains opt-in; no parent integration or release publication.

- Added the independent experimental Relay Auditor subproject: disabled-by-default relay probes, adjustable intervals, budgets, local UI/CLI, optional official API reference, read-only CC Switch/Codex++ provider discovery and request-evidence accounting contracts. Official login is never model-tested; the released monitor/runtime remains unmodified. Real model calibration and historical request-ledger attribution are pending.

## 0.2.0 — Desktop distribution / 桌面分发

Published on 2026-11-02: [v0.2.0](https://github.com/3271741455CJ/Codex-Token-Usage-Monitor/releases/tag/v0.2.0).

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
