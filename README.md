# Codex Usage Check

A local dashboard for inspecting Codex usage records, with startup update checks and optional official account synchronization. Source files remain read-only.

**Version:** 0.2.0 · Standalone packages and startup update checks.

**[Download / 下载安装包](https://github.com/3271741455CJ/Codex-Token-Usage-Monitor/releases/latest)** — Windows、macOS (Intel / Apple Silicon)、Linux (x64 / ARM64)，内置 Python 和导出依赖。See [installation / 安装说明](docs/INSTALLATION.md).

## Codex Lens / 中转模型检测

Codex Lens is a separately runnable detector module for the token monitor. It evaluates relay models and can compare them with an eligible official reference on the same tasks. Its build version and packages are managed separately from the monitor.

Codex Lens 是主项目的检测功能模块。它可以独立运行，后续通过 v2 匿名检测与用量快照接入主项目。先从下面的入口选择你要维护的部分。

- [检测器首页 / Detector overview](subprojects/relay_auditor/README.md)
- [主项目与检测器开发交接 / Developer handoff](docs/CODEX_LENS_HANDOFF.md)
- [检测数学原理 / Mathematical principles](Technical-Documentation-Principles-of-Mathematics-Transfer-Station-Inspection.md)

## Documentation / 项目说明

- [English — full README](README/README.md)
- [简体中文 — 完整项目说明](README/README-Simplified_Chinese.md)
- [File guide / 文件说明](docs/FILE_GUIDE.md)
- [Changelog / 版本变更](CHANGELOG.md)
- [Work log / 工作记录](WORKLOG.md)
- [Delivery and development handoff / 工作进度与开发交接报告](docs/DELIVERY_REPORT.md)

Windows quick start: double-click `查看Codex用量.cmd` for local interactive refresh and Word/Excel/PDF/image exports; see [requirements and format scopes](docs/INTERACTIVE_REPORTS.md).
The generated `.reports/latest.html` uses anonymous references and local viewing guides for sensitive originals; usage statistics remain private local output. See the foremost [confidentiality rule](SECURITY.md).

This independent project is not an official OpenAI product. Local records are not a complete account bill. Licensed under the [MIT License](LICENSE).
