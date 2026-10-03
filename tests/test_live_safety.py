import subprocess
import sys
import unittest
from pathlib import Path


class LiveSafetyTests(unittest.TestCase):
    def test_live_script_refuses_without_vpn_acknowledgment(self):
        script = Path(__file__).resolve().parents[1] / 'scripts/live_smoke.py'
        result = subprocess.run([sys.executable, str(script), '--playlist',
                                 'https://example.invalid/never-contact'],
                                capture_output=True, text=True, timeout=15)
        self.assertEqual(result.returncode, 2)
        self.assertIn('Live testing is disabled', result.stderr)
