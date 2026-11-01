from pathlib import Path
import base64
import copy
import json
import os
import sqlite3
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

from codex_usage.metadata import scan_metadata, safe_url
from codex_usage.safety import checked_local_path, validate_output
from codex_usage.privacy import protect_report
from codex_usage.report import render_html, write_report


class PrivacyTests(unittest.TestCase):
    def test_output_filter_removes_private_originals_without_changing_accounting(self):
        original = 'PRIVATE-ORIGINAL'
        source = {'path': 'C:/'+original+'/rollout.jsonl', 'uri': 'file:///C:/'+original,
                  'line': 12, 'kind': 'session', 'key': original, 'description': original}
        report = {
            'account': {'email': original+'@example.invalid', 'account_id': original,
                        'api_key_masked': original, 'name': original, 'access_token': original},
            'configuration': {'model': 'model-a', 'reasoning_effort': 'high', 'base_url': original,
                              'configured_providers': [{'id': original}], 'profile': original},
            'versions': {'desktop_path': original, 'desktop_version': '1.2.3', 'id': original},
            'totals': {'total_tokens': 120, 'input_tokens': 100, 'output_tokens': 20},
            'sessions': [{'id': original, 'title': original, 'project': original, 'project_id': original,
                          'project_name': original, 'creator_account_id': original, 'sources': [source['path']]}],
            'turns': [{'id': original, 'session_id': original, 'root_session_id': original,
                       'root_turn_id': original, 'project_id': original, 'title': original,
                       'project': original, 'project_name': original, 'source': source,
                       'usage_sources': [source], 'attribution': 'matched', 'total_tokens': 120,
                       'model_segments': [{'model': 'model-a', 'total_tokens': 120, 'unknown_private_field': original}]}],
            'projects': [{'id': original, 'name': original, 'total_tokens': 120}],
            'database_only_sessions': [{'id': original+'-db', 'title': original, 'rollout_path': original, 'source': source}],
            'sources': [source], 'warnings': ['无法读取：C:/'+original, '离线无法获取付款/发票、API 余额/费用。'],
            'rate_limits': [{'account_id': original, 'limit_id': original, 'limit_name': original,
                             'primary': {'used_percent': 20}, 'source': source}],
            'official_usage': {'status': 'ok', 'summary': {'lifetimeTokens': 500},
                               'daily': None, 'rate_limits': [{'label': 'Codex 共享额度', 'credits': {'balance': 0}}], 'raw_response': original},
            'unapproved_top_level': original,
        }
        before = copy.deepcopy(report)
        safe = protect_report(report)
        self.assertEqual(report, before)
        self.assertNotIn(original, json.dumps(safe))
        self.assertEqual(safe['totals'], report['totals'])
        self.assertEqual(safe['warnings'][1], report['warnings'][1])
        self.assertEqual(safe['official_usage']['summary'], {'lifetimeTokens': 500})
        self.assertIsNone(safe['official_usage']['daily'])
        self.assertEqual(safe['official_usage']['rate_limits'][0]['credits']['balance'], 0)
        turn = safe['turns'][0]
        self.assertEqual(turn['session_id'], safe['sessions'][0]['id'])
        self.assertEqual(turn['root_turn_id'], turn['id'])
        self.assertEqual(turn['project_id'], safe['projects'][0]['id'])
        self.assertEqual(turn['project_name'], safe['projects'][0]['name'])
        self.assertEqual(turn['source']['path'], safe['sources'][0]['path'])
        self.assertEqual(turn['source']['line'], 12)
        self.assertTrue(turn['source']['private_reference'])
        self.assertNotIn('uri', turn['source'])
        self.assertIn('本地', safe['account']['privacy_note'])
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory)
            write_report(report, output, export_json=True)
            for filename in ('latest.html', 'usage.json'):
                self.assertNotIn(original, (output/filename).read_text(encoding='utf-8'))
            self.assertEqual(json.loads((output/'usage.json').read_text(encoding='utf-8')), safe)
        self.assertNotIn(original, render_html(report))

    def test_aliases_preserve_root_links_and_distinct_groups(self):
        report = {'sessions': [
            {'id': 'parent', 'project': '/private/worktree', 'project_name': 'private name'},
            {'id': 'child', 'parent_thread_id': 'parent', 'root_session_id': 'parent', 'project': '/private/second'},
        ], 'turns': [
            {'id': 'same-id', 'session_id': 'parent', 'root_session_id': 'parent', 'root_turn_id': 'same-id', 'project': '/private/worktree'},
            {'id': 'same-id', 'session_id': 'child', 'root_session_id': 'parent', 'root_turn_id': 'same-id', 'project': '/private/second'},
        ], 'projects': [{'id': '/private/worktree', 'name': 'private name'}],
            'rate_limits': [{'account_id': 'first'}, {'account_id': 'second'}, {'account_id': 'first'}]}
        safe = protect_report(report)
        parent, child = safe['turns']
        self.assertNotEqual(parent['id'], child['id'])
        self.assertEqual(child['root_turn_id'], parent['id'])
        self.assertEqual(child['root_session_id'], parent['session_id'])
        self.assertEqual(safe['sessions'][1]['parent_thread_id'], safe['sessions'][0]['id'])
        self.assertNotEqual(parent['project'], child['project'])
        self.assertEqual(safe['sessions'][0]['project_name'], safe['projects'][0]['id'])
        self.assertNotEqual(safe['rate_limits'][0]['account_id'], safe['rate_limits'][1]['account_id'])
        self.assertEqual(safe['rate_limits'][0]['account_id'], safe['rate_limits'][2]['account_id'])

    def test_guard_blocks_network_processes_and_source_writes(self):
        # The audit hook cannot be removed; isolate it in a test Python process.
        # Socket/DNS attempts must fail at the audit event before any connection.
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            output = root / 'output'
            output.mkdir()
            protected = root / 'private.txt'
            protected.write_text('original', encoding='utf-8')
            os.link(protected, output / 'hardlinked.txt')
            db = root / 'original.sqlite'
            connection = sqlite3.connect(db)
            connection.execute('CREATE TABLE example (value TEXT)')
            connection.close()
            copied = output / 'copy.sqlite'
            copied.write_bytes(db.read_bytes())
            code = r'''
import json, os, socket, sqlite3, subprocess, sys
from pathlib import Path
from codex_usage.safety import install_guard
root=Path(sys.argv[1]); out=root/'output'; source=root/'private.txt'
install_guard(out)
blocked=[]
checks={
 'socket':lambda:socket.socket(),
 'dns':lambda:socket.getaddrinfo('offline-test.invalid',443),
 'process':lambda:subprocess.run([sys.executable,'-c','pass']),
 'write_source':lambda:source.write_text('bad'),
 'unlink_source':lambda:source.unlink(),
 'rename_source':lambda:source.rename(out/'stolen'),
 'hardlink_write':lambda:(out/'hardlinked.txt').write_text('bad'),
 'sqlite_source':lambda:sqlite3.connect((root/'original.sqlite').as_uri()+'?mode=ro',uri=True),
 'sqlite_write':lambda:sqlite3.connect(str(out/'forbidden.sqlite')),
 'unc':lambda:open(r'\\offline-test.invalid\share\file','rb'),
}
for label,check in checks.items():
 try: check()
 except (PermissionError,ValueError): blocked.append(label)
(out/'allowed.txt').write_text('allowed')
con=sqlite3.connect((out/'copy.sqlite').as_uri()+'?mode=ro',uri=True)
con.execute('SELECT * FROM example').fetchall(); con.close()
print(json.dumps({'blocked':blocked,'source':source.read_text(),'output':(out/'allowed.txt').read_text()}))
'''
            process = subprocess.run([sys.executable, '-B', '-c', code, str(root)], cwd=Path(__file__).resolve().parents[1], capture_output=True, text=True)
            self.assertEqual(process.returncode, 0, process.stderr)
            result = json.loads(process.stdout)
            self.assertEqual(set(result['blocked']), {'socket', 'dns', 'process', 'write_source', 'unlink_source', 'rename_source', 'hardlink_write', 'sqlite_source', 'sqlite_write', 'unc'})
            self.assertEqual(result['source'], 'original')
            self.assertEqual(result['output'], 'allowed')
            self.assertFalse((output / 'forbidden.sqlite').exists())

    def test_path_checks_reject_network_locations_and_protected_output(self):
        for value in (r'\\server\share\data', '//server/share/data', 'https://example.invalid/data'):
            with self.assertRaises(ValueError):
                checked_local_path(value)
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            with self.assertRaises(ValueError):
                validate_output(root / 'codex' / 'reports', root / 'codex')
            with self.assertRaises(ValueError):
                validate_output(root / 'installation' / 'reports', root / 'codex', [root / 'installation'])
            with self.assertRaises(ValueError):
                validate_output(root, root / 'codex')

    def test_credentials_and_url_auth_are_not_exported(self):
        with tempfile.TemporaryDirectory() as temporary:
            home = Path(temporary)
            claims = {'email': 'fixture@example.invalid', 'name': 'Fixture', 'secret_extra': 'UNAPPROVED-CLAIM', 'https://api.openai.com/auth': {'chatgpt_account_id': 'fixture-account', 'chatgpt_plan_type': 'test'}}
            payload = base64.urlsafe_b64encode(json.dumps(claims).encode()).decode().rstrip('=')
            jwt = 'HEADER.' + payload + '.SIGNATURE'
            (home / 'auth.json').write_text(json.dumps({'auth_mode': 'apikey', 'OPENAI_API_KEY': 'sk-PRIVATE-CREDENTIAL-001122', 'tokens': {'id_token': jwt, 'refresh_token': 'RAW-REFRESH-SECRET', 'access_token': 'RAW-ACCESS-SECRET'}}), encoding='utf-8')
            (home / 'config.toml').write_text('model_provider = "test"\n[model_providers.test]\nname = "Fixture Provider"\nbase_url = "https://username:PRIVATE-PASSWORD@example.invalid/v1?key=PRIVATE-QUERY#PRIVATE-FRAGMENT"\n', encoding='utf-8')
            with patch('codex_usage.metadata.read_versions', return_value={}):
                data = scan_metadata(home)
            serialized = json.dumps(data)
            for secret in ('sk-PRIVATE-CREDENTIAL-001122', 'RAW-REFRESH-SECRET', 'RAW-ACCESS-SECRET', jwt, 'UNAPPROVED-CLAIM', 'PRIVATE-PASSWORD', 'PRIVATE-QUERY', 'PRIVATE-FRAGMENT'):
                self.assertNotIn(secret, serialized)
            self.assertEqual(data['account']['email'], 'fixture@example.invalid')
            self.assertEqual(data['account']['base_url'], 'https://example.invalid/v1')
            self.assertTrue(data['account']['api_key_masked'].endswith('1122'))

    def test_malformed_url_does_not_leak_credentials(self):
        value = safe_url('https://username:PRIVATE@[invalid')
        self.assertNotIn('PRIVATE', value)

    def test_malformed_optional_metadata_is_ignored(self):
        cases = [
            'profile="test"\nprofiles=[]\n',
            'model_providers=[]\n',
            'model_provider=["invalid"]\n',
            'profile=["invalid"]\n',
        ]
        with tempfile.TemporaryDirectory() as temporary:
            home = Path(temporary)
            (home/'auth.json').write_text('{"tokens":[]}', encoding='utf-8')
            (home/'models_cache.json').write_text('{"models":null}', encoding='utf-8')
            for text in cases:
                with self.subTest(config=text):
                    (home/'config.toml').write_text(text, encoding='utf-8')
                    with patch('codex_usage.metadata.read_versions', return_value={}):
                        data = scan_metadata(home)
                    self.assertIsInstance(data['account'], dict)
                    self.assertEqual(data['model_catalog'], [])


if __name__ == '__main__':
    unittest.main()
