# Installation / 安装与更新

Download from [this repository's Releases](https://github.com/3271741455CJ/Codex-Token-Usage-Monitor/releases/latest). Desktop packages include Python, document export libraries and a Chinese font. Existing local Codex data and a browser are required. Runtime dependencies are never downloaded.

从上述 Release 下载对应系统及架构的文件，无需安装 Python。默认读取当前用户的 `.codex` 或 `CODEX_HOME`；没有数据时请先使用 Codex，或用 `--codex-home` 指定本地数据目录。

| Platform / 平台 | Package / 文件 | Install / 安装 |
| --- | --- | --- |
| Windows 10/11 x64 | `windows-x64-Setup.exe` | Current-user installer, Start Menu shortcut, no requested elevation / 当前用户安装，无需管理员权限 |
| Windows portable | `windows-x64-portable.zip` | Extract the whole folder; run the EXE; keep `_internal` / 整体解压并保留配套文件 |
| macOS 13+ Intel | `macos-x64.dmg` | Drag the app to Applications / 拖入“应用程序” |
| macOS 13+ Apple Silicon | `macos-arm64.dmg` | Native ARM app; same installation / 原生 ARM 应用 |
| Ubuntu 22.04+ / glibc 2.35+ x64 | `linux-x64.deb` / `.tar.gz` | Install DEB using the system installer, or extract and run the executable / 系统安装器安装 DEB，或解压运行 |
| Ubuntu 24.04+ / glibc 2.39+ ARM64 | `linux-arm64.deb` / `.tar.gz` | Same as above / 同上 |

Windows ARM can use the x64 package through emulation; no native Windows ARM binary is supplied. Android/iOS, 32-bit systems and Alpine/musl Linux are unsupported. Official account synchronization and Windows Store version detection remain Windows-specific. / 官方同步未扩展至 macOS/Linux。

## Launch and update / 启动与更新

- Double-click the app to open its loopback-only browser report. Keep the process running for refresh. / 双击启动本机报告，保留进程即可更新数据。
- Every user launch checks this monitor's public stable release. A newer version asks Yes/No before opening the same repository's HTTPS release page, identifying the matching package when available. Exit the app before installing the new version into the same location. / 每次启动检查本工具正式版，确认后打开下载页；退出后覆盖安装。
- The app does not automatically download, execute or elevate installers. Declining keeps the old version; the next launch checks again. Offline/API/rate-limit failures do not block collection. Startup waits at most four seconds; background refresh workers never prompt. / 不静默更新；断网或拒绝不影响使用，刷新不重复弹窗。
- `--no-update-check` skips the check for a fully offline launch (unless also requesting `--sync-official`); `--version` prints the installed monitor version. Custom interactive invocations must include `--serve`, e.g. `Codex-Token-Usage-Monitor --serve --no-update-check`. / 两参数同时适用于源码和安装版，自定义交互运行请带 `--serve`。

## Local output / 本机输出

Installed apps write `Codex-Token-Usage-Monitor/reports` below `%LOCALAPPDATA%` (Windows), `~/Library/Application Support` (macOS), or `${XDG_DATA_HOME:-~/.local/share}` (Linux). Source runs retain `.reports/` beside `run.py`. `--output` overrides this. Parents are created after protected-path validation. Upgrade and uninstall preserve user reports and Codex originals. / 报告独立于程序目录，升级与卸载不自动删除，Codex 原文件保持只读。

`SHA256SUMS.txt` and platform dependency inventories accompany releases. Verify Windows downloads using `Get-FileHash -Algorithm SHA256 <file>`, macOS using `shasum -a 256 <file>`, Linux using `sha256sum <file>`. Checksums verify integrity, not publisher identity. / 校验值用于检查文件完整性，不代替签名。

## Trust / 签名

Windows builds are unsigned unless a trusted certificate is configured; SmartScreen or Smart App Control may still warn. See [Windows distribution](WINDOWS_TRUST.md). Current macOS packages lack Developer ID notarization; Gatekeeper may warn or block. Packaging tests do not establish OS reputation. / 本次未替发布者办理可信签名证书或 Apple 公证，不能保证系统不提示风险。
