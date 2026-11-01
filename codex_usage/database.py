"""Read a private copy of the Codex index without opening the original in SQLite."""
from __future__ import annotations

from pathlib import Path
import math
import re
import shutil
import sqlite3
import tempfile

from .safety import checked_local_path, inside


THREAD_COLUMNS = (
    'id', 'title', 'project_id', 'model', 'reasoning_effort', 'model_provider',
    'creator_account_id', 'creator_user_id', 'tokens_used', 'cli_version',
    'created_at', 'updated_at', 'created_at_ms', 'updated_at_ms', 'rollout_path',
    'cwd', 'archived', 'source', 'thread_source', 'agent_path', 'agent_role',
)
NUMERIC_COLUMNS = {'tokens_used', 'created_at', 'updated_at', 'created_at_ms', 'updated_at_ms', 'archived'}


def _text(value: object, limit: int = 5000) -> str | None:
    return value[:limit] if isinstance(value, str) else None


def _number(value: object) -> int | None:
    if isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(value) and value >= 0:
        return int(value)
    return None


def _fingerprint(paths: list[Path]) -> tuple:
    values = []
    for path in paths:
        checked_local_path(path)
        try:
            stat = path.stat()
            values.append((True, stat.st_size, stat.st_mtime_ns))
        except FileNotFoundError:
            values.append((False,))
    return tuple(values)


def _copy_snapshot(source: Path, destination: Path) -> bool:
    """Copy DB + WAL + SHM; retry if any file changes while being copied."""
    originals = [checked_local_path(Path(str(source) + suffix)) for suffix in ('', '-wal', '-shm')]
    copies = [checked_local_path(Path(str(destination) + suffix)) for suffix in ('', '-wal', '-shm')]
    for _ in range(3):
        before = _fingerprint(originals)
        for original, copy, fingerprint in zip(originals, copies, before):
            if copy.exists():
                copy.unlink()
            if fingerprint[0]:
                try:
                    # copyfile uses read-only source handles, unlike SQLite itself.
                    shutil.copyfile(original, copy)
                except FileNotFoundError:
                    pass
        if before == _fingerprint(originals) and destination.is_file():
            return True
    return False


def _columns(connection: sqlite3.Connection, table: str) -> set[str]:
    # Table names are internal constants, never interpolated from data.
    return {row[1] for row in connection.execute(f'PRAGMA table_info("{table}")')}


def scan_database(home: Path, scratch: Path) -> dict:
    """Return whitelisted index metadata; DB counters are never token summands.

    The index's creator account identifies the creator of a thread, not each
    later request's billing identity. Consumers must retain that distinction.
    """
    result = {'threads': {}, 'projects': [], 'sources': [], 'warnings': []}
    try:
        home = checked_local_path(home)
        scratch = checked_local_path(scratch)
        if inside(scratch, home) or inside(home, scratch):
            raise ValueError('数据库临时副本目录不能位于 Codex 数据目录内。')
        candidates = []
        if home.is_dir():
            for path in home.glob('state_*.sqlite'):
                match = re.fullmatch(r'state_(\d+)\.sqlite', path.name)
                if match:
                    candidates.append((int(match[1]), checked_local_path(path)))
        if not candidates:
            result['warnings'].append('未找到 state_*.sqlite：项目目录与会话创建者归属仅使用其他本地记录。')
            return result
        _, source = max(candidates, key=lambda entry: entry[0])
        for suffix, description in (
            ('', '会话索引：标题、项目、创建者账号及索引元数据；tokens_used 不加入 Token 汇总。'),
            ('-wal', 'SQLite 尚未检查点的记录；仅复制后与数据库副本一并读取。'),
            ('-shm', 'SQLite 共享内存索引；仅复制到临时目录，不直接连接原数据库。'),
        ):
            path = checked_local_path(Path(str(source) + suffix))
            result['sources'].append({'path': str(path), 'uri': path.as_uri(), 'kind': 'sqlite' if not suffix else 'sqlite-sidecar', 'description': description, 'exists': path.exists()})
        scratch.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(prefix='codex-index-', dir=scratch) as folder:
            copy = checked_local_path(Path(folder) / source.name)
            stable = _copy_snapshot(source, copy)
            if not stable:
                result['warnings'].append('会话索引正在更新：复制期间连续检测到变化，数据库元数据可能不完整；重新运行可刷新。')
            connection = sqlite3.connect(copy.as_uri() + '?mode=ro', uri=True, timeout=1)
            connection.row_factory = sqlite3.Row
            try:
                connection.execute('PRAGMA query_only=ON')
                available = _columns(connection, 'threads')
                columns = [name for name in THREAD_COLUMNS if name in available]
                if 'id' in columns:
                    selection = ','.join('"' + name + '"' for name in columns)
                    for row in connection.execute('SELECT ' + selection + ' FROM threads'):
                        record = {key: _number(value) if key in NUMERIC_COLUMNS else _text(value) for key, value in dict(row).items()}
                        if not record.get('id'):
                            result['warnings'].append('会话索引包含缺失或类型异常的 ID；该条索引已跳过。')
                            continue
                        # Preserve Codex's source column without overloading provenance.
                        record['thread_origin'] = record.pop('source', None)
                        record['source'] = {'path': str(source), 'uri': source.as_uri(), 'table': 'threads', 'key': record['id']}
                        result['threads'][record['id']] = record
                project_columns = _columns(connection, 'projects')
                root_columns = _columns(connection, 'project_roots')
                roots: dict[str, list[str]] = {}
                if {'project_id', 'path'} <= root_columns:
                    for row in connection.execute('SELECT project_id, path FROM project_roots'):
                        project_id, path = _text(row['project_id']), _text(row['path'])
                        if project_id and path:
                            roots.setdefault(project_id, []).append(path)
                if {'id', 'name'} <= project_columns:
                    for row in connection.execute('SELECT id, name FROM projects'):
                        project_id = _text(row['id'])
                        if project_id:
                            result['projects'].append({'id': project_id, 'name': _text(row['name']), 'roots': roots.get(project_id, []), 'source': {'path': str(source), 'uri': source.as_uri(), 'table': 'projects', 'key': project_id}})
            finally:
                connection.close()
        return result
    except (OSError, ValueError, sqlite3.Error) as error:
        result['warnings'].append('读取本地数据库索引失败（' + type(error).__name__ + '）；JSONL 用量统计仍可独立使用。')
        return result
