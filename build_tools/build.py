"""Native builds only. Downloads occur here on clean builders, never at runtime."""
import argparse
import hashlib
import importlib.metadata
import json
import os
from pathlib import Path
import platform
import shutil
import subprocess
import sys
import tarfile
import urllib.request

ROOT = Path(__file__).resolve().parents[1]
NAME = 'Codex-Token-Usage-Monitor'
FONT_BLOB = 'fb0637bafbcd804fe32152370a1225990745b4bc'
LICENSE_BLOB = '1c9f43281b8f216c5461fe9ac729afbade7724e4'


def run(*args):
    subprocess.run(list(map(str, args)), cwd=ROOT, check=True)


def download_blob(filename, blob):
    path = ROOT/'build'/filename
    def digest(data):
        return hashlib.sha1(f'blob {len(data)}\0'.encode()+data).hexdigest()
    if path.is_file() and digest(path.read_bytes()) == blob:
        return path
    url = f'https://api.github.com/repos/google/fonts/git/blobs/{blob}'
    headers = {'User-Agent': NAME, 'Accept': 'application/vnd.github.raw+json'}
    if os.environ.get('GH_TOKEN'):
        headers['Authorization'] = 'Bearer '+os.environ['GH_TOKEN']
    request = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(request, timeout=90) as response:
        data = response.read(30*1024*1024)
    if digest(data) != blob:
        raise ValueError('font source integrity check failed')
    path.write_bytes(data)
    return path


def prepare():
    (ROOT/'build').mkdir(exist_ok=True)
    source = download_blob('NotoSansSC.ttf', FONT_BLOB)
    download_blob('OFL.txt', LICENSE_BLOB)
    from fontTools.ttLib import TTFont
    from fontTools.varLib.instancer import instantiateVariableFont
    font = TTFont(source)
    instance = instantiateVariableFont(font, {'wght': 400}, inplace=True)
    for record in instance['name'].names:
        replacement = {1: 'Report Sans SC', 2: 'Regular', 3: 'ReportSansSC-Regular',
                       4: 'Report Sans SC Regular', 6: 'ReportSansSC-Regular',
                       16: 'Report Sans SC', 17: 'Regular'}.get(record.nameID)
        if replacement:
            record.string = replacement.encode(record.getEncoding())
    destination = ROOT/'codex_usage/assets/ReportSansSC.ttf'
    destination.parent.mkdir(exist_ok=True)
    instance.save(destination)
    version = (ROOT/'VERSION').read_text().strip()
    parts = tuple(map(int, version.split('.'))) + (0,)
    text = f'''VSVersionInfo(ffi=FixedFileInfo(filevers={parts!r}, prodvers={parts!r},
    mask=0x3f, flags=0, OS=0x40004, fileType=1, subtype=0, date=(0,0)),
    kids=[StringFileInfo([StringTable('040904B0', [
        StringStruct('CompanyName', 'Codex Token Usage Monitor contributors'),
        StringStruct('FileDescription', 'Codex Token Usage Monitor'),
        StringStruct('FileVersion', '{version}'),
        StringStruct('ProductName', 'Codex Token Usage Monitor'),
        StringStruct('ProductVersion', '{version}'),
        StringStruct('OriginalFilename', '{NAME}.exe'),
        StringStruct('LegalCopyright', 'MIT License')])]),
        VarFileInfo([VarStruct('Translation', [1033,1200])])])'''
    (ROOT/'build/windows-version.txt').write_text(text, encoding='utf-8')


def copy_licenses(bundle):
    destination = bundle/'third-party-licenses'
    destination.mkdir(exist_ok=True)
    for name in ('python-docx', 'openpyxl', 'Pillow', 'reportlab', 'lxml', 'charset-normalizer', 'et-xmlfile', 'typing_extensions'):
        distribution = importlib.metadata.distribution(name)
        folder = destination/name; folder.mkdir(exist_ok=True)
        for item in distribution.files or []:
            if any(word in item.name.lower() for word in ('license', 'copying', 'notice')):
                original = distribution.locate_file(item)
                if original.is_file(): shutil.copy2(original, folder/item.name)
    shutil.copy2(ROOT/'build/OFL.txt', destination/'ReportSansSC-OFL.txt')
    python_license = Path(sys.base_prefix)/'LICENSE.txt'
    if python_license.is_file(): shutil.copy2(python_license, destination/'Python-LICENSE.txt')


