import sys
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from process_checks import run_with_deadline


class ProcessDeadlineTests(unittest.TestCase):
    def test_success_and_failure_exit_codes_are_preserved(self):
        for status in (0, 3):
            with self.subTest(status=status):
                self.assertEqual(run_with_deadline([sys.executable, '-c', f'raise SystemExit({status})'], 5), status)

    def test_blocked_validation_process_is_terminated(self):
        import time
        started = time.monotonic()
        self.assertEqual(run_with_deadline([sys.executable, '-c', 'import time; time.sleep(60)'], .2), 124)
        self.assertLess(time.monotonic() - started, 8)
