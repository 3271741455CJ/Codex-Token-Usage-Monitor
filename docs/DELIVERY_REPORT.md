# 工作进度与开发交接报告

更新日期：2026-11-02（Asia/Shanghai）。本报告对应 v0.2.0 的启动更新检查、桌面分发与发布流程改造，面向后续协作开发者。

## 交付位置与状态

- 目标原仓库：[3271741455CJ/Codex-Token-Usage-Monitor](https://github.com/3271741455CJ/Codex-Token-Usage-Monitor)。本次成果提交在原仓库，不以个人 fork 作为更新源。
- 实现分支：`codex/startup-updates-and-releases`。实现候选 `d492f26` 已通过[五平台原生 CI](https://github.com/3271741455CJ/Codex-Token-Usage-Monitor/actions/runs/41376896912)。
- 当前进度：功能、原生构建及候选验收完成；正在完成合并和 v0.2.0 正式发布。正式发布结果将补充到本文“发布完成记录”，不能把候选测试通过等同于 Release 已上线。
- 版本唯一来源：[VERSION](../VERSION)；用户更新入口：[Releases](https://github.com/3271741455CJ/Codex-Token-Usage-Monitor/releases/latest)。

| 工作项 | 当前结果 |
| --- | --- |
| 启动检查本工具版本、询问是否更新 | 已实现并测试 |
| 完全离线启动、版本显示 | `--no-update-check` / `--version` 已实现 |
| Windows 安装器与便携 ZIP | 构建、独立导出、安装/卸载检查通过 |
| macOS Intel / Apple Silicon DMG | 两个原生架构构建与独立导出检查通过 |
| Linux x64 / ARM64 DEB 与 tar.gz | 两个原生架构构建与独立导出检查通过 |
| Python、导出依赖与中文字体内置 | 已完成，运行时无需安装依赖 |
| 隐私、只读、网络和本机服务边界 | 保留并增加包内资源回归检查 |
| Windows 可信代码签名 | 后端和校验流程已接入，当前构建为未签名 |
| Apple Developer ID 公证 | 未配置，后续工作 |
| 正式 Release、下载附件与更新接口核对 | 发布阶段进行中，完成后补记 |

## 本次具体实现

### 版本检查与用户确认

`codex_usage/updates.py` 只访问原仓库固定的 GitHub latest Release API。使用数字语义版本比较，仅识别 `vMAJOR.MINOR.PATCH` 的已发布正式版；不采纳草稿、预发布、降级或其他仓库链接。

每次用户启动最多等待四秒。发现更高版本后询问是否打开同一原仓库的 HTTPS 下载页，提示适合当前系统的安装包名称。用户拒绝、断网、限流或响应异常时继续本地工作；用户确认后自行下载，退出旧进程后安装。当前实现不静默下载、不自动执行或覆盖运行中的程序。

请求不读取或发送 Codex 登录信息、用量、配置、路径、Cookie 或个人标识，也不继承代理。后台刷新工作进程固定带 `--no-update-check`，不重复弹窗。

### 安装后直接使用

`desktop.py` 为独立入口，无参数时启动本机交互报告；`--worker` 分支仅执行受限采集。`runtime.py` 区分源码与冻结程序，生成固定工作进程命令，防止子进程递归启动服务。

独立包内置 Python、python-docx、openpyxl、Pillow、reportlab 和中文字体。字体从固定 Google Fonts Git blob 下载并校验，构建时派生为静态 TrueType，附 SIL OFL；依赖许可证随包分发。安装后的用户只需已有本机 Codex 数据与浏览器。

| 平台 | 独立版报告目录的父位置 | 包形式与基线 |
| --- | --- | --- |
| Windows | `%LOCALAPPDATA%` | x64 Setup.exe / portable.zip；Windows 10/11 |
| macOS | `~/Library/Application Support` | Intel / ARM64 DMG；macOS 13+ |
| Linux | `${XDG_DATA_HOME:-~/.local/share}` | x64 DEB/tar.gz：glibc 2.35+；ARM64：glibc 2.39+ |

上述位置下使用 `Codex-Token-Usage-Monitor/reports`；源码仍默认 `.reports/`。升级和卸载不自动清理用户报告，也不改动 Codex 源数据。Windows Store 版本检测和可选官方同步仍限 Windows。

### 发布流程与 Windows 信誉处理

`.github/workflows/release.yml` 在五个平台原生运行测试、打包及真实独立进程检查。Windows 额外静默安装到测试目录、运行已安装程序、再卸载。版本标签必须与 VERSION 相同。

全部构建成功后，发布任务验证八个必需安装附件，生成 SHA256SUMS.txt，先创建草稿、上传完整附件，再公开 Release。构建失败不发布残缺正式版。每个平台另附依赖版本清单。

Windows 使用无 UPX 的目录式包、标准 Inno Setup、固定 AppId、明确产品/版本/发布者信息、用户级安装和卸载支持。可通过仓库 Secrets 接入可信 PFX 签名，对程序、安装器、安装器临时副本和卸载器签名，并验证时间戳；`REQUIRE_WINDOWS_SIGNING=true` 可阻止未签名发布。详见 [WINDOWS_TRUST.md](WINDOWS_TRUST.md)。

当前没有可信签名证书，云端日志明确标记 UNSIGNED。本机 Defender 对候选构建的扫描未发现威胁，但不能据此承诺 SmartScreen 无提示。信誉需要可信发布者身份及后续积累；程序未修改杀毒设置、排除列表或下载来源标记。

## 关键文件与调用链

| 文件 | 接手时关注的职责 |
| --- | --- |
| `run.py` | 参数、更新检查入口、路径验证与采集 guard 安装 |
| `desktop.py` | 独立应用默认启动与固定 worker 分流 |
| `codex_usage/updates.py` | 版本比较、固定公开 API、超时、确认框与可信发布页 |
| `codex_usage/runtime.py` | 用户输出目录与源码/独立程序工作命令 |
| `codex_usage/server.py` | 回环服务、完整批次切换、默认浏览器打开 |
| `codex_usage/exports.py` | 中文字体选择与原有隐私导出 |
| `codex_usage/safety.py` | 原有离线/只读边界，以及冻结应用内部只读资源例外 |
| `build_tools/build.py`, `monitor.spec` | 固定字体源、许可证、原生打包与打包后检查 |
| `build_tools/windows.iss`, `sign-windows.ps1` | 当前用户安装、可选签名与验证 |
| `build_tools/smoke.py`, `release_manifest.py` | 合成独立进程验收与完整附件/校验值检查 |
| `tests/test_updates.py`, `test_bundle_resources.py` | 更新确认和应用包资源安全回归 |

调用链：用户启动 → 公开版本检查/确认 → 回环服务 → 固定且禁用版本检查的 worker → 原有只读采集/隐私过滤 → 同一批次的网页与文档图片。

macOS 的 PyInstaller 模板/库链接在 Frameworks 与 Resources 之间。新增例外仅允许“原路径、解析目标均在当前运行应用包内”的只读打开；越界链接、包内写入与用户显式源路径链接仍被拒绝。这是后续修改时需要保留并测试的边界，详见 [SECURITY.md](../SECURITY.md)。

## 验证与证据

- [五平台原生候选运行 41376896912](https://github.com/3271741455CJ/Codex-Token-Usage-Monitor/actions/runs/41376896912) 全部通过；各任务执行 53 项 Python 合成测试与 19 项前端测试。
- 各平台真实独立工作进程生成全部 9 个文件，核验源内容/修改时间不变、合成私人字段不进入 HTML；Windows 已安装程序也执行相同检查。
- 本机 Windows Python 3.13.14：53 项中 51 通过、2 项因符号链接权限跳过；云端原生环境实际运行链接检查，Windows 与 macOS ARM64 日志记录 53 项全部通过。
- 合成总览/历史页已用独立 Edge 会话在 1440×1000 检查并查看截图，控制台 0 errors / 0 warnings。不是所有设备、所有分辨率的完整验收。
- Markdown 本地链接和 VERSION/双语 README 一致性通过。所有测试均使用合成数据；未上传真实账号、报告、日志、配置或凭据。
- 详细结果与曾经失败后修复的 macOS 临时目录/包内资源问题见 [VERIFICATION.md](VERIFICATION.md)；过程记录见 [WORKLOG.md](../WORKLOG.md)。

## 后续开发操作

先阅读 [AGENTS.md](../AGENTS.md)、[SECURITY.md](../SECURITY.md)、[MAINTENANCE.md](MAINTENANCE.md)。在独立 Python 3.11+ 环境准备构建依赖，然后从仓库根目录执行：

```text
python -m pip install -r requirements-build.txt
python -B build_tools/build.py --prepare-only
python -B -m unittest discover -s tests -v
node tests/test_dashboard.cjs
python -I -B run.py --serve --no-update-check
```

macOS 测试临时目录应是没有符号链接的真实路径；CI 使用 runner.temp，不应通过关闭源路径检查解决。查看/导出真实数据只在本地进行，不加入测试夹具。

目标系统本机执行 `python -B build_tools/build.py`。Windows 需 Inno Setup 6，macOS 用 hdiutil，Linux 用 dpkg-deb；这是原生构建，不是交叉编译。`--bundle-only` 可先检查独立程序。

发布下一版时修改 VERSION 及对应双语说明/变更记录，完成分支 CI 后合并，再创建并推送同版本 `vX.Y.Z` 标签；等所有原生构建及发布任务成功后核对安装附件与 latest API。不要移动已经发布的标签。失败的附件上传可能留下草稿，维护者应检查草稿状态后恢复，不能在同一正式标签下悄悄替换二进制。完整步骤见 [RELEASING.md](RELEASING.md)。

## 接手待办与已知限制

1. **Windows 可信签名**：由发布者取得并验证合法身份，接入适合证书的硬件/云端签名服务；当前 PFX 接口只适用于已有可导出证书。私钥和密码只进入 Secrets，不能写入仓库或 Issue。
2. **macOS 分发信任**：接入 Developer ID 签名、公证及 staple；当前 DMG 未公证，Gatekeeper 可能警告或拦截。
3. **覆盖范围**：继续在干净实体机、不同桌面环境与分辨率验收。Windows ARM 使用 x64 模拟；没有原生 Windows ARM、32 位、Android/iOS 或 musl Linux 包。
4. **更新方式**：当前确认后打开下载页，安装仍由用户完成。如需自动安装，需另行设计签名、哈希验证、回滚与重启流程。
5. **账号同步**：仍限原有 Windows 官方客户端适配器；其他系统默认只分析本机记录。不能把本地记录当完整云端账单，也未验证所有官方网页指标一致。

## 发布完成记录

待正式发布后补充 Release、合并提交与最终核对结果。
