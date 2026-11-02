# Work log / 工作记录

This log records completed work, evidence and remaining tasks. It is not a release history or a copy of private conversations. See [CHANGELOG.md](CHANGELOG.md) for version changes.

## Current status / 当前状态

Version: **0.1.0**, initial local implementation. GitHub upload/release: **not performed**.

| Area / 项目 | Status / 状态 | Evidence / 依据 |
| --- | --- | --- |
| Local collector and accounting / 采集与统计 | Implemented / 已实现 | `codex_usage/`, parser tests |
| Read-only and offline protections / 只读与离线 | Implemented and tested / 已实现并测试 | Privacy and database tests |
| Dashboard logic / 页面逻辑 | Implemented and tested / 已实现并测试 | Synthetic DOM tests |
| Optional official synchronization / 可选官方同步 | Implemented, unreleased / 已实现、待发布 | 2026-10-29 official usage/limits requests succeeded; no web-parity claim |
| Visual browser acceptance / 浏览器视觉验收 | Outstanding / 待完成 | Embedded browser rejected `file://` |
| Documentation / 文档 | Initial documentation prepared / 已整理首版文档 | Bilingual README and `docs/` |
| License / 许可证 | MIT selected / 已选择 MIT | `LICENSE` added locally |
| GitHub publication / 发布 | Not started / 未执行 | No commit/tag/remote created by this documentation task |

## 2026-11-01 — MIT license selected / 选择 MIT 许可证

- Added the MIT license and synchronized the license status in the project documentation. No commit or push was performed.
- Checked license links, version/status wording, ignore rules and `git diff --check`; implementation tests were not rerun for this documentation-only change.

## 2026-10-26 — Initial implementation verification / 首版验证

- Completed the local collector, dashboard, launcher and data-source documentation.
- Recorded 30 passing Python tests plus one Windows symlink test skipped; 14 frontend tests passed.
- Verified local collection, credential exclusion, reconciled direct totals and CSP hashes.
- Recorded the visual-verification limitation in [VERIFICATION.md](docs/VERIFICATION.md).

## 2026-10-29 — Repository documentation / 仓库文档整理

- Moved the full Chinese README into `README/`; added the English README and a root language-navigation page.
- Established `VERSION` (0.1.0), changelog, work log, file guide and synchronization rules.
- Added contribution/security guidance and issue/PR templates; extended ignore and text-formatting rules.
- Scope: documentation and repository hygiene; no collector behavior changes, GitHub upload or cloud CI execution.
- Validation: relative Markdown links, documentation versions and sensitive-output ignore rules checked locally. Prior implementation test results remain dated 2026-10-26; they are not presented as a new test run.

## 2026-10-29 — Optional official account usage / 可选官方账号用量

- Owner explicitly authorized optional official-client networking while retaining default offline collection; updated `AGENTS.md` and security documentation accordingly.
- Added `--sync-official`, isolated official app-server startup, effective-config validation, memory-only authentication, fixed error states and allowlisted usage/daily/limit parsing. Original auth/config/log/database sources remain read-only; no model turn or credential refresh is requested.
- Added separate official summary cards, daily visualization/table and quota bars. Local filters and totals never change official figures or imply complete remote per-turn coverage.
- Updated bilingual READMEs, source/file guides and synthetic demo/tests. `VERSION` remains 0.1.0, changes are Unreleased; no commit, tag, push or release performed.
- Validation: Python 3.15 on Windows, 39 tests: 38 passed, one symlink-privilege skip; Node frontend: 16 passed. Initial sandbox runs hit temporary-directory and hardlink permissions; final Python run used a project-local temporary directory outside the sandbox after automatic approval.
- Checked the installed official client's initialization/config protocol without credentials. Subsequently verified actual account usage and limits successfully with status-only tool output; original auth content/mtime unchanged and isolated runtime removed. Generated the private report without exposing its values. Credentials were checked locally for exclusion from the report.
- Browser visual check on synthetic data remains blocked by the embedded browser's `file://` policy; no workaround used. Official overview/analytics webpage parity has not been verified. See [verification](docs/VERIFICATION.md).
- Final local Markdown links, version consistency and private-output ignore checks passed; the generated report was updated with the final template without exposing private values.