def package_windows(bundle, stem, version):
    signed = bool(os.environ.get('WINDOWS_CERTIFICATE_BASE64'))
    signer = ROOT/'build_tools/sign-windows.ps1'
    if signed:
        run('pwsh', '-NoProfile', '-File', signer, '-Target', bundle/(NAME+'.exe'))
    elif os.environ.get('REQUIRE_WINDOWS_SIGNING') == 'true':
        raise RuntimeError('Release requires a trusted Windows signing certificate')
    compiler = shutil.which('ISCC') or r'C:\Program Files (x86)\Inno Setup 6\ISCC.exe'
    command = [compiler, f'/DAppVersion={version}']
    if signed:
        command += ['/DSigningEnabled=1', f'/Srelease_sign=pwsh -NoProfile -File $q{signer}$q -Target $f']
    run(*command, ROOT/'build_tools/windows.iss')
    shutil.make_archive(str(ROOT/'release'/f'{stem}-portable'), 'zip', root_dir=bundle.parent, base_dir=bundle.name)
    print('Windows signing:', 'trusted signature and timestamp verified' if signed else 'UNSIGNED; SmartScreen warnings remain possible')


def package_macos(stem):
    stage = ROOT/'build/dmg'; stage.mkdir(exist_ok=True)
    app = ROOT/'dist/Codex Token Usage Monitor.app'
    shutil.copytree(app, stage/app.name, symlinks=True, dirs_exist_ok=True)
    (stage/'Applications').symlink_to('/Applications', target_is_directory=True)
    run('hdiutil', 'create', '-volname', 'Codex Token Usage Monitor', '-srcfolder', stage,
        '-ov', '-format', 'UDZO', ROOT/'release'/f'{stem}.dmg')


def package_linux(bundle, stem, version, arch):
    with tarfile.open(ROOT/'release'/f'{stem}.tar.gz', 'w:gz') as archive:
        archive.add(bundle, arcname=NAME)
    stage = ROOT/'build/deb'; stage.mkdir(exist_ok=True)
    opt = stage/'opt'/NAME
    shutil.copytree(bundle, opt, dirs_exist_ok=True)
    applications = stage/'usr/share/applications'; applications.mkdir(parents=True, exist_ok=True)
    (applications/f'{NAME}.desktop').write_text(f'''[Desktop Entry]
Type=Application
Name=Codex Token Usage Monitor
Comment=Local Codex usage dashboard
Exec=/opt/{NAME}/{NAME}
Terminal=true
Categories=Utility;
''')
    control = stage/'DEBIAN'; control.mkdir(exist_ok=True)
    baseline = '2.35' if arch == 'x64' else '2.39'
    (control/'control').write_text(f'''Package: codex-token-usage-monitor
Version: {version}
Section: utils
Priority: optional
Architecture: {'amd64' if arch == 'x64' else 'arm64'}
Maintainer: Codex Token Usage Monitor contributors <noreply@users.noreply.github.com>
Depends: libc6 (>= {baseline}), libx11-6, libfontconfig1, libfreetype6
Homepage: https://github.com/3271741455CJ/Codex-Token-Usage-Monitor
Description: Local read-only Codex usage dashboard with document exports
''')
    run('dpkg-deb', '--build', '--root-owner-group', stage, ROOT/'release'/f'{stem}.deb')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--prepare-only', action='store_true')
    parser.add_argument('--bundle-only', action='store_true')
    args = parser.parse_args()
    prepare()
    if args.prepare_only: return
    run(sys.executable, '-m', 'PyInstaller', '--noconfirm', '--clean', ROOT/'build_tools/monitor.spec')
    bundle = ROOT/'dist'/NAME
    if sys.platform == 'darwin':
        bundle = ROOT/'dist/Codex Token Usage Monitor.app/Contents/MacOS'
    copy_licenses(bundle)
    executable = bundle/(NAME + ('.exe' if os.name == 'nt' else ''))
    run(sys.executable, ROOT/'build_tools/smoke.py', executable)
    if args.bundle_only: return
    version = (ROOT/'VERSION').read_text().strip()
    arch = {'x86_64': 'x64', 'amd64': 'x64', 'aarch64': 'arm64', 'arm64': 'arm64'}[platform.machine().lower()]
    system = {'win32': 'windows', 'darwin': 'macos'}.get(sys.platform, 'linux')
    stem = f'{NAME}-{version}-{system}-{arch}'
    (ROOT/'release').mkdir(exist_ok=True)
    if system == 'windows': package_windows(bundle, stem, version)
    elif system == 'macos': package_macos(stem)
    else: package_linux(bundle, stem, version, arch)


if __name__ == '__main__':
    main()
