# 发布候选 / Release candidates

本项目的 `VERSION` 是安装包版本来源。0.1.0 是当前候选版本。GitHub 仓库归属、公开源码、构建产物上传、标签和正式 Release 均需维护者确认。

## 本机构建

在目标操作系统上使用隔离环境。

```text
python -m venv .venv
python -m pip install -r requirements-build.txt
python -B -m unittest discover -s tests -v
node tests/test_dashboard.cjs
python -B build_tools/build.py
```

创建虚拟环境后，先激活它或使用其中的 Python。Windows 安装器需要 Inno Setup 6。只验证 Windows 便携版可传入 `--portable-only`。macOS 用系统磁盘镜像工具，Linux 用发行版的包工具。PyInstaller 在产物的目标系统上运行。

## 审阅和发布

1. 用 `python -B build_tools/stage_source.py` 导出明确允许的源码、合成测试、文档和静态资源。审阅源码包和文件清单，确保只有公开内容。
2. 确认 GitHub 身份与目标 `owner/repository` 后，在批准的仓库运行 [原生构建流程](../.github/workflows/build-native.yml)。流程为手动触发，产物用于验证。
3. 检查各系统和架构的安装、启动、卸载及包哈希。记录实测平台、签名和公证状态。只有经确认的产物进入 Release。

The build workflow is manual and uses synthetic tests. It produces build artifacts. Publishing a GitHub Release is a separate maintainer action. PyInstaller requires a builder on each target operating system. [PyInstaller manual](https://pyinstaller.org/en/stable/index.html)
