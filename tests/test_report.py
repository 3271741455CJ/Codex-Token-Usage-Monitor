from pathlib import Path
import base64
import hashlib
import json
import re
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

from codex_usage.report import build_report, number, render_html


def scripts(html):
    return re.findall(r'<script\b[^>]*>(.*?)</script\s*>', html, re.I|re.S)


def fingerprints(root):
    return {str(p.relative_to(root)): (p.stat().st_mtime_ns, hashlib.sha256(p.read_bytes()).hexdigest()) for p in root.rglob('*') if p.is_file()}


class ReportTests(unittest.TestCase):
    def test_embedded_data_cannot_break_out_of_script_and_csp_matches(self):
        report = {'models': [{'model': '</script><script>globalThis.PRIVATE_EXECUTED=1</script><img src="https://offline-test.invalid/x">&\u2028\u2029__CSP__'}], 'title': 'PRIVATE-TITLE'}
        html = render_html(report)
        self.assertNotIn('<script>globalThis.PRIVATE_EXECUTED=1</script>', html)
        self.assertNotIn('<img src="https://offline-test.invalid/x">', html)
        payload = re.search(r'<script id="report-data" type="application/json">(.*?)</script>', html, re.S).group(1)
        self.assertEqual(json.loads(payload)['models'], report['models'])
        self.assertTrue(json.loads(payload)['privacy']['protected'])
        self.assertNotIn('PRIVATE-TITLE', html)
        policy = re.search(r'http-equiv="Content-Security-Policy" content="([^"]+)"', html).group(1)
        for body in scripts(html):
            digest = base64.b64encode(hashlib.sha256(body.encode('utf-8')).digest()).decode()
            self.assertIn("'sha256-"+digest+"'", policy)
        self.assertIn("connect-src 'none'", policy)
        self.assertIn("default-src 'none'", policy)
        self.assertIn("form-action 'none'", policy)
        self.assertNotRegex(policy, r"script-src[^;]*'unsafe-inline'")

    def test_invalid_numeric_values_do_not_break_aggregation(self):
        for value in (float('nan'), float('inf'), float('-inf'), -1, None, True, '123'):
            self.assertEqual(number(value), 0)
        self.assertEqual(number(123), 123)

    def test_source_uris_are_derived_from_local_paths(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            local = root/'session.jsonl'
            metadata = {'account': {}, 'configuration': {}, 'versions': {}, 'model_catalog': [], 'sources': [], 'warnings': []}
            logs = {'sessions': [{'id':'s', 'source':{'path':str(local),'uri':'https://offline-test.invalid/private'}}], 'turns': [], 'rate_limits': [], 'sources': [{'path':r'\\server\share\private.json','uri':'file://server/share/private.json'}], 'warnings': []}
            with patch('codex_usage.report.scan_metadata',return_value=metadata), patch('codex_usage.sessions.scan_sessions',return_value=logs), patch('codex_usage.database.scan_database',return_value={'threads':{},'projects':[],'sources':[],'warnings':[]}):
                report = build_report(root,root/'output')
            self.assertEqual(report['sources'], [])
            self.assertEqual(report['sessions'][0]['source']['uri'], local.as_uri())
            self.assertNotIn('https://offline-test.invalid', json.dumps(report))

    def test_cli_end_to_end_preserves_sources_and_keeps_secrets_out(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            home, output = root/'home', root/'output'
            (home/'sessions').mkdir(parents=True)
            (home/'auth.json').write_text('{"auth_mode":"apikey","OPENAI_API_KEY":"sk-PRIVATE-CLI-KEY-998877"}',encoding='utf-8')
            (home/'config.toml').write_text('model="gpt-fixture"\nmodel_reasoning_effort="high"\n',encoding='utf-8')
            rows = [
                {'type':'session_meta','timestamp':'2026-10-25T00:00:00Z','payload':{'id':'fixture-session','cwd':str(root/'project')}},
                {'type':'event_msg','timestamp':'2026-10-25T00:00:01Z','payload':{'type':'task_started','turn_id':'fixture-turn'}},
                {'type':'turn_context','timestamp':'2026-10-25T00:00:02Z','payload':{'turn_id':'fixture-turn','model':'gpt-fixture','effort':'high'}},
                {'type':'event_msg','timestamp':'2026-10-25T00:00:03Z','payload':{'type':'user_message','message':'PRIVATE-USER-MESSAGE-SENTINEL'}},
                {'type':'token_usage_record','timestamp':'2026-10-25T00:00:04Z','payload':{'thread_id':'fixture-session','turn_id':'fixture-turn','response_id':'fixture-response','usage':{'input_tokens':100,'cached_input_tokens':40,'output_tokens':10,'reasoning_output_tokens':5,'total_tokens':110}}},
            ]
            (home/'sessions'/'rollout.jsonl').write_text(''.join(json.dumps(row)+'\n' for row in rows),encoding='utf-8')
            before = fingerprints(home)
            repository = Path(__file__).resolve().parents[1]
            process = subprocess.run([sys.executable,'-B',str(repository/'run.py'),'--no-update-check','--codex-home',str(home),'--output',str(output),'--json'],cwd=repository,capture_output=True,text=True,encoding='utf-8',errors='replace')
            self.assertEqual(process.returncode,0,process.stderr)
            self.assertEqual(before,fingerprints(home))
            report=json.loads((output/'usage.json').read_text(encoding='utf-8'))
            self.assertEqual(report['totals']['total_tokens'],110)
            self.assertEqual(report['totals']['cached_input_tokens'],40)
            self.assertEqual(report['totals']['reasoning_output_tokens'],5)
            self.assertTrue(report['privacy']['protected'])
            self.assertNotIn(str(root), process.stdout + process.stderr)
            for file in (output/'usage.json',output/'latest.html'):
                content=file.read_text(encoding='utf-8')
                self.assertNotIn('sk-PRIVATE-CLI-KEY-998877',content)
                self.assertNotIn('PRIVATE-USER-MESSAGE-SENTINEL',content)
                for private in ('998877', 'fixture-session', 'fixture-turn', str(root).replace('\\', '\\\\')):
                    self.assertNotIn(private, content)

    def test_key_command_and_cli_errors_only_give_local_guidance(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            home = root/'PRIVATE-LOCAL-HOME'
            home.mkdir()
            (home/'auth.json').write_text('{"OPENAI_API_KEY":"sk-PRIVATE-KEY-END9876"}', encoding='utf-8')
            repository = Path(__file__).resolve().parents[1]
            command = [sys.executable, '-B', str(repository/'run.py'), '--no-update-check', '--codex-home', str(home), '--output', str(root/'out')]
            process = subprocess.run(command+['--show-api-key'], capture_output=True, text=True, encoding='utf-8')
            self.assertEqual(process.returncode, 0, process.stderr)
            self.assertIn('自行查看', process.stdout)
            for secret in ('PRIVATE-LOCAL-HOME', 'PRIVATE-KEY', 'END9876', '9876'):
                self.assertNotIn(secret, process.stdout + process.stderr)
            self.assertFalse((root/'out').exists())
            command[command.index('--codex-home')+1] = str(home/'PRIVATE-MISSING')
            process = subprocess.run(command, capture_output=True, text=True, encoding='utf-8')
            self.assertEqual(process.returncode, 1)
            self.assertNotIn('PRIVATE', process.stderr + process.stdout)


if __name__ == '__main__':
    unittest.main()
