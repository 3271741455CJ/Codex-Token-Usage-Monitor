# Codex Usage Check

[English](README.md) | [简体中文](README-Simplified_Chinese.md)

**Version 0.1.0 — initial implementation, not yet released on GitHub.**

Inspect locally stored Codex usage in a single offline dashboard. The collector reads configuration, cached login metadata, session logs and a copy of the session index, then generates a standalone HTML report. By default it does not call account APIs. Explicit `--sync-official` uses the installed official client to read account usage and limits; it never uploads local logs.

This independent project is not affiliated with or endorsed by OpenAI. The dashboard interface is currently Simplified Chinese; these READMEs are bilingual documentation, not a UI language switch.

## Features

| View | What it shows |
| --- | --- |
| Account and configuration | Local viewing guides for identity/credentials/private configuration; default model and reasoning effort |
| Versions and models | Installed Windows desktop package version, model-cache client version, observed CLI versions and cached model capabilities |
| Usage | Input, cached input, output, reasoning output and total tokens by date, project, session, turn, model and reasoning effort |
| Official account (optional) | Account Token summary, daily chart and quota windows through the official client; separate from local totals |
| Subagents | Direct usage and separately labeled inclusive totals for verified parent/child relationships |
| Limits | Locally recorded window percentages, reset timestamps, credit fields and historical snapshots |
| Provenance | Anonymous source references, local viewing guides and event line numbers, scan warnings and database-only records with missing logs |
| Exploration | Filters, sorting, pagination, drilldowns and local CSV export |

## Requirements

- Windows is the primary supported and tested environment. The launcher and installed-app version detection are Windows-specific; other platforms have not been validated.
- Python **3.11+**, installed locally. Recorded validation used Python 3.12 and 3.15 on Windows.
- A modern local browser and existing Codex local data.
- Node.js is needed only for frontend development tests; no npm packages are required.

Static collection uses the standard library. Interactive export uses locally available document libraries and a loopback-only service; there is no CDN, telemetry, automatic updater or dependency download.

## Quick start

1. Keep the project files together in a local folder.
2. Double-click **`查看Codex用量.cmd`**.
3. The launcher generates a complete batch under **`.reports/snapshot-*/`** and opens its loopback-only interactive page.
4. Keep the launcher window open and click “更新数据” to regenerate all files. A saved standalone HTML remains a static snapshot.

Run these commands from the project root in PowerShell:

```powershell
python -I -S -B .\run.py
python -I -S -B .\run.py --codex-home 'D:\LocalCodexData' --output 'D:\LocalReports'
python -I -S -B .\run.py --json
```

Data directory precedence: `--codex-home`, then `CODEX_HOME`, then `%USERPROFILE%\.codex`. The default output is `.reports/` beside `run.py`. Its parent directory must exist. Output and protected data/install directories must not contain one another. UNC paths, mapped network drives, symlinks and Windows reparse points are rejected.

| Option | Purpose |
| --- | --- |
| `--codex-home PATH` | Read another local Codex data directory |
| `--output PATH` | Write into a separate local output directory |
| `--sync-official` | Opt in to official account usage/limits synchronization; Windows Store Codex and readable ChatGPT file login required |
| `--json` | Also create `usage.json` with the same privacy filtering as HTML; still for local use only |
| `--show-api-key` | Print a local viewing guide only; no longer prints a key or any fragment |
| `--help` | Show command help |

To collect without opening a browser, run `run.py` directly or use `查看Codex用量.cmd --no-open`. The latter is a launcher option, not a Python option.

## Accounting boundaries

**Local token totals are not the official account bill.** Deleted/unsynced logs, other devices and records never written locally are outside coverage. A session's creator account does not establish the billing identity of every subsequent request.

Modern `token_usage_record` entries are deduplicated by response ID; legacy `token_count` snapshots are processed as increments. The two streams and SQLite `tokens_used` are not added together. Cached input and reasoning output are subsets of input and output. Inclusive subagent totals are explanatory values, not additional consumption to add again.

Five-hour and weekly limits are window percentages, not fixed token quotas. Cached model context windows are not account quotas. Offline operation cannot retrieve live Settings → Usage & Billing, invoices, current API balance/costs or unrecorded per-model allowances. Missing information stays unknown; expired snapshots are labeled.

System credential stores, authentication commands, remote hosts and WSL-internal files are not automatically queried. Config defaults may be overridden by project or turn settings; historical turn metadata is used where available.

## Privacy and read-only design

