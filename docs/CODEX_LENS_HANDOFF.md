# 主项目与检测器开发交接 / Developer handoff

Codex Token Usage Monitor collects and presents local token usage. Codex Lens evaluates the service quality of relay models. It lives under `subprojects/relay_auditor/` and can run independently while the host integration is developed. Both use synthetic fixtures for development.

## 从哪里开始 / Choose a component

| 工作范围 | 源码和运行入口 | 版本与文档 |
| --- | --- | --- |
| 主项目 · Codex Token Usage Monitor | 根目录 `run.py` 与 `desktop.py`。采集、聚合、交互报告和导出位于 `codex_usage/`。 | 根目录 `VERSION` 与主项目 Releases。现有交接见[主项目 v0.2.0 交付记录](DELIVERY_REPORT.md)。 |
| 检测器 · Codex Lens | `subprojects/relay_auditor/run.py` 与 `desktop.py`。Python 核心和本机界面位于该目录的 `relay_auditor/`。 | 检测器自己的 `VERSION`。入门见[检测器首页](../subprojects/relay_auditor/README.md)，逐文件职责见[检测器文件指南](../subprojects/relay_auditor/FILE_GUIDE.md)。 |

主项目验证从仓库根目录运行。合成演示生成本地 HTML。

```text
python -B tests/make_demo.py
python -B -m unittest discover -s tests -v
node tests/test_dashboard.cjs
```

检测器验证从子项目目录运行。命令行演示使用已知答案，无需配置真实接口或 Key。

```text
cd subprojects/relay_auditor
python -I -S -B run.py demo
python -B -m unittest discover -s tests -v
node tests/test_dashboard.cjs
```

## 检测器改动入口 / Detector work areas

以下路径均相对于 `subprojects/relay_auditor/`。

| 想改什么 | 先读哪里 |
| --- | --- |
| 浅色工作台、目标切换、报告展示 | `relay_auditor/web/`、`tests/test_dashboard.cjs` |
| 检测队列、预算与同题对照 | `relay_auditor/` 中的 `controller.py`、`planning.py`、`assessment.py` |
| 题目、判分与报告 | `relay_auditor/` 中的 `suites.py`、`statistics.py`、`reports.py`。先读[数学原理](../subprojects/relay_auditor/Technical-Documentation-Principles-of-Mathematics-Transfer-Station-Inspection.md)。 |
| 中转导入、官方匹配及传输 | `relay_auditor/` 中的 `catalog.py`、`official.py`、`adapters.py`、`transport.py` |
| 窗口、安装包和图标 | `relay_auditor/desktop.py`、`relay_auditor/runtime.py`、`build_tools/`、`assets/` |
| 隐私与用量归属 | `relay_auditor/` 中的 `storage.py`、`profiles.py`、`vault.py`、`accounting.py`，以及固定入口 `usage_worker.py` |

## 以后如何接到主项目 / Host integration

- 检测器通过 `Auditor.snapshot()` 和 `Auditor.usage_snapshot()` 提供 v2 匿名检测及用量数据。独立本机服务提供会话内的 `GET assessment` 与 `GET usage`。接入方应检查 `schema_version` 和 `snapshot_type`。带有界面专用私有字段的 `GET state` 留在检测器界面中。
- 主项目继续负责离线采集、可选官方同步和汇报。检测器负责目标凭据、官方参考、预算、队列及检测。未来接入可先做只读展示，再按用户明确操作调用 `estimate()`、`submit()` 和 `cancel()`。
- 官方登录、官方 API、各中转渠道及未知来源分别处理。业务消耗、检测探针和官方参考的计量各有范围。跨来源合并或归属需要逐请求证据。

详细字段、使用示例及版本约定见 [CLI 和 Python 接入契约](../subprojects/relay_auditor/docs/EXTENDING.md#integration-contract--token监视器接入)。

## 构建状态与接手顺序 / Build status and next work

检测器 0.1.0 候选已在 Windows x64 构建便携 ZIP，并验证冻结离线 worker。Windows Setup、Intel 与 Apple Silicon 的 macOS DMG，以及 Ubuntu 24.04 x64 与 ARM64 的 DEB 和 tar.gz 需要各自的原生构建与验证。

本仓库中的[检测器原生构建工作流](../.github/workflows/relay-auditor-native.yml)为手动触发，产物供验证和审阅。独立源码包提供子项目自己的同类工作流。正式发布前需要单独确认安装包、标签与可见状态，维护者应保护主项目的正式版本和更新入口。 [检测器构建说明](../subprojects/relay_auditor/docs/RELEASING.md) · [主项目发布流程](RELEASING.md)

建议按具体任务推进：

1. **主项目接入**。先用合成 v2 快照做只读展示，测试旧版本、未知来源和缺失用量的显示，再审阅进程和权限边界。
2. **桌面包验收**。按平台记录包校验值、安装、启动、卸载和本机数据目录行为。签名和公证状态随各候选注明。
3. **检测准确性**。先选定确切型号、对照条件和预算，再通过冻结的先导与验证流程采样。现有软件回归验证程序行为，真实误报率与检出率须由对应实验给出。

## 评审时核对 / Review checklist

- PR 说明改动属于主项目、检测器，还是 v2 接口契约。
- 从对应目录记录实际执行的合成检查、平台和已知限制。涉及展示时附合成截图或清晰的复现步骤。
- 保持正式包、候选包和源码归档的版本与校验值可追溯。公开内容使用经审阅的源码、合成夹具和匿名示例。
- 私人配置、Key、原始日志、账户数据与真实报告留在本机。涉及字段、凭据、回环路由或 worker 的改动一并审阅隐私边界。 [保密规则](../SECURITY.md) · [维护矩阵](MAINTENANCE.md)
