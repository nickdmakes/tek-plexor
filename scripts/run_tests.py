"""Run the complete deterministic suite with coverage and a process-tree deadline."""
import sys
from process_checks import run_with_deadline


if __name__ == '__main__':
    raise SystemExit(run_with_deadline(
        [sys.executable, '-m', 'coverage', 'run', '-m', 'unittest', 'discover', '-s', 'tests', '-v'],
        timeout=180,
    ))
