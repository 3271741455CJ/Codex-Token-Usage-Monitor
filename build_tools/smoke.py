"""Exercise a real standalone guarded worker, using synthetic data only."""
import json
from pathlib import Path
import subprocess
import sys
import tempfile


def main():
    executable = str(Path(sys.argv[1]).resolve())
    with tempfile.TemporaryDirectory() as temp:
        root = Path(temp)
        home = root/'synthetic-codex'; home.mkdir()
        (home/'sessions').mkdir()
        source = home/'sessions'/'demo.jsonl'
        source.write_text(json.dumps({'type': 'session_meta', 'payload': {'id': 'SYNTHETIC-ID', 'cwd': '/SYNTHETIC-PRIVATE'}})+'\n')
        before = source.read_bytes(), source.stat().st_mtime_ns
        out = root/'reports'
        result = subprocess.run([executable, '--worker', '--codex-home', str(home), '--output', str(out),
                                 '--all-formats', '--json'], capture_output=True, timeout=120)
        if result.returncode:
            print('Standalone worker failed:', result.stdout.decode('utf-8', 'replace'), result.stderr.decode('utf-8', 'replace'))
            raise SystemExit(1)
        from codex_usage.exports import FILES
        for name in ('latest.html', 'usage.json', *FILES):
            assert (out/name).stat().st_size, name
        assert b'SYNTHETIC-PRIVATE' not in (out/'latest.html').read_bytes()
        assert (source.read_bytes(), source.stat().st_mtime_ns) == before
        print('Standalone worker: all nine formats generated; sources unchanged; private fields excluded.')


if __name__ == '__main__':
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    main()
