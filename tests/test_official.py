"""Synthetic official responses and child process; no account or network access."""
import io
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

from codex_usage.official import CONFIG, Rpc, SyncError, check_config, clean_limits, clean_usage, fetch_official, unavailable
from codex_usage.report import build_report, render_html


def config():
    result = {}
    for key, value in CONFIG.items():
        parts = key.split('.')
        target = result
        for part in parts[:-1]:
            target = target.setdefault(part, {})
        target[parts[-1]] = value
    return {'config': result}


class FakeRpc:
    calls = []
    fail_usage = False
    def __init__(self, process):
        pass
    def send(self, message):
        pass
    def call(self, method, params=None):
        self.calls.append(method)
        if method == 'config/read':
            return config()
        if method == 'account/login/start':
            return {'type': 'chatgptAuthTokens'}
        if method == 'account/usage/read':
            if self.fail_usage:
                raise SyncError('unsupported')
            return {'summary': {'lifetimeTokens': 900, 'access_token': 'PRIVATE-RESPONSE'}, 'dailyUsageBuckets': [{'startDate': '2026-10-20', 'tokens': 90}]}
        if method == 'account/rateLimits/read':
            return {'rateLimits': {'limitId': 'codex', 'primary': {'usedPercent': 20, 'windowDurationMins': 300}}}
        return {}


class FakeProcess:
    def __init__(self):
        self.stdin, self.stdout = io.BytesIO(), io.BytesIO()
        self.killed = False
    def poll(self):
        return None
    def kill(self):
        self.killed = True
    def wait(self):
        return 0


