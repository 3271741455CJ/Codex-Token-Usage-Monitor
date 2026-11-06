# 安装 Codex Lens / Install Codex Lens

当前为 0.1.0 发布候选。发布资产按操作系统和处理器分别构建。请选择与设备匹配的包，并核对随包提供的 SHA-256。

| 系统 / System | 候选格式 / Package | 使用方式 / How to open |
| --- | --- | --- |
| Windows 10/11 x64 | Setup.exe 或 portable.zip | 每用户安装到开始菜单，或完整解压后运行 `Relay-Auditor.exe`。依赖系统已有 WebView2 Runtime。 |
| macOS Intel / Apple Silicon | x64 或 arm64 DMG | 打开磁盘镜像，把应用拖到 Applications，再从那里打开。构建目标为 macOS 13 或更新版本，实机兼容性待验证。当前候选未做 Apple 公证。 |
| Ubuntu 24.04 Linux x64 / arm64 | DEB 或 tar.gz | 用系统包管理器装 DEB，或解压后启动 `Relay-Auditor`。桌面需要 GTK 3 和 WebKitGTK 4.1。构建基线为 glibc 2.39。 |

可执行包包含 Python 与检测器。WebView2、WKWebView 或 WebKitGTK 由系统提供。所有平台都可从源码运行标准库 CLI。源码桌面端需先在隔离环境安装 [requirements-desktop.txt](../requirements-desktop.txt)。

Windows 提供目标专属的系统凭据保存。macOS 与 Linux 以当前会话保存 Key，重启后可在原目标贴入 Key 并点击开始。应用设置与匿名历史保存在各系统的用户数据目录。

The native build matrix covers Windows x64, Intel and Apple Silicon macOS, and x64 and ARM64 Ubuntu-family Linux. The [build process](RELEASING.md) describes which combinations still need native verification. Windows setup and portable packages use the system WebView2 runtime. The macOS app uses WKWebView. Linux uses system GTK 3 and WebKitGTK 4.1. The Windows vault is opt-in. Other platforms keep keys for the current session.

更多 Windows 操作见 [Windows 桌面说明](../WINDOWS.md)。
