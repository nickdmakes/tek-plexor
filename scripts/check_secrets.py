"""Scan Git history and nonignored working-tree files without exposing values."""
import shutil
import subprocess
import tempfile
from pathlib import Path


def main():
    root = Path(__file__).resolve().parents[1]
    executable = shutil.which('gitleaks')
    if not executable:
        raise SystemExit('Install gitleaks before running this check')
    subprocess.run([executable, 'git', '--redact', '--no-banner', str(root)], check=True)
    listing = subprocess.run(['git', 'ls-files', '--cached', '--others', '--exclude-standard', '-z'],
                             cwd=root, check=True, capture_output=True).stdout
    with tempfile.TemporaryDirectory(prefix='tek-plexor-secret-scan-') as folder:
        snapshot = Path(folder)
        for name in set(listing.decode().split('\0')) - {''}:
            relative = Path(name)
            if relative.is_absolute() or '..' in relative.parts:
                raise SystemExit('Unsafe repository path in scan input')
            source = root / relative
            if source.is_symlink():
                raise SystemExit('Symlink must be reviewed before secret scanning: ' + name)
            if not source.is_file():
                continue  # A tracked file deleted in the working tree.
            target = snapshot / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(source, target)
        subprocess.run([executable, 'dir', '--redact', '--no-banner', str(snapshot)], check=True)


if __name__ == '__main__':
    main()
