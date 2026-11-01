# One-folder bundles; no UPX, obfuscation, self-extraction or elevation.
from pathlib import Path
import sys
root = Path(SPECPATH).parent
version = (root / 'VERSION').read_text().strip()
datas = [(str(root/'VERSION'), '.'), (str(root/'LICENSE'), 'licenses'),
         (str(root/'codex_usage/dashboard.html'), 'codex_usage'),
         (str(root/'codex_usage/live.js'), 'codex_usage'),
         (str(root/'codex_usage/assets/ReportSansSC.ttf'), 'codex_usage/assets'),
         (str(root/'build/OFL.txt'), 'licenses')]
from PyInstaller.utils.hooks import collect_data_files
for package in ('docx', 'reportlab'):
    datas += collect_data_files(package)
a = Analysis([str(root/'desktop.py')], pathex=[str(root)], binaries=[], datas=datas,
             hiddenimports=['tkinter', 'tkinter.messagebox', 'PIL._webp'],
             hookspath=[], runtime_hooks=[], excludes=['pytest', 'IPython', 'matplotlib', 'numpy'], noarchive=False)
pyz = PYZ(a.pure)
exe = EXE(pyz, a.scripts, [], exclude_binaries=True, name='Codex-Token-Usage-Monitor',
          debug=False, strip=False, upx=False, console=sys.platform != 'darwin',
          version=str(root/'build/windows-version.txt') if sys.platform == 'win32' else None,
          codesign_identity=None, entitlements_file=None)
coll = COLLECT(exe, a.binaries, a.datas, strip=False, upx=False, name='Codex-Token-Usage-Monitor')
if sys.platform == 'darwin':
    app = BUNDLE(coll, name='Codex Token Usage Monitor.app',
                 bundle_identifier='io.github.3271741455cj.codex-token-usage-monitor',
                 info_plist={'CFBundleShortVersionString': version, 'CFBundleVersion': version,
                             'NSHighResolutionCapable': True, 'LSMinimumSystemVersion': '13.0'})
