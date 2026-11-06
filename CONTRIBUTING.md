# Contributing / 贡献说明

Read the [English README](README/README.md) or [简体中文说明](README/README-Simplified_Chinese.md), [file guide](docs/FILE_GUIDE.md) and [maintenance rules](docs/MAINTENANCE.md) before changing the project.

Codex Lens is the relay detector under `subprojects/relay_auditor/`. Start with the [main project and detector handoff](docs/CODEX_LENS_HANDOFF.md) to choose the right entry point and checks. See the [CLI and Python guide](subprojects/relay_auditor/docs/EXTENDING.md) for extension contracts and the [mathematical principles](subprojects/relay_auditor/Technical-Documentation-Principles-of-Mathematics-Transfer-Station-Inspection.md) for evaluation and calibration. Ordinary development and CI use synthetic inputs.

Codex must follow the explicit-scope/minimal-change rule in [AGENTS.md](AGENTS.md): only the user's requested changes and directly necessary tests/docs. This governs repository modifications. The separate foremost product requirement is [confidentiality](SECURITY.md); private originals stay local, with only the owner's explicit OpenAI official-authentication exception.

## Development workflow

1. Use a local checkout and create a focused branch, e.g. `git switch -c fix/usage-counting`.
2. Make a small, reviewable change. Keep parsing/aggregation separate from UI presentation and preserve the default offline/read-only boundaries and the narrowly scoped opt-in official adapter described in `docs/OFFICIAL_SYNC.md`.
3. Reproduce parser or safety bugs with **synthetic** fixtures. Do not submit real auth files, logs, reports or screenshots containing account data.
4. Run applicable checks from the repository root:

   ```powershell
   python -B -m unittest discover -s tests -v
   node .\tests\test_dashboard.cjs
   python -B .\tests\make_demo.py
   ```

   Python 3.11+ is needed for the collector/tests; Node is only needed for frontend tests. Static collector tests need no dependencies; full export/build checks require `python -m pip install -r requirements-build.txt` and `python build_tools/build.py --prepare-only` at build time. The demo output is `.qa/demo.html`.
5. Update both READMEs when shared facts change, the work log, and other files required by the maintenance matrix. Record any failures or skipped tests.
6. Review `git diff` and `git diff --cached` before committing. Submit a PR explaining the problem, resulting behavior, verification and limitations.

## Detector checks / 检测器检查

Run these separately from the root monitor checks. The detector demo uses a synthetic model and requires only Python 3.11+.

```text
cd subprojects/relay_auditor
python -I -S -B run.py demo
python -B -m unittest discover -s tests -v
node tests/test_dashboard.cjs
```

When changing an evaluation, record the suite version and the precise comparison conditions. For an API or snapshot change, include a synthetic compatibility and privacy check. For packaging, report the target OS, architecture and the checks actually run. [Native build instructions](subprojects/relay_auditor/docs/RELEASING.md)

纯文档变更检查链接、版本和中英文一致性即可；不要声称重新运行了未执行的测试。浏览器视觉检查应使用合成演示，DOM 单元测试不等于视觉验收。

## License status

The project is licensed under the [MIT License](LICENSE). Retain its copyright and permission notices when redistributing the software.