- Sources are read-only. SQLite connects only to a temporary copy of the database and WAL/SHM; temporary copies are removed after use.
- A Python audit hook blocks socket/DNS/HTTP activity, arbitrary subprocesses and writes outside the report directory. Official sync permits exactly one preconfigured official stdio child; the native child is a separate trust boundary. Reparse points and writes through multiply linked files are rejected.
- The standalone HTML has a restrictive CSP, hash-authorized scripts and no remote assets or network connections.
- Confidentiality is the foremost [product rule](../SECURITY.md). Credentials and fragments, identities, private URLs/configuration, original session/project titles and IDs, paths, conversations and tool/log contents are excluded from HTML (including embedded data), JSON, CSV and terminal output. Reports provide local viewing guides instead.
- Sessions, turns, projects and sources use report-local anonymous numbers; no original-value map is saved. Usage/model/time/quota statistics remain available but private. Keep reports, CSV exports and real logs out of GitHub, issues and screenshots.

Networking is permitted as needed for report data under the confidentiality rule. The current implementation keeps default offline mode and optional official sync; it adds no general crawler. The owner explicitly permits the necessary access token and account ID solely for OpenAI official authentication, never other destinations or report display.

To inspect sensitive originals, open the Codex data directory you selected (by default `.codex` under your user home) and follow the report guide to `auth.json`, `config.toml`, session logs or a local SQLite copy. Original paths are not embedded in reports. `--show-api-key` now provides this guide only.

These controls protect this program's code paths; they are not an OS firewall and do not control browser extensions or other apps. Concurrent Codex writes can produce incomplete final lines or changing snapshots. Rerun when warned; the collector never repairs source files.

## Optional official account synchronization

Run `python -I -S -B .\run.py --sync-official` to obtain an account snapshot, potentially covering other devices within the service’s scope. The dashboard shows official totals, daily Token history and quota bars independently of local detail filters. This is not a guarantee of exact, simultaneous parity with the official overview/analytics webpages. Remote per-turn/model details are unavailable unless supplied by another supported source. Missing values stay unknown; no official-minus-local estimate is made.

The adapter uses the installed Windows Store Codex client in an isolated temporary home, validates safe effective configuration before sending an access token through private stdin, and uses memory-only authentication. It does not renew tokens or copy original credentials/configuration. Unsupported interfaces and partial failures are visible; local reporting continues. Original login files remain read-only. No manual snapshot import is implemented. See [official synchronization](../docs/OFFICIAL_SYNC.md) for requirements and security boundaries.

## Development and documentation

```powershell
python -B -m unittest discover -s tests -v
node .\tests\test_dashboard.cjs
python -B .\tests\make_demo.py
```

The demo uses synthetic data and writes `.qa/demo.html`. Tests need no internet. Export tests require the local export libraries; server tests use loopback only. [Verification](../docs/VERIFICATION.md) records actual results and limitations; DOM tests do not constitute visual browser acceptance.

- [File guide and architecture](../docs/FILE_GUIDE.md)
- [Data sources and accounting details (Chinese)](../docs/DATA_SOURCES.md)
- [Changelog](../CHANGELOG.md) and [work log](../WORKLOG.md)
- [Contributing](../CONTRIBUTING.md), [security](../SECURITY.md), [maintenance rules](../docs/MAINTENANCE.md)
- [Release checklist](../docs/RELEASING.md)

## Status and license

The first local implementation is available. Automatic visual acceptance remains outstanding because the available embedded browser rejected `file://` previews. No GitHub release has been published, and no CI service is configured. The project is licensed under the [MIT License](../LICENSE).

## Interactive refresh and document exports

Double-click the launcher to open a loopback-only report service. Keep its console open; “更新数据” regenerates the full report set and reloads the page only after success. Start `启动交互报告.cmd --sync-official` to also refresh official account figures. Default collection makes no external requests. Saved HTML remains a static snapshot.

The format selector offers DOCX/PDF summaries, XLSX complete sanitized records, PNG/JPEG/WebP/SVG overview images, and the existing filtered CSV. New formats export the whole snapshot, not the current filters. Files are generated together in local `snapshot-*` directories; failed refreshes preserve the previous batch. Filters reset after a successful reload.

Exports require locally available python-docx, openpyxl, Pillow, reportlab and the Windows Microsoft YaHei font. The interactive launcher prefers the existing Codex bundled Python runtime, then PATH Python. No dependencies are downloaded. Use `python -I -B run.py --serve` or `--all-formats --json`; omit `-S` for export dependencies. The plain CLI and `--no-open` launcher remain static. See [interactive reports](../docs/INTERACTIVE_REPORTS.md) for file scopes and the local service security boundary.
