"""Check that a packaged Qt executable starts outside the repository directory."""
import os
import subprocess
import sys
import tempfile
from pathlib import Path


def main():
    executable = Path(sys.argv[1]).resolve()
    if not executable.is_file():
        raise SystemExit('Packaged executable missing')
    environment = dict(os.environ, QT_QPA_PLATFORM='offscreen')
    with tempfile.TemporaryDirectory() as folder:
        process = subprocess.Popen([str(executable)], cwd=folder, env=environment,
                                   stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        try:
            try:
                output, _ = process.communicate(timeout=10)
            except subprocess.TimeoutExpired:
                print('Packaged app remained running for 10 seconds')
                return
            raise SystemExit('Packaged app exited before startup check: ' +
                             output.decode(errors='replace'))
        finally:
            if process.poll() is None:
                process.terminate()
                try:
                    process.communicate(timeout=10)
                except subprocess.TimeoutExpired:
                    process.kill()
                    process.communicate()


if __name__ == '__main__':
    main()
