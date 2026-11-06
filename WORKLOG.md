# Work log / 工作记录

## 2026-11-06 — Codex Lens synthetic review check

- GitHub Actions on Windows and Python 3.13 failed when the paired review did not finish within the fixture's five-second wait. A synthetic delay in local SQLite reservations reproduced the same assertion.
- The fixture now runs the worker scheduled by `Service.submit` directly and asserts its terminal state. It still checks the full review budget, fresh question seeds and persisted screen provenance. Queue and cancellation tests still use background threads.
- The delayed reproduction passed after the change. Local Windows detector checks ran 157 Python tests (156 passed, one skipped), all 11 dashboard tests and the offline CLI suite listing. Main project checks ran 53 Python tests (50 passed, three skipped) and passed all 19 dashboard tests.

## 2026-11-06 — Codex Lens module release candidate

- Prepared the detector's 0.1.0 candidate with its own package version, the existing MIT license, a bilingual project landing page, a technical mathematics document, and a multi-resolution application and installer icon.
- Added a manual native build matrix for Windows x64, macOS Intel/Apple Silicon and Ubuntu 24.04 x64/ARM64. The Windows portable build completed locally. Automatic approval review blocked downloading and running the Inno Setup compiler under its policy, so the Windows setup package and the macOS/Linux packages await native runners.
- Added aggregate assessment and usage session routes and direct SDK access for future monitor integration. Synthetic tests exercised the privacy and origin guards and the offline preflight.
- Passed 157 Python tests and 11 Node tests on Windows. The 93-file source archive verified all internal hashes and document links, then passed the offline demo and 157 Python tests from an extracted standalone tree. The Windows portable archive and its frozen offline worker passed local smoke. GitHub upload and publication await the owner's confirmation.

## 2026-11-05 — Light desktop workbench

- Implemented the selected light design. The active target, model, reference status and request estimate share a toolbar. Paired scores and skill comparisons appear together, with formal statistics in the details. History owns the export controls and settings owns desktop notifications.
- Fixed a sanitization bug that could cause the official answer counts to overwrite the relay summary. Older entries with an unlabeled official count still use the relay count.
- Passed 154 Python and 11 Node tests. Edge with a synthetic backend verified target switching, deletion fallback, locked-key entry, reference assessment and review preview at wide and narrow widths. The Windows x64 package and frozen offline worker passed build smoke and archive verification.

## 2026-11-05 — Assessment accuracy and imported-key restart

- Reproduced the locked-card click path in Edge and corrected the Key submission order. Imports offer opt-in storage in the existing target-owned Windows credential item. A locked target can use a newly pasted Key directly on Start.
- Aligned task prompts and grading in quality-v2. Assessment-v2 reports planned, attempted, correct, incorrect and unscorable counts for each side. A matched initial screen uses 20 requests. It preserves formal decision allocation for complete review batches and offers a budget preview for optional independently seeded review. The new history signal requires four comparable complete runs.
- The source calibration tool exercises the desktop engine against frozen GPT/Codex settings. It reports pilot performance by task and pilot costs separately, reserves validation seeds and dates, and verifies stored conclusions against paired counts.
- Passed 154 subproject Python tests and 9 Node tests. Edge with a synthetic backend and simulated vault covered both restart paths, reference review, budget blocking, cancellation and comparison display. The local Windows x64 archive passed its worker smoke, checksum and packaged-resource checks. Real model accuracy and native Windows window interaction remain separate verification gates.

## 2026-11-05 — Same-model official reference and target deletion

- Added independent reference configuration with 16 fixed presets across 10 providers, exact IDs and verified aliases, compatible protocol checks and one-click paired reports. Static catalogs defer Key verification to detection. Legacy keys with a recorded original origin remain independently saved and pinned. Authentication, model and parameter blockers stop further official requests in the current run.
- Target deletion uses the owned UUID, cancels pending and periodic work, removes only the target profile and its credential item, and preserves history and usage. Stable aliases survive restart and are never recycled. A stale instance checks that its target still exists before sending follow-up requests.
- Passed 144 subproject Python tests and 8 Node tests. Edge exercised the GPT alias flow, permission and region feedback, report details, deletion guards and failure handling against a synthetic loopback backend. The local Windows x64 package and frozen offline worker passed smoke and archive checks. Real provider access, real-model calibration and native window interaction were outside this verification.

## 2026-11-04 — One-button Relay Auditor preview

- Added one-click assessment, target-level progress and cancellation, retriable estimates, plain result summaries and per-task paired counts. Specialist settings remain expandable.
- The declared family selects an experimental GPT/Codex, DeepSeek, Claude or Gemini profile. Other families use the shared ability suite. DeepSeek Chat uses a fixed official reference destination and separately counts direct API checks. The original destination of stored reference keys survives protocol changes.
- Isolated Python suite 112/112 and Node suite 6/6 passed. Edge with a synthetic loopback service exercised unpaired ability, official DeepSeek and matched pairs, plus one-click model switching, cancellation, estimate retry, sample controls and responsive layout. Windows bundle and offline worker smoke passed. No real model samples were collected. Native window acceptance remains open.

