# Windows signing and reputation / Windows 签名与下载信誉

“Not commonly downloaded” is a SmartScreen reputation warning, separate from a confirmed malware detection. Microsoft assesses both publisher and file reputation. Even a validly signed new file can warn; EV certificates no longer grant an immediate bypass. See [Microsoft's developer guidance](https://learn.microsoft.com/windows/apps/package-and-deploy/smartscreen-reputation) and [signing options](https://learn.microsoft.com/windows/apps/package-and-deploy/code-signing-options).

截图中的“通常不会下载”是下载信誉提示。长期应使用真实、持续一致的可信发布者签名；通过微软商店分发的 MSIX 由商店签名。GitHub Release、ZIP、校验值、自签证书均不能保证免提示。

## Implemented / 已实现

- One-folder bundle with no UPX, obfuscation or single-file runtime extraction / 目录式打包，不加壳、不混淆、不使用单文件运行时自解压。
- Standard current-user Inno Setup installer: stable AppId, product/publisher/version metadata, HTTPS project links, uninstall support and no requested elevation / 标准安装器、固定标识、清晰版本信息、可卸载且无需提权。
- Consent before opening update downloads; no silent installer execution / 更新需确认，不静默执行安装器。
- Clean native builds, synthetic tests, standalone and Windows install/uninstall checks, complete assets and SHA-256 inventories / 干净原生构建、合成测试、完整发布附件与校验值。
- Optional Authenticode signing of the launcher, installer, temporary setup copies and uninstaller; SHA-256 and timestamp verification must pass / 支持签名与时间戳，验证失败阻止发布。

These do not promise a specific SmartScreen or antivirus verdict. The application never alters antivirus settings, exclusions, browser protections or download-origin metadata. / 不修改 Defender、防护排除列表、浏览器防护或下载来源标记。

## Configure trusted signing / 配置信任签名

In repository Settings → Secrets and variables → Actions:

| Secret / variable | Purpose / 用途 |
| --- | --- |
| `WINDOWS_CERTIFICATE_BASE64` (secret) | Trusted code-signing PFX with private key, Base64-encoded / 可信代码签名 PFX，支持现有可导出证书 |
| `WINDOWS_CERTIFICATE_PASSWORD` (secret) | PFX password / PFX 密码 |
| `REQUIRE_WINDOWS_SIGNING=true` (variable) | Refuse unsigned publication / 阻止无签名发布 |

Never commit keys or paste them into issues. The signing backend reads secrets from environment variables, creates a PFX only under the runner temporary directory, removes it in `finally`, and verifies signature plus timestamp. Credentials are never passed in process arguments or uploaded. For non-exportable hardware/cloud keys, replace this PFX backend with the provider's official integration. This is not an existing Azure Artifact Signing integration. / 新证书通常使用硬件或云端密钥，请按实际服务对接，不尝试导出不可导出密钥。

Without configured credentials, builds report **UNSIGNED**. Public trust requires verified publisher identity; a self-signed certificate cannot supply it. For false detections, the owner may submit the exact final public package to [Microsoft's software-developer portal](https://www.microsoft.com/wdsi/filesubmission). No packages are automatically uploaded to analysis services. / 如遇误报，发布者可向微软提交最终公开包复核，勿上传真实 Codex 数据。