class OfficialTests(unittest.TestCase):
    def test_allowlist_and_unknown_values(self):
        summary, daily = clean_usage({'summary': {'lifetimeTokens': 123, 'peakDailyTokens': True, 'currentStreakDays': -1, 'longestStreakDays': float('inf'), 'accessToken': 'PRIVATE'}, 'dailyUsageBuckets': [{'startDate': '2026-10-20', 'tokens': None}]})
        self.assertEqual(summary['lifetimeTokens'], 123)
        self.assertIsNone(summary['peakDailyTokens'])
        self.assertIsNone(summary['currentStreakDays'])
        self.assertIsNone(summary['longestStreakDays'])
        self.assertIsNone(daily[0]['tokens'])
        self.assertNotIn('PRIVATE', json.dumps([summary, daily], allow_nan=False))
        self.assertIsNone(clean_usage({'summary': None})[1])
        self.assertEqual(clean_usage({'dailyUsageBuckets': []})[1], [])

    def test_daily_duplicates_dates_and_unsafe_integer(self):
        row = {'startDate': '2026-10-20', 'tokens': 4}
        self.assertEqual(len(clean_usage({'dailyUsageBuckets': [row, row]})[1]), 1)
        for rows in ([row, dict(row, tokens=5)], [dict(row, startDate='PRIVATE')], [dict(row, startDate='2026-02-30')]):
            with self.assertRaises(SyncError):
                clean_usage({'dailyUsageBuckets': rows})
        summary, _ = clean_usage({'summary': {'lifetimeTokens': 2**60}})
        self.assertIsNone(summary['lifetimeTokens'])

    def test_limit_map_wins_and_never_copies_arbitrary_text(self):
        raw = {'rateLimits': {'primary': {'usedPercent': 80}}, 'rateLimitsByLimitId': {'PRIVATE-ID': {'limitId': 'PRIVATE-ID', 'limitName': 'PRIVATE-NAME', 'primary': {'usedPercent': 20, 'resetsAt': None}, 'credits': {'balance': '3.50', 'hasCredits': False, 'accessToken': 'PRIVATE'}}}}
        limits = clean_limits(raw)
        self.assertEqual(len(limits), 1)
        self.assertEqual(limits[0]['primary']['usedPercent'], 20)
        self.assertEqual(limits[0]['credits']['balance'], 3.5)
        self.assertNotIn('PRIVATE', json.dumps(limits))

    def test_unsafe_effective_configuration_is_rejected(self):
        check_config(config())
        for key, value in [('cli_auth_credentials_store', 'file'), ('chatgpt_base_url', 'https://example.invalid'), ('mcp_servers', {'private': {}})]:
            changed = config()
            changed['config'][key] = value
            with self.assertRaises(SyncError):
                check_config(changed)
        with self.assertRaises(SyncError):
            check_config({})

    def test_sync_preserves_credentials_cleans_temp_and_handles_partial(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            home, output = root/'home', root/'reports'
            home.mkdir(); output.mkdir()
            auth = home/'auth.json'
            auth.write_text(json.dumps({'auth_mode': 'chatgpt', 'tokens': {'access_token': 'PRIVATE-ACCESS', 'refresh_token': 'PRIVATE-REFRESH', 'account_id': 'fixture-account'}}))
            before = auth.read_bytes(), auth.stat().st_mtime_ns
            for partial in (False, True):
                FakeRpc.calls = []
                process = FakeProcess()
                plan = {'cwd': str(output/'.official-fixture')}
                with patch('codex_usage.official.Rpc', FakeRpc), patch.object(FakeRpc, 'fail_usage', partial):
                    result = fetch_official(home, output, plan, lambda: process, expected_account='fixture-account')
                self.assertEqual(result['status'], 'partial' if partial else 'ok')
                self.assertEqual(result['limits_status'], 'ok')
                self.assertEqual(before, (auth.read_bytes(), auth.stat().st_mtime_ns))
                self.assertEqual(list(output.iterdir()), [])
                self.assertTrue(process.killed)
                self.assertNotIn('PRIVATE', render_html({'official_usage': result}))
                self.assertEqual(FakeRpc.calls, ['initialize', 'config/read', 'account/login/start', 'account/usage/read', 'account/rateLimits/read'])
            with patch('codex_usage.official.Rpc', FakeRpc):
                result = fetch_official(home, output, plan, lambda: self.fail('must not launch'), expected_account='different')
            self.assertEqual(result['status'], 'account_changed')

    def test_rpc_discards_errors_and_refuses_refresh(self):
        class Process:
            stdin = io.BytesIO()
        for message, expected in [({'id': 1, 'error': {'code': -32601, 'message': 'PRIVATE-TOKEN'}}, 'unsupported'), ({'id': 9, 'method': 'account/chatgptAuthTokens/refresh', 'params': {'secret': 'PRIVATE'}}, 'login_required')]:
            process = Process()
            process.stdout = io.BytesIO((json.dumps(message)+'\n').encode())
            rpc = Rpc(process, timeout=.1)
            with self.assertRaises(SyncError) as error:
                rpc.call('account/usage/read')
            self.assertEqual(str(error.exception), expected)

    def test_official_totals_are_not_local_totals_and_offline_is_default(self):
        metadata = {'account': {}, 'configuration': {}, 'versions': {}}
        logs = {'sessions': [], 'turns': [{'id': 't', 'total_tokens': 10}]}
        with tempfile.TemporaryDirectory() as temp, patch('codex_usage.report.scan_metadata', return_value=metadata), patch('codex_usage.sessions.scan_sessions', return_value=logs), patch('codex_usage.database.scan_database', return_value={}):
            root = Path(temp)
            self.assertEqual(build_report(root, root/'out')['official_usage']['status'], 'offline')
            result = build_report(root, root/'out', official_reader=lambda _: dict(unavailable('ok'), summary={'lifetimeTokens': 900}))
            self.assertEqual(result['totals']['total_tokens'], 10)
            self.assertEqual(result['official_usage']['summary']['lifetimeTokens'], 900)

    def test_one_shot_process_exception_keeps_parent_network_and_writes_blocked(self):
        # Exercise real pipe creation and Windows audit command normalization,
        # with a synthetic Python child, never the real authenticated client.
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            output = root/'output'
            output.mkdir()
            code = r'''
import os, socket, sys
from pathlib import Path
from codex_usage.safety import install_guard
root=Path(sys.argv[1]); out=root/'output'
plan={'args':[sys.executable,'-I','-S','-B','-c','print("synthetic")'],'cwd':str(out),'env':{k:os.environ[k] for k in ('SystemRoot','WINDIR') if k in os.environ}}
launch=install_guard(out,official_launch=plan)
p=launch(); stdout,_=p.communicate(timeout=10)
assert stdout.strip()==b'synthetic'
for action in (launch, socket.socket, lambda:(root/'forbidden').write_text('bad')):
 try: action()
 except PermissionError: pass
 else: raise AssertionError('guard bypass')
print('PASS')
'''
            result = subprocess.run([sys.executable, '-B', '-c', code, str(root)], capture_output=True, text=True, cwd=Path(__file__).resolve().parents[1])
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(result.stdout.strip(), 'PASS')


if __name__ == '__main__':
    unittest.main()
