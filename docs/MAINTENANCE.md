# Maintenance and synchronization / 同步维护规则

These are Codex/contributor modification rules. Follow [AGENTS.md](../AGENTS.md): change only the user's explicitly requested scope and directly necessary tests/docs; this matrix does not authorize unrelated work. 产品首要保密约束单独定义于 [SECURITY.md](../SECURITY.md)，不得与 Codex 的最小改动规范混淆。

Changes must update their affected documentation in the **same commit or pull request**. Do not let one README describe functionality missing from the other.

## Change matrix / 更新对应表

| Change / 变更 | Files to update / 同步文件 |
| --- | --- |
| Feature, CLI, requirements, platform support, privacy behavior | Both full READMEs; root navigation if its summary changes; `CHANGELOG.md`; `WORKLOG.md` |
| Parser fields, accounting, account attribution or source files | `docs/DATA_SOURCES.md`, affected READMEs, meaningful tests, changelog and work log |
| New/moved/deleted project files or architectural changes | `docs/FILE_GUIDE.md`, affected links/imports, work log; changelog if user-visible |
| Security boundary or private output changes | `SECURITY.md`, privacy sections in both READMEs, `.gitignore` if relevant, tests, changelog/work log |
| Test commands or actual validation results | `CONTRIBUTING.md`, READMEs if commands change, `docs/VERIFICATION.md` with actual date/environment/results |
| Release version | `VERSION`, both full READMEs, root README, `CHANGELOG.md`, `WORKLOG.md`; matching tag/release only when actually published |
| Documentation-only wording/translation correction | Both corresponding README passages when shared facts change; work log; changelog only if user-visible meaning changes |
| Contribution or release process | Relevant process docs, `AGENTS.md` or `.github/` templates as applicable |

## Version rules / 版本规则

- `VERSION` contains one `MAJOR.MINOR.PATCH` value and is the source of truth. Initial version: **0.1.0**.
- Record changes after the initial baseline under `CHANGELOG.md` → `Unreleased` until preparing the next release.
- Increment PATCH for compatible fixes, MINOR for new compatible features, MAJOR for incompatible changes. Before 1.0, explicitly call out incompatibilities and advance MINOR for them.
- Documentation edits do not automatically require a new version. Never create a new release just to make the work log look current.
- When preparing a release, assign its version and move the corresponding Unreleased entries into that version section. Keep “not released” until publication; record an actual release date only after publication.
- The Git tag is `v` plus the exact VERSION value. Do not rewrite published tags; use a new version for corrections.

## Evidence and review / 证据与检查

1. Compare both READMEs for matching capabilities, requirements, commands, limits and version/status.
2. Check relative links after moving files; root README remains a short language-navigation page.
3. Record tests actually run and their date, environment, pass/fail/skip results. Do not convert old results into current validation or claim DOM tests prove visual layout.
4. Review staged files and ignored paths; only synthetic fixtures and screenshots may be shared.
5. Keep known limitations and work-log pending tasks until there is evidence they are resolved.
6. Before release, follow [RELEASING.md](RELEASING.md).

These are contributor/reviewer rules, not an installed automatic enforcement service. There is no cloud CI or automatic documentation synchronizer in this initial version.
