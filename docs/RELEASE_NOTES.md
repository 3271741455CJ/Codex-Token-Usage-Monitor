# v0.2.0 — 安装即用与启动更新检查

- 每次启动检查正式版本，发现更新先询问；确认后打开本仓库下载页。断网或拒绝更新可继续使用，支持 `--no-update-check` 与 `--version`。
- Windows 当前用户安装器及便携 ZIP；macOS Intel / Apple Silicon DMG；Linux x64 / ARM64 DEB 和 tar.gz。内置 Python、导出依赖和中文字体。
- 安装版报告保存在独立用户数据目录；升级及卸载保留报告，Codex 原文件保持只读。打开浏览器与后台采集适配桌面平台。
- 干净原生构建、合成数据测试、独立程序导出检查及 Windows 安装/卸载验证，附 SHA256SUMS.txt。
- Windows 使用无 UPX 的目录打包、清晰版本信息、无需提权的标准安装器，并支持可信签名与时间戳。

下载 `windows-x64-Setup.exe` / 对应 macOS 架构 `.dmg` / 对应 Linux 架构 `.deb`，GitHub 自动生成的 Source code 是源码，不是安装包。

**签名说明：未配置 Windows 可信签名证书时，包为未签名构建，仍可能出现 SmartScreen 提示。macOS 包未作 Developer ID 公证，可能受 Gatekeeper 限制。** 可信签名需要发布者身份验证，不能通过校验值或更换扩展名消除提示。详见 [Windows 分发说明](https://github.com/3271741455CJ/Codex-Token-Usage-Monitor/blob/main/docs/WINDOWS_TRUST.md)。

Windows 10/11 x64；macOS 13+；Linux x64 需 glibc 2.35+（Ubuntu 22.04+），ARM64 需 glibc 2.39+（Ubuntu 24.04+）。Android/iOS、32 位及 musl Linux 不支持。官方账号同步仍限 Windows 且需显式开启。独立项目，非 OpenAI 官方产品。

Startup update consent, bundled runtimes/fonts and native desktop packages. Confirmation opens this repository's release page; installation is manual. Sources remain read-only. Windows builds are unsigned until a trusted signing certificate is configured; macOS builds are not notarized. See [installation](https://github.com/3271741455CJ/Codex-Token-Usage-Monitor/blob/main/docs/INSTALLATION.md).
