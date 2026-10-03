"""Check that a packaged Qt executable starts outside the repository directory."""
import os
import subprocess
import sys
import tempfile
from pathlib import Path
from process_checks import stop_process_tree


def main():
    executable = Path(sys.argv[1]).resolve()
    if not executable.is_file():
        raise SystemExit('Packaged executable missing')
    environment = dict(os.environ, QT_QPA_PLATFORM='offscreen')
    with tempfile.TemporaryDirectory() as folder, tempfile.TemporaryFile() as output_file:
        process = subprocess.Popen([str(executable)], cwd=folder, env=environment,
                                   stdout=output_file, stderr=subprocess.STDOUT,
                                   start_new_session=os.name != 'nt',
                                   creationflags=subprocess.CREATE_NEW_PROCESS_GROUP if os.name == 'nt' else 0)
        try:
            try:
                process.wait(timeout=10)
            except subprocess.TimeoutExpired:
                print('Packaged app remained running for 10 seconds')
                return
            output_file.seek(0)
            raise SystemExit('Packaged app exited before startup check: ' +
                             output_file.read().decode(errors='replace'))
        finally:
            # PyInstaller's launcher has a child application. Kill the entire
            # tree before closing output; inherited pipes can otherwise hang
            # communicate() indefinitely on Windows.
            stop_process_tree(process)


if __name__ == '__main__':
    main()