## 2026-10-29 — Confidential output and scoped modifications / 保密输出与最小改动

- Established the foremost product privacy rule and explicit sensitive-data categories in `SECURITY.md`. Preserved the owner's exception allowing necessary access token/account ID only for OpenAI official authentication. Report-needed networking is permitted under that rule; this change adds no crawler or third-party endpoint.
- Put Codex's requested-scope-only rule separately in `AGENTS.md` and maintenance/contributor instructions. Changes are limited to output privacy, local viewing guides, related tests and documentation; parser/accounting algorithms and official authentication/sync implementation were not changed.
- Added a shared output allowlist/alias layer before HTML and JSON serialization; CSV uses sanitized embedded data. Removed original identities, titles, IDs, private configuration/paths and key fragments. Sensitive originals have local viewing guides; alias mappings stay in memory. Changed `--show-api-key` to guidance only and suppressed private values in CLI success/error output.
- Updated bilingual READMEs, source/file guides and Unreleased notes. Kept VERSION 0.1.0; no commit/tag/push/release.
- Validation: Windows / Python 3.15, 42 tests: 41 passed, one symlink-privilege skip; Node: 17 passed. The first sandbox run failed only at hardlink fixture creation; the final synthetic-data run passed outside the sandbox after automatic approval. Added end-to-end output/CSV privacy, alias relationship, preserved accounting and CLI guidance checks; regenerated the synthetic demo.
- Sanitized the existing default local HTML report without new authentication/network calls; local totals and the official snapshot were unchanged. No default JSON export existed. Tool output contained only success flags, never report values. Copies previously exported elsewhere were not scanned or modified.
- Browser visual acceptance remains outstanding under the previously recorded `file://` policy restriction. No claim of a new visual check or exact official-webpage parity.
- Final relative Markdown link, version-consistency and private-output ignore checks passed. Reviewed changes against the local pre-change source snapshot; unrelated parser, database, safety, official-client and launcher code were not changed.


## 2026-10-30 — Multi-format exports and local refresh / 多格式导出与本机更新

- Added privacy-filtered DOCX/PDF summaries, XLSX complete field/detail records, PNG/JPEG/WebP/SVG overview images and format selection alongside existing filtered CSV. All files share a snapshot; exports do not read raw credentials or upload data.
- Added a loopback-only service with random session paths, exact Host checks, same-origin POST/header validation, fixed download routes and fixed guarded collector workers. Complete generations replace the served snapshot only after success; errors preserve previous files and use fixed messages. The original collector audit guard is unchanged.
- Updated the double-click launcher to use the interactive service and an existing local export runtime. Plain CLI and --no-open remain static. Official synchronization stays opt-in. Local export dependencies and Windows font requirements are documented; nothing was downloaded.
- Validation: bundled Python 3.12, 44 tests: 43 passed, one Windows symlink-privilege skip. Node: 19 passed. Export package/image integrity, spreadsheet formula neutralization, privacy filtering, origin/Host/path rejection, failure retention, live refresh success/retry and CSP hashes covered. An actual synthetic guarded worker was exercised through loopback HTTP, including refresh and all format downloads.
- Initial bundled-runtime tests exposed a Windows stdout encoding mismatch; CLI streams now explicitly use UTF-8. Initial manual CSP verification did not normalize CRLF as an HTML parser does; the corrected check passed and became a regression assertion.
- Rendered synthetic DOCX via local LibreOffice, PDF via Poppler, and all six XLSX tabs via LibreOffice/PDF. Inspected PNG previews; removed the inherited Word title border, embedded Chinese PDF font and fitted Excel print width. Image overview also visually checked. Full browser layout acceptance remains outstanding; prior file:// restriction was not bypassed.
- Existing private default snapshot was exported locally to every new format with status-only output; no new official authentication or source-data changes were needed. Previously downloaded copies do not auto-update. VERSION stays 0.1.0 / Unreleased; no commit, push or release.

