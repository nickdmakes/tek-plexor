import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock, patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import smoke_packaged


class PackagedSmokeTests(unittest.TestCase):
    def test_running_launcher_uses_tree_cleanup_without_inherited_pipe_wait(self):
        process = Mock()
        process.wait.side_effect = subprocess.TimeoutExpired('app', 10)
        with tempfile.NamedTemporaryFile() as executable:
            with patch.object(sys, 'argv', ['smoke_packaged.py', executable.name]), \
                 patch.object(smoke_packaged.subprocess, 'Popen', return_value=process) as spawn, \
                 patch.object(smoke_packaged, 'stop_process_tree') as stop:
                smoke_packaged.main()
        stop.assert_called_once_with(process)
        self.assertNotEqual(spawn.call_args.kwargs['stdout'], subprocess.PIPE)
        process.communicate.assert_not_called()

    def test_early_exit_still_fails_and_cleans_up(self):
        process = Mock()
        process.wait.return_value = 1
        with tempfile.NamedTemporaryFile() as executable:
            with patch.object(sys, 'argv', ['smoke_packaged.py', executable.name]), \
                 patch.object(smoke_packaged.subprocess, 'Popen', return_value=process), \
                 patch.object(smoke_packaged, 'stop_process_tree') as stop:
                with self.assertRaisesRegex(SystemExit, 'exited before startup'):
                    smoke_packaged.main()
        stop.assert_called_once_with(process)
