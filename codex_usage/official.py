"""Opt-in official app-server reads. Credentials travel only over private stdio.

No browser cookies, private HTTP endpoints, token refresh, model turns or raw
response logs. The offline collector remains independent of this adapter.
"""
from __future__ import annotations

from datetime import date, datetime, timezone
import json
import math
import os
from pathlib import Path
import queue
import re
import shutil
import threading
import time
import uuid

from .metadata import mapping, read_json
from .safety import checked_local_path, inside

MAX_BYTES = 2 * 1024 * 1024
SUMMARY = ('lifetimeTokens', 'peakDailyTokens', 'longestRunningTurnSec',
           'currentStreakDays', 'longestStreakDays')
CONFIG = {
    'cli_auth_credentials_store': 'ephemeral',
    'chatgpt_base_url': 'https://chatgpt.com/backend-api/',
    'model_provider': 'openai', 'check_for_update_on_startup': False,
    'analytics.enabled': False, 'otel.exporter': 'none',
    'otel.trace_exporter': 'none', 'otel.metrics_exporter': 'none',
    'otel.log_user_prompt': False, 'features.hooks': False,
}


class SyncError(Exception):
    """Contains only an internal status code, never server error messages."""


def unavailable(status='offline'):
    return {'status': status, 'fetched_at': None, 'summary': {},
            'daily': None, 'rate_limits': None, 'usage_status': status,
            'limits_status': status}


def numeric(value, *, integer=False):
    if (not isinstance(value, (int, float)) or isinstance(value, bool)
            or not 0 <= value <= 9007199254740991 or not math.isfinite(value)):
        return None
    if integer and int(value) != value:
        return None
    return int(value) if integer else value


def clean_usage(raw):
    raw = mapping(raw)
    if 'summary' not in raw and 'dailyUsageBuckets' not in raw:
        raise SyncError('unsupported')
    summary = {key: numeric(mapping(raw.get('summary')).get(key), integer=True) for key in SUMMARY}
    buckets = raw.get('dailyUsageBuckets')
    daily = None
    if isinstance(buckets, list):
        dates = {}
        for item in buckets:
            item = mapping(item)
            stamp = item.get('startDate')
            if not isinstance(stamp, str) or not re.fullmatch(r'\d{4}-\d{2}-\d{2}', stamp):
                raise SyncError('invalid_response')
            try:
                date.fromisoformat(stamp)
            except ValueError:
                raise SyncError('invalid_response') from None
            tokens = numeric(item.get('tokens'), integer=True)
            if stamp in dates and dates[stamp] != tokens:
                raise SyncError('invalid_response')
            dates[stamp] = tokens
        daily = [{'date': key, 'tokens': value} for key, value in sorted(dates.items())]
    return summary, daily


def clean_limits(raw):
    raw = mapping(raw)
    if 'rateLimitsByLimitId' not in raw and 'rateLimits' not in raw:
        raise SyncError('unsupported')
    buckets = raw.get('rateLimitsByLimitId')
    values = list(buckets.values()) if isinstance(buckets, dict) and buckets else [raw.get('rateLimits')]
    result = []
    for item in values:
        if not isinstance(item, dict):
            continue
        # Do not copy arbitrary names, IDs or server strings into the report.
        clean = {'label': '额度池 ' + str(len(result) + 1)}
        if item.get('limitId') == 'codex':
            clean['label'] = 'Codex 共享额度'
        for key in ('primary', 'secondary'):
            window = mapping(item.get(key))
            clean[key] = {field: numeric(window.get(field)) for field in ('usedPercent', 'windowDurationMins', 'resetsAt')} if window else None
        credits = mapping(item.get('credits'))
        balance = credits.get('balance')
        if isinstance(balance, str):
            try:
                balance = float(balance)
            except ValueError:
                balance = None
        clean['credits'] = {'balance': numeric(balance), **{
            key: credits.get(key) if isinstance(credits.get(key), bool) else None
            for key in ('hasCredits', 'unlimited')}}
        result.append(clean)
    return result or None


def make_launch(output: Path):
    """Only use the protected, installed Windows Store Codex package.

    Deliberately do not execute PATH wrappers or a configurable binary with
    account credentials. No installation or dependency download is attempted.
    """
    if os.name != 'nt':
        raise SyncError('client_unavailable')
    system_drive = Path(os.environ.get('SystemRoot', 'C:/Windows')).anchor
    apps = checked_local_path(Path(system_drive) / 'Program Files' / 'WindowsApps')
    candidates = []
    for path in apps.glob('OpenAI.Codex_*__2p2nqsd0c76g0/app/resources/codex.exe'):
        match = re.fullmatch(r'OpenAI\.Codex_(\d+(?:\.\d+){3})_[^_]+__2p2nqsd0c76g0', path.parents[2].name)
        if match:
            candidates.append((tuple(map(int, match[1].split('.'))), checked_local_path(path)))
    if not candidates:
        raise SyncError('client_unavailable')
    exe = max(candidates)[1]
    folder = checked_local_path(output / ('.official-' + uuid.uuid4().hex))
    args = [str(exe), 'app-server']
    for key, value in CONFIG.items():
        args += ['-c', key + '=' + json.dumps(value)]
    # No inherited API keys, endpoint/proxy overrides, tracing or plugin config.
    env = {key: os.environ[key] for key in ('SystemRoot', 'WINDIR', 'SystemDrive') if key in os.environ}
    env.update({key: str(folder) for key in ('CODEX_HOME', 'HOME', 'USERPROFILE', 'APPDATA', 'LOCALAPPDATA', 'TEMP', 'TMP')})
    env['RUST_LOG'] = 'off'
    return {'args': args, 'cwd': str(folder), 'env': env}