- Final local Markdown link, version and new private-export ignore checks passed.

## 2026-11-01 — Desktop release and startup updates / 安装包与启动更新

- Implemented bounded public stable-release checks, explicit update consent and offline/version flags; no private input is sent, and collector workers never check versions.
- Added standalone dispatch, per-user output, desktop browser launch, bundled Chinese export font and native Windows/macOS/Linux packaging with clean-build CI and complete-release checksums.
- Added Windows current-user installation, no-UPX one-folder builds, product metadata and optional verified Authenticode signing/timestamps; documented unsigned SmartScreen and macOS notarization limitations.
- User redirected delivery to the original `3271741455CJ/Codex-Token-Usage-Monitor` repository. Its main matches the fork baseline; collaborator push access was verified without exposing credentials. Update/release links target the original repository.
- Local Windows Python 3.13: 52 tests, 51 passed and one symlink-privilege skip; Node dashboard: 19 passed. Native bundles, installer and cross-platform CI validation are pending at this entry; no publication claimed yet.

## 2026-11-02 — Standalone Windows verification / Windows 独立程序验证

- Built the no-UPX one-folder Windows application with bundled Python 3.13.14, export libraries and the pinned OFL Chinese font. The real frozen guarded worker generated all nine output files from synthetic data; source content/mtime remained unchanged and private fixture values were excluded.
- Re-ran the 52 Python tests: 51 passed, one symlink-privilege skip; all 19 Node dashboard tests passed. A local Microsoft Defender custom scan of the built application reported zero detections. This does not prove SmartScreen download reputation, code signing or clean behavior on every machine.
- Corrected unsigned installer handling so SignedUninstaller is enabled only when its signing backend is configured; clarified installed-app output guidance.
- GitHub rejected the original-repository branch push because the existing PAT lacks workflow scope. No implementation commit, tag or Release has been published remotely yet. Browser submission also stopped because the UI tool could not confidently determine the browser URL. User chose to add workflow permission; publication awaits that change and native CI results.

## 2026-11-02 — Original-repository native CI / 原仓库原生构建

- User added workflow scope; implementation and workflow commits were pushed to the original repository's feature branch. Run 41376083373 passed Windows build/install/uninstall and Linux ARM64 native packaging; macOS tests exposed the system `/var` temporary-directory symlink, correctly rejected by the unchanged source guard.
- Moved synthetic CI fixtures into the runner's real temporary directory and canonicalized the build smoke test's own temporary root. Source symlinks remain rejected; no runtime guard was relaxed. Native macOS revalidation remains required. Corrected the Chinese README's old CI-status sentence.

The second native run passed macOS source regressions but the frozen app hit PyInstaller's internal resource links. Added a narrowly bounded read-only bundle resource exception: both lexical and resolved paths must remain inside the executable bundle. Source checks, external links and writes remain protected. Added synthetic regression coverage; native frozen-app revalidation is pending.

## Before publishing / 发布前待办

- [ ] Manually verify layout in a local browser using synthetic demo data.
- [ ] Rerun applicable tests against the final release candidate and record the results.
- [ ] Decide repository visibility and license; add license text only after an explicit owner choice.
- [ ] Review staged files for private reports, credentials and local paths.
- [ ] Create the GitHub repository, push reviewed source, and create a tag/release when ready.

## Entry format / 后续记录格式

Use date → purpose → changed areas → checks actually run/results → remaining limitations. Record failed or skipped checks honestly; never include account identifiers, real logs or secret values.
