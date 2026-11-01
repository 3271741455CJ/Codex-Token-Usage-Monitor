"""Public release metadata only; never reads Codex data or installs code."""
from dataclasses import dataclass
import json
import platform
import re
import sys
import threading
import urllib.request
import webbrowser
from pathlib import Path

REPOSITORY = '3271741455CJ/Codex-Token-Usage-Monitor'
RELEASES_URL = f'https://github.com/{REPOSITORY}/releases'
API_URL = f'https://api.github.com/repos/{REPOSITORY}/releases/latest'
MAX_BYTES = 512 * 1024


def version_tuple(value):
    if not isinstance(value, str) or not re.fullmatch(r'(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)', value):
        raise ValueError('invalid stable version')
    return tuple(map(int, value.split('.')))


def current_version():
    value = (Path(__file__).resolve().parents[1] / 'VERSION').read_text(encoding='utf-8').strip()
    version_tuple(value)
    return value


def platform_id():
    system = {'win32': 'windows', 'darwin': 'macos'}.get(sys.platform, 'linux' if sys.platform.startswith('linux') else '')
    arch = {'amd64': 'x64', 'x86_64': 'x64', 'arm64': 'arm64', 'aarch64': 'arm64'}.get(platform.machine().lower(), '')
    return f'{system}-{arch}' if system and arch else None


@dataclass(frozen=True)
class Update:
    version: str
    url: str
    package: str | None


def parse_release(data, installed, target=None):
    if not isinstance(data, dict) or data.get('draft') is not False or data.get('prerelease') is not False:
        return None
    tag = data.get('tag_name', '')
    if not isinstance(tag, str) or not tag.startswith('v'):
        return None
    try:
        if version_tuple(tag[1:]) <= version_tuple(installed):
            return None
    except ValueError:
        return None
    url = f'{RELEASES_URL}/tag/{tag}'
    if data.get('html_url') != url:
        return None
    suffix = {'windows-x64': 'windows-x64-Setup.exe', 'macos-x64': 'macos-x64.dmg',
              'macos-arm64': 'macos-arm64.dmg', 'linux-x64': 'linux-x64.deb',
              'linux-arm64': 'linux-arm64.deb'}.get(target or platform_id())
    name = f'Codex-Token-Usage-Monitor-{tag[1:]}-{suffix}' if suffix else None
    assets = data.get('assets')
    available = isinstance(assets, list) and any(isinstance(a, dict) and a.get('name') == name for a in assets)
    return Update(tag[1:], url, name if available else None)


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, *args, **kwargs):
        raise ValueError('release metadata redirects are not allowed')


def fetch_release():
    # No inherited proxies, cookies, authentication, local paths or identifiers.
    opener = urllib.request.build_opener(urllib.request.ProxyHandler({}), NoRedirect())
    request = urllib.request.Request(API_URL, headers={
        'Accept': 'application/vnd.github+json', 'User-Agent': 'Codex-Token-Usage-Monitor',
        'X-GitHub-Api-Version': '2022-11-28'})
    with opener.open(request, timeout=3) as response:
        if response.status != 200:
            return None
        payload = response.read(MAX_BYTES + 1)
        if len(payload) > MAX_BYTES:
            return None
        return json.loads(payload)


def find_update(installed, fetcher=None, timeout=4):
    result = []
    def worker():
        try:
            result.append(parse_release((fetcher or fetch_release)(), installed))
        except Exception:
            pass  # Fixed silence for offline, no release, rate limits or bad metadata.
    thread = threading.Thread(target=worker, daemon=True)
    thread.start()
    thread.join(timeout)
    return result[0] if result else None


def ask_update(installed, update):
    package = f'\n适用安装包：{update.package}' if update.package else '\n请在发布页选择适合本机的安装包。'
    message = (f'当前版本：{installed}\n发现新版本：{update.version}' + package +
               '\n\n是否打开 GitHub 发布页下载更新？\n安装前请退出本程序；报告数据会保留。选择“否”继续使用当前版本。')
    if sys.platform == 'win32':
        import ctypes
        # Default to No. No shell, automatic download, execution or elevation.
        return ctypes.windll.user32.MessageBoxW(None, message, 'Codex 用量查看器 · 发现更新', 0x124) == 6
    try:
        import tkinter as tk
        from tkinter import messagebox
        root = tk.Tk(); root.withdraw()
        try:
            return messagebox.askyesno('Codex 用量查看器 · 发现更新', message, default='no', parent=root)
        finally:
            root.destroy()
    except Exception:
        if sys.stdin is not None and sys.stdin.isatty():
            print(message)
            return input('打开下载页？[y/N] ').strip().lower() in ('y', 'yes')
        print(f'发现新版本 {update.version}；下载地址：{update.url}')
        return False


def startup_check(installed=None, *, checker=None, prompt=None, opener=None):
    try:
        installed = installed or current_version()
        update = (checker or find_update)(installed)
        if update and (prompt or ask_update)(installed, update):
            (opener or webbrowser.open)(update.url)
    except Exception:
        pass  # Update UI must never prevent local collection.
