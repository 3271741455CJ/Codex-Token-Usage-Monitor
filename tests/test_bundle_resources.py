"""Packaged data may use internal links; user inputs and writes may not."""
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


class BundleResourceTests(unittest.TestCase):
    def test_internal_reads_external_links_and_writes(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary).resolve()
            resources = root/'App.app/Contents/Resources'; resources.mkdir(parents=True)
            frameworks = resources.with_name('Frameworks'); frameworks.mkdir()
            (resources/'template.txt').write_text('bundled fixture')
            (root/'source.txt').write_text('private fixture')
            output = root/'output'; output.mkdir()
            try:
                (frameworks/'template.txt').symlink_to(resources/'template.txt')
                (frameworks/'outside.txt').symlink_to(root/'source.txt')
            except OSError:
                self.skipTest('symlink privilege unavailable')
            code = r'''
import sys
from pathlib import Path
from codex_usage.safety import install_guard, checked_local_path
root = Path(sys.argv[1]); framework = root/'App.app/Contents/Frameworks'
sys.frozen = True; sys._MEIPASS = str(framework)
original_platform = sys.platform; sys.platform = 'darwin'
install_guard(root/'output')
sys.platform = original_platform
assert (framework/'template.txt').read_text() == 'bundled fixture'
for operation in (
    lambda: (framework/'outside.txt').read_text(),
    lambda: (framework/'template.txt').write_text('forbidden'),
    lambda: checked_local_path(framework/'template.txt'),
):
    try: operation()
    except (ValueError, PermissionError): pass
    else: raise AssertionError('bundle boundary bypass')
print('bundle boundary passed')
'''
            process = subprocess.run([sys.executable, '-B', '-c', code, str(root)],
                                     capture_output=True, text=True, cwd=Path(__file__).resolve().parents[1])
            self.assertEqual(process.returncode, 0, process.stderr)
            self.assertIn('bundle boundary passed', process.stdout)
            self.assertEqual((resources/'template.txt').read_text(), 'bundled fixture')
            self.assertEqual((root/'source.txt').read_text(), 'private fixture')
