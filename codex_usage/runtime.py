"""Paths and fixed worker commands for source and standalone distributions."""
import os
from pathlib import Path
import sys


def default_output():
    if not getattr(sys, 'frozen', False):
        return Path(__file__).resolve().parents[1] / '.reports'
    if sys.platform == 'win32':
        base = Path(os.environ.get('LOCALAPPDATA') or Path.home() / 'AppData' / 'Local')
    elif sys.platform == 'darwin':
        base = Path.home() / 'Library' / 'Application Support'
    else:
        base = Path(os.environ.get('XDG_DATA_HOME') or Path.home() / '.local' / 'share')
    return base / 'Codex-Token-Usage-Monitor' / 'reports'


def collector_command(home, folder, official=False):
    args = ['--codex-home', str(home), '--output', str(folder), '--all-formats', '--json', '--no-update-check']
    if official:
        args.append('--sync-official')
    if getattr(sys, 'frozen', False):
        return [sys.executable, '--worker', *args]
    return [sys.executable, '-I', '-B', str(Path(__file__).resolve().parents[1] / 'run.py'), *args]
