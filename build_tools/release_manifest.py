"""Fail publication if any advertised native package is missing."""
import hashlib
from pathlib import Path

root = Path(__file__).resolve().parents[1]
version = (root/'VERSION').read_text().strip()
folder = root/'release'
for suffix in ('windows-x64-Setup.exe', 'windows-x64-portable.zip', 'macos-x64.dmg', 'macos-arm64.dmg',
               'linux-x64.deb', 'linux-x64.tar.gz', 'linux-arm64.deb', 'linux-arm64.tar.gz'):
    path = folder/f'Codex-Token-Usage-Monitor-{version}-{suffix}'
    if not path.is_file() or not path.stat().st_size:
        raise SystemExit(f'Missing release asset: {path.name}')
lines = [f'{hashlib.sha256(p.read_bytes()).hexdigest()}  {p.name}' for p in sorted(folder.iterdir())
         if p.is_file() and p.name != 'SHA256SUMS.txt']
(folder/'SHA256SUMS.txt').write_text('\n'.join(lines)+'\n')
print('All eight native packages verified; SHA256SUMS.txt generated.')