## 2026-11-03 — Relay Auditor quality-product implementation

- Implemented the approved product-plan software inside the existing independent subdirectory, sharing core between desktop/CLI/Python. Added versioned deterministic procedural quality/context/reasoning tasks, replay seeds/counts/public comparison parameters, v2 four-dimensional experimental reports, v1 legacy protection and same-condition history. No generated code executes; virtual tool arguments are text tests, not native function-call certification.
- Added private target/name/settings persistence separate from anonymous evidence, default-unsaved keys and optional exact-owned Windows vault storage without enumeration/plaintext fallback. Restores are disabled/locked as applicable. Added bounded sequential queue, current/queued cancellation, progress, preflight request/token/manual-price estimates, support matrix, readable offline HTML, anomaly/interruption timeline and offline synthetic demo. Model lists/custom names/reasoning/import separation remain.
- Added native Anthropic/Gemini text/stream adapters with fixed independent official reference origins, terminal/truncation/usage handling and explicit unsupported parameters. No real endpoint/model compatibility or per-family accuracy claim. Frozen source study tooling hashes generator/grader/statistics/transports, separates pilot/new dates, budgets every trial, preserves interruptions/failures and validates duplicate/cross-study outcomes; exact confidence bounds propose review candidates only. No paid study was run and no verified public baseline was invented.
- Added bilingual product docs, methods/source API/contribution guidance and a separate Windows/Linux Python3.11/3.13 synthetic-only CI definition; hosted runs/third-party contribution acceptance are not claimed. Parent runtime, offline guards and VERSION unchanged; no commit/merge/split/push/sign/release. Manager request-ledger attribution remains pending.
- Actual checks: child Python106/106 and Node6/6; root Python53 (50 passed/3 environment skips) and Node19/19. Source CLI offline demo passed. Edge synthetic-backend flows at1440×1080/700×900 passed locked restore/key update, preflight, queue/cancel, context results, missing-reference guard and anonymous HTML download, with zero observed runtime errors/horizontal overflow. Browser/server were closed. Windows portable candidate/frozen-worker smoke passed; final resource/checksum/ignore/link checks are recorded in verification.
- Open gates: real calibrated FP/power/holdout results; full current native Windows window/file-picker/exit/vault acceptance; per-family validation; community independent extension. Final native-window launch was previously denied by automatic approval (only “blocked by policy”); it was not bypassed or counted as successful validation.

This log records completed work, evidence and remaining tasks. It is not a release history or a copy of private conversations. See [CHANGELOG.md](CHANGELOG.md) for version changes.

## 2026-11-03 — Relay Auditor model options and provider import

- Reproduced native dialog failure with actual pywebview parser: the old filename-only filters and plus-sign description were invalid. Fixed valid wildcards/descriptions, visible import status/errors/cancel, known-location auto-import and manual custom-file selection.
- Added model dropdowns from bounded config/modelList or explicit relay /models GET; distinct official-reference discovery uses only independent official Key and fixed official origin. Added live-only custom names and per-target reasoning options, pending-setting application before tests, default-reference following model changes, and clear live-result/periodic reset on changed model/effort. Anonymous history/budget/exports exclude names.
- Added explicit import-only versus import-and-screen, with three requests for the latter and no periodic auto-enable. Official directory entries expose no relay tests. No source switches, authentication renewal, real configs or model calls.
- Isolated Python suite78/78, Node5/5 passed. Parent Python53 total,50 passed/3 environment skips; Node19/19. Browser QA with synthetic provider source/fake API passed model choice/custom name/xhigh import-and-screen, edited model/max setting, manual address model listing, official exclusion, button status and 1440x1080/390x844 layouts (no observed JS errors/horizontal overflow). Focused checkbox-sync reproduction failed with old behavior and passed after fix; independent-reference route failed with old behavior and passed fixed.
- Built a fresh Windows candidate and ZIP, frozen-worker synthetic smoke passed. Source desktop launcher now follows a generated latest-candidate launcher after successful build without interrupting a running old EXE. Final native-window launch with isolated synthetic environment was rejected by automatic approval with only “blocked by policy”; no workaround or final native-window claim. Real-library filter validation and simulated UI flows provide the stated evidence.
- No commit, merge, publication, signing or main-runtime/version change. True model calibration and manager request-ledger attribution remain pending.

## 2026-11-02 — Relay Auditor Windows desktop / 子项目 Windows 桌面端