class Rpc:
    def __init__(self, process, timeout=20):
        self.process = process
        self.timeout = timeout
        self.messages = queue.Queue(maxsize=32)
        self.next_id = 0
        self.reader = threading.Thread(target=self._read, daemon=True)
        self.reader.start()

    def _read(self):
        try:
            while True:
                line = self.process.stdout.readline(MAX_BYTES + 1)
                if not line or len(line) > MAX_BYTES:
                    break
                value = json.loads(line)
                if isinstance(value, dict):
                    self.messages.put_nowait(value)
        except (OSError, ValueError, queue.Full):
            pass
        try:
            self.messages.put_nowait(None)
        except queue.Full:
            pass

    def send(self, message):
        payload = (json.dumps(message, separators=(',', ':')) + '\n').encode()
        if len(payload) > 64000:
            raise SyncError('invalid_response')
        errors = []
        def write():
            try:
                self.process.stdin.write(payload)
                self.process.stdin.flush()
            except OSError:
                errors.append(True)
        writer = threading.Thread(target=write, daemon=True)
        writer.start()
        writer.join(self.timeout)
        if writer.is_alive() or errors:
            raise SyncError('connection_failed')

    def call(self, method, params=None):
        self.next_id += 1
        request_id = self.next_id
        self.send({'id': request_id, 'method': method, 'params': params or {}})
        deadline = time.monotonic() + self.timeout
        while True:
            if time.monotonic() >= deadline:
                raise SyncError('timeout')
            try:
                item = self.messages.get(timeout=max(0, deadline - time.monotonic()))
            except queue.Empty:
                raise SyncError('timeout') from None
            if item is None:
                raise SyncError('connection_failed')
            if 'method' in item:
                if 'id' in item:
                    # Never refresh credentials, approve actions or execute tools.
                    self.send({'id': item['id'], 'error': {'code': -32601, 'message': 'Unsupported by usage reader'}})
                    if item['method'] == 'account/chatgptAuthTokens/refresh':
                        raise SyncError('login_required')
                continue
            if item.get('id') != request_id:
                continue
            if 'error' in item:
                code = mapping(item['error']).get('code')
                raise SyncError('unsupported' if code == -32601 else 'request_failed')
            if not isinstance(item.get('result'), dict):
                raise SyncError('invalid_response')
            return item['result']


def check_config(raw):
    config = mapping(raw.get('config'))
    for key, expected in CONFIG.items():
        value = config
        for part in key.split('.'):
            value = mapping(value).get(part)
        # Require proof of in-memory credentials and disabled telemetry before auth.
        if value != expected:
            raise SyncError('unsafe_configuration')
    if any(config.get(key) for key in ('mcp_servers', 'notify', 'hooks')):
        raise SyncError('unsafe_configuration')


def credentials(home):
    raw = read_json(home / 'auth.json')
    tokens = mapping(raw.get('tokens'))
    if raw.get('auth_mode') not in (None, 'chatgpt'):
        raise SyncError('login_required')
    token, account = tokens.get('access_token'), tokens.get('account_id')
    if not isinstance(token, str) or not 1 <= len(token) <= 16000 or not isinstance(account, str) or not 1 <= len(account) <= 256:
        raise SyncError('login_required')
    return token, account


def fetch_official(home, output, plan, launch, *, expected_account=None):
    result = unavailable('connection_failed')
    folder = checked_local_path(plan['cwd'])
    if not inside(folder, checked_local_path(output)) or folder == output:
        return unavailable('unsafe_configuration')
    process = None
    created = False
    try:
        token, account = credentials(home)
        if expected_account is not None and expected_account != account:
            raise SyncError('account_changed')
        folder.mkdir(mode=0o700)
        created = True
        process = launch()
        rpc = Rpc(process)
        rpc.call('initialize', {'clientInfo': {'name': 'codex_usage_check', 'version': '0.1.0'}, 'capabilities': {'experimentalApi': True}})
        rpc.send({'method': 'initialized', 'params': {}})
        check_config(rpc.call('config/read', {'includeLayers': False}))
        auth = rpc.call('account/login/start', {'type': 'chatgptAuthTokens', 'accessToken': token, 'chatgptAccountId': account})
        if auth.get('type') != 'chatgptAuthTokens':
            raise SyncError('login_required')
        result = unavailable('partial')
        for method, key in [('account/usage/read', 'usage'), ('account/rateLimits/read', 'limits')]:
            try:
                raw = rpc.call(method)
                if key == 'usage':
                    result['summary'], result['daily'] = clean_usage(raw)
                else:
                    result['rate_limits'] = clean_limits(raw)
                result[key + '_status'] = 'ok'
                result[key + '_fetched_at'] = datetime.now(timezone.utc).isoformat()
            except SyncError as error:
                result[key + '_status'] = str(error)
        # Discard the snapshot if the user's selected login changed mid-scan.
        if credentials(home)[1] != account:
            raise SyncError('account_changed')
        result['status'] = 'ok' if result['usage_status'] == result['limits_status'] == 'ok' else 'partial'
        result['fetched_at'] = datetime.now(timezone.utc).isoformat()
    except SyncError as error:
        result = unavailable(str(error))
    except (OSError, ValueError, RuntimeError):
        result = unavailable('connection_failed')
    finally:
        if process is not None:
            try:
                if process.poll() is None:
                    process.kill()
                process.wait()
            finally:
                for stream in (process.stdin, process.stdout):
                    try:
                        stream.close()
                    except OSError:
                        pass
        if created:
            try:
                checked_local_path(folder)
                shutil.rmtree(folder)
            except (OSError, ValueError):
                result['cleanup_warning'] = True
    return result
