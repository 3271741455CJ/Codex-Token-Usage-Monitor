from pathlib import Path
import hashlib
import json
import sqlite3
import tempfile
import unittest

from codex_usage.database import scan_database


def fingerprint(folder):
    return {p.name: (p.stat().st_mtime_ns, hashlib.sha256(p.read_bytes()).hexdigest()) for p in folder.iterdir() if p.is_file()}


class DatabaseTests(unittest.TestCase):
    def test_reads_uncheckpointed_wal_without_changing_source(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            home = root / 'home'
            home.mkdir()
            db = home / 'state_5.sqlite'
            con = sqlite3.connect(db)
            try:
                con.execute('PRAGMA journal_mode=WAL')
                con.execute('PRAGMA wal_autocheckpoint=0')
                con.execute('CREATE TABLE threads (id TEXT, title TEXT, tokens_used INTEGER, creator_account_id TEXT, first_user_message TEXT, source TEXT)')
                con.execute('CREATE TABLE projects (id TEXT, name TEXT)')
                con.execute('CREATE TABLE project_roots (project_id TEXT, path TEXT)')
                con.commit()
                con.execute('PRAGMA wal_checkpoint(TRUNCATE)')
                con.execute('INSERT INTO threads VALUES (?,?,?,?,?,?)', ('thread-1', 'Useful title', 123, 'creator-a', 'SECRET MESSAGE MUST NOT ESCAPE', 'cli'))
                con.execute('INSERT INTO projects VALUES (?,?)', ('project-1', 'A project'))
                con.execute('INSERT INTO project_roots VALUES (?,?)', ('project-1', str(root / 'project')))
                con.commit()
                self.assertGreater(Path(str(db) + '-wal').stat().st_size, 0)
                before = fingerprint(home)
                result = scan_database(home, root / 'output' / '.scratch')
                self.assertEqual(result['warnings'], [])
                self.assertEqual(result['threads']['thread-1']['tokens_used'], 123)
                self.assertEqual(result['threads']['thread-1']['creator_account_id'], 'creator-a')
                self.assertEqual(result['threads']['thread-1']['thread_origin'], 'cli')
                self.assertNotIn('first_user_message', result['threads']['thread-1'])
                self.assertNotIn('SECRET MESSAGE', str(result))
                self.assertEqual(result['projects'][0]['roots'], [str(root / 'project')])
                self.assertEqual(before, fingerprint(home))
                self.assertEqual(list((root / 'output' / '.scratch').iterdir()), [])
            finally:
                con.close()

    def test_accepts_old_schema_and_chooses_highest_state_version(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            home = root / 'home'
            home.mkdir()
            for number in (2, 10):
                con = sqlite3.connect(home / f'state_{number}.sqlite')
                con.execute('CREATE TABLE threads (id TEXT, title TEXT)')
                con.execute('INSERT INTO threads VALUES (?,?)', (f'thread-{number}', 'title'))
                con.commit()
                con.close()
            result = scan_database(home, root / 'output' / '.scratch')
            self.assertEqual(set(result['threads']), {'thread-10'})
            self.assertEqual(result['projects'], [])
            self.assertEqual(result['warnings'], [])

    def test_rejects_scratch_under_source(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            result = scan_database(root, root / '.scratch')
            self.assertTrue(result['warnings'])
            self.assertFalse((root / '.scratch').exists())

    def test_missing_or_corrupt_database_is_reported(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            home = root / 'home'
            home.mkdir()
            self.assertTrue(scan_database(home, root / 'scratch')['warnings'])
            (home / 'state_5.sqlite').write_bytes(b'not a sqlite file')
            result = scan_database(home, root / 'scratch')
            self.assertEqual(result['threads'], {})
            self.assertTrue(result['warnings'])

    def test_sqlite_dynamic_types_cannot_break_json_or_become_fake_zeros(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            home = root / 'home'
            home.mkdir()
            con = sqlite3.connect(home / 'state_5.sqlite')
            con.execute('CREATE TABLE threads (id TEXT, title TEXT, tokens_used INTEGER, creator_account_id TEXT)')
            con.execute('INSERT INTO threads VALUES (?,?,?,?)', ('valid-id', b'PRIVATE-BLOB', float('inf'), b'INVALID-ACCOUNT'))
            con.execute('INSERT INTO threads VALUES (?,?,?,?)', (b'invalid-id', 'title', 4, 'account'))
            con.execute('CREATE TABLE projects (id TEXT, name TEXT)')
            con.execute('INSERT INTO projects VALUES (?,?)', ('project-id', b'INVALID-PROJECT-NAME'))
            con.commit()
            con.close()
            result = scan_database(home, root / 'scratch')
            self.assertEqual(set(result['threads']), {'valid-id'})
            self.assertIsNone(result['threads']['valid-id']['title'])
            self.assertIsNone(result['threads']['valid-id']['creator_account_id'])
            self.assertIsNone(result['threads']['valid-id']['tokens_used'])
            self.assertTrue(result['warnings'])
            encoded = json.dumps(result, allow_nan=False)
            self.assertNotIn('PRIVATE-BLOB', encoded)


if __name__ == '__main__':
    unittest.main()
