"""Offline end-to-end tests: only the external YouTube provider is replaced.

Use real Qt workers/signals, engine parsing, metadata editing, ffmpeg, and tags.
"""
import os
os.environ.setdefault('QT_QPA_PLATFORM', 'offscreen')
import shutil
import subprocess
import tempfile
import time
import unittest
from pathlib import Path
from unittest.mock import patch
from PyQt6.QtWidgets import QApplication
from mutagen import File
from tp_engine import yt_api
from tp_interface.app import MainWindow
from audio_fixtures import write_tone

URLS = ['https://youtube.com/watch?v=aaaaaaaaaaa', 'https://youtube.com/watch?v=bbbbbbbbbbb']
PLAYLIST_URL = 'https://youtube.com/playlist?list=PLoffline_fixture'


@unittest.skipUnless(shutil.which('ffmpeg'), 'ffmpeg required for end-to-end tests')
class EndToEndTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.folder = Path(self.tmp.name)
        wav = write_tone(self.folder / 'fixture.wav')
        self.fixture = self.folder / 'fixture.webm'
        subprocess.run(['ffmpeg', '-nostdin', '-v', 'error', '-i', str(wav),
                        '-c:a', 'libopus', str(self.fixture)], check=True, timeout=15)
        fixture = self.fixture
        class Stream:
            subtype = 'webm'
            def download(self, filename, output_path, skip_existing, timeout):
                target = Path(output_path) / filename
                shutil.copyfile(fixture, target)
                return str(target)
        class Query(list):
            def filter(self, **kwargs):
                if kwargs != {'only_audio': True}:
                    raise AssertionError('Expected audio-only stream selection')
                return self
            def order_by(self, field):
                if field != 'abr':
                    raise AssertionError('Expected bitrate selection')
                return self
            def desc(self):
                return self
            def first(self):
                return self[0]
        class Video:
            def __init__(self, url):
                index = URLS.index(url)
                self.title = ['Artist A - First song', 'Artist B - Second song'][index]
                self.author = ['Artist A', 'Artist B'][index]
                self.vid_info = {'videoDetails': {'author': self.author}}
                self.watch_url = url
                self.streams = Query([Stream()])
        class Playlist:
            def __init__(self, url):
                if url != PLAYLIST_URL:
                    raise AssertionError('Unexpected playlist URL')
                self.video_urls = URLS
        self.video_patch = patch.object(yt_api, 'YouTube', Video)
        self.playlist_patch = patch.object(yt_api, 'Playlist', Playlist)
        self.video_patch.start()
        self.playlist_patch.start()
        self.window = MainWindow()
        self.controller = self.window.ytSingleController
        self.destination = self.folder / 'output'
        self.destination.mkdir()
        self.window.ytDestinationInput.setText(str(self.destination))

    def tearDown(self):
        if not self.controller.threadpool.waitForDone(15000):
            self.fail("Workers did not stop; run_tests.py enforces the outer process deadline")
        self.app.processEvents()
        self.controller.metadataController.mdw.close()
        self.window.close()
        self.video_patch.stop()
        self.playlist_patch.stop()
        self.tmp.cleanup()

    def wait_until(self, predicate):
        deadline = time.monotonic() + 15
        while time.monotonic() < deadline:
            self.app.processEvents()
            if predicate():
                return
            time.sleep(.01)
        self.fail('Timed out: ' + self.window.debugConsole.toPlainText())

    def load(self, url):
        self.window.ytUrlInput.setText(url)
        self.wait_until(lambda: self.window.ytDownloadButton.isEnabled())

    def download(self):
        self.window.ytDownloadButton.click()
        self.assertFalse(self.window.ytDownloadButton.isEnabled())
        self.wait_until(lambda: self.window.ytDownloadButton.isEnabled())
        self.assertEqual(self.window.progressBar.value(), 100)
        self.assertEqual(self.controller.downloadState.n_download_failed, 0)
        self.assertEqual(self.controller.downloadState.n_conversions_failed, 0)

    def test_playlist_metadata_edit_download_conversion_and_tags(self):
        self.load(PLAYLIST_URL)
        self.assertEqual(len(self.controller.metadataController.mdPayloads), 2)
        self.assertEqual(self.window.ytTitleInput.text(), 'First song')
        self.window.ytEditMetadataButton.click()
        md = self.controller.metadataController.mdw
        self.assertEqual(md.mdNumberAudiosLabel.text(), '2 audios')
        row = md.mdColumn.itemAt(1).widget()
        row.titleInput.setText('Edited second song')
        md.mdApplyButton.click()
        self.download()
        outputs = sorted(self.destination.glob('*.m4a'))
        self.assertEqual([p.name for p in outputs],
                         ['Edited second song - Artist B.m4a', 'First song - Artist A.m4a'])
        for output in outputs:
            audio = File(output)
            self.assertGreater(audio.info.length, 0.1)
            self.assertEqual(audio.tags['\xa9nam'], [output.stem.split(' - ')[0]])
            self.assertEqual(audio.tags['\xa9ART'], [output.stem.split(' - ')[1]])
        self.assertEqual(list(self.destination.glob('*.webm')), [])
        self.assertIn('downloads: 2/2', self.window.debugConsole.toPlainText())

    def test_single_video_without_conversion_keeps_source(self):
        self.load(URLS[0])
        self.window.ytConversionSettings.setChecked(False)
        self.download()
        files = list(self.destination.iterdir())
        self.assertEqual([p.name for p in files], ['First song - Artist A.webm'])
        self.assertEqual(files[0].read_bytes(), self.fixture.read_bytes())

    def test_single_video_with_conversion_can_keep_original(self):
        self.load(URLS[0])
        self.window.ytConversionKeepOriginal.setChecked(False)
        self.download()
        self.assertEqual({p.suffix for p in self.destination.iterdir()}, {'.webm', '.m4a'})
