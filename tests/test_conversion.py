import shutil
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from mutagen import File
from tp_conversion import converter
from utils.Utils import YtDownloadPayload as DP, MetadataPayload as MP
from audio_fixtures import write_tone


@unittest.skipUnless(shutil.which('ffmpeg'), 'ffmpeg required for integration tests')
class ConversionTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.folder = Path(self.tmp.name)

    def tearDown(self):
        self.tmp.cleanup()

    def test_each_format_produces_readable_audio_with_metadata(self):
        for fmt in ('m4a', 'mp4', 'mp3', 'ogg'):
            with self.subTest(format=fmt):
                source = write_tone(self.folder / f'tone-{fmt}.wav')
                converter.convert(str(source), DP(compression=fmt).getPayload(),
                                  MP(title='Test song', artist='Test artist').getPayload())
                audio = File(source.with_suffix('.' + fmt))
                self.assertGreater(audio.info.length, 0.1)
                if fmt in ('m4a', 'mp4'):
                    self.assertEqual(audio.tags['\xa9nam'], ['Test song'])
                    self.assertEqual(audio.tags['\xa9ART'], ['Test artist'])
                elif fmt == 'mp3':
                    self.assertEqual(str(audio.tags['TIT2']), 'Test song')
                    self.assertEqual(str(audio.tags['TPE1']), 'Test artist')
                else:
                    self.assertEqual(audio.tags['title'], ['Test song'])
                    self.assertEqual(audio.tags['artist'], ['Test artist'])
                self.assertTrue(source.exists())

    def test_existing_output_and_input_are_unchanged(self):
        source = write_tone(self.folder / 'song.wav')
        original = source.read_bytes()
        output = source.with_suffix('.m4a')
        output.write_bytes(b'existing music')
        with self.assertRaises(converter.FileExistsException):
            converter.convert(str(source), DP(delete_og=True).getPayload(), MP().getPayload())
        self.assertEqual(output.read_bytes(), b'existing music')
        self.assertEqual(source.read_bytes(), original)

    def test_conversion_failure_preserves_source(self):
        source = self.folder / 'invalid.wav'
        source.write_bytes(b'not audio')
        with self.assertRaises(converter.AudioConversionException):
            converter.convert(str(source), DP(delete_og=True).getPayload(), MP().getPayload())
        self.assertEqual(source.read_bytes(), b'not audio')

    def test_successful_conversion_can_delete_source(self):
        source = write_tone(self.folder / 'song.wav')
        converter.convert(str(source), DP(delete_og=True).getPayload(), MP().getPayload())
        self.assertFalse(source.exists())
        self.assertGreater(File(source.with_suffix('.m4a')).info.length, 0)

    def test_tags_can_be_disabled(self):
        source = write_tone(self.folder / 'song.wav')
        payload = DP().getPayload()
        payload[DP.ADD_TAGS] = False
        converter.convert(str(source), payload, MP(title='Do not tag').getPayload())
        self.assertNotIn('\xa9nam', File(source.with_suffix('.m4a')).tags)

    def test_legacy_conversion_handles_shell_metacharacters_as_filename(self):
        source = write_tone(self.folder / 'track & metadata.wav')
        output = self.folder / 'output & metadata.m4a'
        converter.opus_to_m4a_cmd(str(source), str(output), delete_in_file=False)
        self.assertTrue(source.exists())
        self.assertGreater(File(output).info.length, 0)

    @unittest.expectedFailure
    def test_source_survives_tag_failure_pending_opt_001(self):
        """Known data-loss defect; OPT-001 tracks the production fix awaiting approval."""
        source = write_tone(self.folder / 'tag-failure.wav')
        with patch.object(converter, 'add_tags', side_effect=OSError('tagging failed')):
            with self.assertRaises(OSError):
                converter.convert(str(source), DP(delete_og=True).getPayload(), MP().getPayload())
        self.assertTrue(source.exists(), 'Source must survive until tags are saved')

    def test_legacy_helper_preserves_input_on_failure(self):
        source = self.folder / 'invalid.wav'
        source.write_bytes(b'not audio')
        with self.assertRaises(converter.AudioConversionException):
            converter.opus_to_m4a_cmd(str(source), str(self.folder / 'output.m4a'))
        self.assertTrue(source.exists())

    @unittest.expectedFailure
    def test_mono_ogg_at_default_bitrate_pending_opt_008(self):
        """OPT-008: Opus rejects 320 kbps for mono input."""
        source = write_tone(self.folder / 'mono.wav', channels=1)
        converter.convert(str(source), DP(compression='ogg').getPayload(), MP().getPayload())
        self.assertGreater(File(source.with_suffix('.ogg')).info.length, 0)
