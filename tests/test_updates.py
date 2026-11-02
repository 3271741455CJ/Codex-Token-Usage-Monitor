import copy
import io
from pathlib import Path
import subprocess
import sys
import threading
import time
import unittest
from unittest.mock import patch
from codex_usage import updates
from codex_usage.runtime import collector_command, default_output


def release(version='0.3.0'):
    return {'tag_name': 'v'+version, 'html_url': updates.RELEASES_URL+'/tag/v'+version,
            'draft': False, 'prerelease': False,
            'assets': [{'name': f'Codex-Token-Usage-Monitor-{version}-windows-x64-Setup.exe'}]}


class UpdateTests(unittest.TestCase):
    def test_numeric_comparison_and_stable_only(self):
        self.assertIsNotNone(updates.parse_release(release('0.10.0'), '0.9.0'))
        for value in ('0.1.0', '0.2.0', '0.3.0-rc.1', '00.3.0', '../../evil', '0.3'):
            self.assertIsNone(updates.parse_release(release(value), '0.2.0'))
        for field in ('draft', 'prerelease'):
            data = release(); data[field] = True
            self.assertIsNone(updates.parse_release(data, '0.2.0'))

    def test_trusted_release_url_and_platform_package(self):
        data = release()
        update = updates.parse_release(data, '0.2.0', 'windows-x64')
        self.assertTrue(update.package.endswith('windows-x64-Setup.exe'))
        self.assertEqual(update.url, data['html_url'])
        self.assertIsNone(updates.parse_release(data, '0.2.0', 'linux-arm64').package)
        for url in ('https://evil.invalid/', data['html_url']+'?private=1', data['html_url']+'/../../evil'):
            bad = copy.deepcopy(data); bad['html_url'] = url
            self.assertIsNone(updates.parse_release(bad, '0.2.0'))

    def test_decline_failure_and_acceptance(self):
        update = updates.parse_release(release(), '0.2.0')
        opened = []
        for found, consent in ((None, True), (update, False)):
            updates.startup_check('0.2.0', checker=lambda _: found, prompt=lambda *_: consent, opener=opened.append)
        self.assertEqual(opened, [])
        updates.startup_check('0.2.0', checker=lambda _: update, prompt=lambda *_: True, opener=opened.append)
        self.assertEqual(opened, [update.url])
        updates.startup_check('0.2.0', checker=lambda _: 1/0)
        self.assertIsNone(updates.find_update('0.2.0', fetcher=lambda: 1/0))

    def test_network_wait_has_bounded_deadline(self):
        event = threading.Event()
        start = time.monotonic()
        try:
            result = updates.find_update('0.2.0', fetcher=lambda: event.wait(10), timeout=0.03)
            self.assertIsNone(result)
            self.assertLess(time.monotonic()-start, 1)
        finally:
            event.set()

    def test_request_contains_no_private_context_or_proxies(self):
        class Response(io.BytesIO):
            status = 200
        class Opener:
            def open(self, request, timeout):
                self.request = request; self.timeout = timeout
                return Response(b'{}')
        opener = Opener()
        with patch('urllib.request.build_opener', return_value=opener) as build:
            self.assertEqual(updates.fetch_release(), {})
        self.assertEqual(build.call_args.args[0].proxies, {})
        self.assertEqual(opener.request.full_url, updates.API_URL)
        self.assertIsNone(opener.request.data)
        self.assertNotIn('Authorization', opener.request.headers)
        self.assertNotIn('Cookie', opener.request.headers)
        self.assertEqual(opener.timeout, 3)
        with self.assertRaises(ValueError):
            updates.NoRedirect().redirect_request(None)

    def test_worker_commands_never_prompt_or_recurse(self):
        with patch.object(sys, 'frozen', True, create=True):
            command = collector_command(Path('synthetic'), Path('output'), True)
        self.assertEqual(command[:2], [sys.executable, '--worker'])
        self.assertIn('--no-update-check', command)
        self.assertIn('--sync-official', command)
        self.assertNotIn('--serve', command)
        with patch.object(sys, 'frozen', False, create=True):
            command = collector_command(Path('synthetic'), Path('output'))
        self.assertIn('-I', command)
        self.assertIn('--no-update-check', command)

    def test_per_user_output_on_each_platform(self):
        for system in ('win32', 'darwin', 'linux'):
            with patch.object(sys, 'frozen', True, create=True), patch.object(sys, 'platform', system):
                out = default_output()
                self.assertEqual(out.name, 'reports')
                self.assertIn('Codex-Token-Usage-Monitor', out.parts)
                self.assertNotIn('_internal', out.parts)

    def test_cli_version_and_explicit_offline_start_do_not_check(self):
        import run
        with patch('codex_usage.updates.startup_check') as check, patch('sys.stdout', new_callable=io.StringIO):
            with self.assertRaises(SystemExit) as done:
                run.main(['--version'])
            self.assertEqual(done.exception.code, 0)
            with patch('sys.stderr', new_callable=io.StringIO):
                run.main(['--no-update-check', '--codex-home', 'nonexistent-synthetic-data', '--output', '.qa/offline-output'])
            run.main(['--show-api-key', '--codex-home', 'nonexistent-synthetic-data', '--output', '.qa/offline-output'])
            check.assert_not_called()