- Added an independent WebView2 window, source desktop launcher and local Windows x64 portable build; no changes to parent runtime/entry points or VERSION. No commit, merge or publication.
- Desktop owns loopback/scheduler lifetime, uses dedicated per-user data and ephemeral private browser storage. Native configuration/directory selection never returns paths to the page. Exclusive anonymous exports stay under dedicated output; reminders optionally flash the taskbar. Fixed bundled offline worker is hidden and terminated on observer shutdown.
- Pinned isolated desktop/build dependencies, allowlisted assets, copied third-party notices, added real frozen-worker synthetic smoke and portable SHA-256 output. No runtime downloads, elevation, installer registration, tray process or startup task.
- Child Python 68/68 and Node 4/4 passed. Parent Python 53 total, 50 passed/3 environment skips, Node 19/19. Native candidate build and frozen synthetic worker passed; visible desktop configured a synthetic target with default-off detection and editable 2.5-minute interval, with zero issued requests. Native file-picker live clicks were interrupted by computer-use user-input detection; their handlers/cancellation/privacy have synthetic regressions rather than a claimed live acceptance.
- Independent review's MSHTML fallback and silent initialization-failure findings were reproduced with failing regressions and fixed. In-flight detector Store remains open for settlement until process exit; daemon page requests can fail during shutdown. No unresolved critical/important review finding. No real credentials, local usage or model API calls used. Real calibration, manager request-ledger attribution and parent integration remain pending.

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

- [x] Inspect synthetic overview/history pages in a real browser; see 2026-11-02 verification scope.
- [x] Run candidate native CI on all five targets; run 41376896912 passed, including frozen worker and Windows install/uninstall checks.
- [x] Confirm the original public repository and existing MIT license; no new license choice was made.
- [x] Review explicit source/docs staging; no private reports, credentials, logs or local QA artifacts uploaded.
- [x] Merge reviewed source and publish the matching tag/Release; see the completed publication record below.

## 2026-11-02 — Candidate acceptance and handoff / 候选验收与交接

- Candidate d492f26 passed all five native targets in run 41376896912. The new internal bundle resource/link-boundary tests ran on native CI; Windows and macOS ARM64 recorded all 53 Python tests passing, and each target ran the 19 Node tests and real standalone export checks.
- Used a synthetic-only loopback server and a separate Playwright Edge session to inspect overview/history at 1440×1000. Screenshots were viewed; console reported no errors/warnings. No private live report was opened or uploaded.
- Added docs/DELIVERY_REPORT.md with delivery status, implementation map, safety boundaries, actual validation, release/development commands and signing/notarization/platform follow-ups. Added README/file-guide links and corrected old changelog/status wording. Local links and version consistency passed. Formal publication is still pending at this entry.

## 2026-11-02 — v0.2.0 published / 正式发布与交接完成

- PR #1 merged to the original repository as 10f526a187f8897c07afbabba35a0c14d7280ddd; annotated tag v0.2.0 was pushed to that commit. No published tag or binary was rewritten.
- Release run 41378006761 completed all five native build/test jobs and publication successfully. The public v0.2.0 Release has eight native packages, five dependency inventories and SHA256SUMS.txt.
- Downloaded the public checksum manifest and matched all 13 file hashes to GitHub's uploaded asset digests. Verified the real public startup-check path detects 0.2.0 for 0.1.0 and returns no update for 0.2.0.
- Completed the development handoff report with merge/release/CI evidence, implementation/development/release instructions and explicit remaining signing/notarization/platform limitations. Superseded duplicate CI runs were canceled; the final tag run remains complete and green. This final documentation update does not change the release binaries.

## 2026-11-02 — Relay Auditor subproject prototype / 中转检测子项目

- Saved the approved plan and evolving attribution requirements in `agent.md`; added `subprojects/relay_auditor/` as a separately runnable subproject, not a separate Git repository. No commit, tag, push or merge was performed, and no parent runtime entry or collector guard was changed.
- Implemented synthetic probes, experimental fingerprint screening, paired capability and fixed-batch distribution tests, explicit Responses/Chat/SSE handling, persistent budgets/audit indices and atomic batch reservation, adjustable opt-in scheduling, local UI/CLI/Windows source launcher, offline usage worker, anonymous snapshots and request-evidence source grouping.
- Read-only provider discovery supports verified CC Switch and Codex++ structures, with SQLite temporary copies, official-login/direct-API exclusion and mixed-login relay recognition. Manager request-ledger ingestion and historical reconciliation remain pending; current configuration never rewrites historical attribution.
- Independent review found five important issues; regression tests reproduced and fixed scheduling cancellation races, reference-model baseline collisions, invalid-answer denominators, truncated SSE acceptance and unfrozen batch budgets/partial-audit evidence.
- Actual synthetic checks so far: subproject Python 55 passing; Node 4 passing. Parent Python 53 total, 50 passing and 3 skipped (two symlink-privilege checks, export dependencies unavailable); parent Node 19 passing. Browser QA used a simulated API only, Edge at 1440x1080 and 390x844: default off, interval edit to 150 seconds, on/off, manual three-call screen, zero observed JS errors and no horizontal page overflow. Final catalog-interface recheck passed at both viewports: official entries expose no relay detection button, importing keeps the new target disabled, request count remains three and no JS errors/page horizontal overflow were observed. The built-in browser failed to initialize its assets; the existing Playwright CLI/Edge fallback was used.
- No real credentials, private reports or actual model APIs were read/called for development. No real calibration, performance guarantee, standalone binary publication, request-ledger reconciliation or main-dashboard integration is claimed.

## Entry format / 后续记录格式

Use date → purpose → changed areas → checks actually run/results → remaining limitations. Record failed or skipped checks honestly; never include account identifiers, real logs or secret values.
