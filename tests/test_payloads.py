import tempfile
import unittest
from pathlib import Path
from utils.Utils import YtDownloadPayload as DP


class PayloadTests(unittest.TestCase):
    def test_valid_directory_and_supported_settings(self):
        with tempfile.TemporaryDirectory() as folder:
            self.assertEqual(DP(out_path=folder).isValid(), (True, ''))

    def test_invalid_settings_give_actionable_reasons(self):
        for payload, message in [
            (DP(out_path=''), 'Destination field is empty'),
            (DP(out_path='/nonexistent/tek-plexor-folder'), 'Destination folder does not exist'),
        ]:
            valid, reason = payload.isValid()
            self.assertFalse(valid)
            self.assertIn(message, reason)
        with tempfile.TemporaryDirectory() as folder:
            for payload, message in [(DP(out_path=folder, compression='exe'), 'Invalid compression format'),
                                     (DP(out_path=folder, bitrate=999), 'Invalid bitrate')]:
                valid, reason = payload.isValid()
                self.assertFalse(valid)
                self.assertIn(message, reason)

    @unittest.expectedFailure
    def test_regular_file_is_rejected_pending_opt_007(self):
        """OPT-007: destination validator currently accepts a regular file."""
        with tempfile.TemporaryDirectory() as folder:
            target = Path(folder) / 'file'
            target.write_text('existing file')
            valid, _ = DP(out_path=str(target)).isValid()
            self.assertFalse(valid)
