import os
import io
from contextlib import redirect_stderr
os.environ.setdefault('QT_QPA_PLATFORM', 'offscreen')
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch
from PyQt6.QtWidgets import QApplication
from tp_engine import yt_api
from tp_interface.app import MainWindow
from tp_interface.youtube.yt_download_worker import YtDownloadWorker
from tp_conversion.converter import FileExistsException
from utils.Utils import YtDownloadPayload, MetadataPayload


class PlaylistTests(unittest.TestCase):
    def test_preserves_playlist_order(self):
        import time
        def retrieve(url):
            if url == 'first':
                time.sleep(0.05)
            return (url, 'artist', '', url)
        with patch.object(yt_api, 'get_playlist_video_info_fn', retrieve), patch.object(yt_api, 'as_completed', side_effect=lambda tasks: reversed(tasks)):
            self.assertEqual([v[0] for v in yt_api.get_playlist_videos(SimpleNamespace(video_urls=['first', 'second']))], ['first', 'second'])

    def test_playlist_works_on_single_core(self):
        with patch.object(yt_api, 'cpu_count', return_value=1), patch.object(yt_api, 'get_playlist_video_info_fn', return_value=('title', 'artist', '', 'url')):
            self.assertEqual(len(yt_api.get_playlist_videos(SimpleNamespace(video_urls=['url']))), 1)


class AppTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])

    def setUp(self):
        self.window = MainWindow()
        self.controller = self.window.ytSingleController
        self.tmp = tempfile.TemporaryDirectory()
        self.window.ytDestinationInput.setText(self.tmp.name)

    def tearDown(self):
        self.controller.threadpool.waitForDone()
        self.controller.metadataController.mdw.close()
        self.window.close()
        self.tmp.cleanup()

    def test_download_without_conversion_completes(self):
        self.window.ytConversionSettings.setChecked(False)
        self.controller.metadataController.yt_info_to_payload([('title', 'artist', 'url')])
        with patch('tp_interface.youtube.yt_download_controller.download_single_audio', return_value=('audio.webm', 'audio.webm')):
            self.controller.ytDownloadButtonClicked()
            self.controller.threadpool.waitForDone()
            self.app.processEvents()
        self.assertEqual(self.window.progressBar.value(), 100)
        self.assertTrue(self.window.ytDownloadButton.isEnabled())

    def test_retrieval_error_is_visible(self):
        self.controller.ytInfoRetrievalError((Exception, Exception('Playlist unavailable'), 'trace'))
        self.assertIn('Playlist unavailable', self.window.debugConsole.toPlainText())

    def test_existing_output_is_preserved(self):
        file = Path(self.tmp.name) / 'song.m4a'
        file.write_bytes(b'existing music')
        def fail(**kwargs):
            raise FileExistsException('File exists', file)
        worker = YtDownloadWorker(fail, {}, {})
        worker.run()
        self.assertTrue(file.exists())
        self.assertEqual(file.read_bytes(), b'existing music')

    def test_download_is_disabled_until_metadata_ready(self):
        self.assertFalse(self.window.ytDownloadButton.isEnabled())

    def test_old_retrieval_cannot_replace_current_url(self):
        from tp_engine.yt_api import YtInfoPayload
        with patch.object(self.controller.threadpool, 'start'):
            self.window.ytUrlInput.setText('https://youtube.com/watch?v=rxY0krufo1E')
            self.window.ytUrlInput.clear()
        self.controller.ytInfoRetrievalResult(YtInfoPayload([('old song', 'artist', 'old url')], False), request_id=1)
        self.assertEqual(self.controller.metadataController.mdPayloads, [])
        self.assertFalse(self.window.ytDownloadButton.isEnabled())

    def test_unexpected_download_failure_finishes_progress(self):
        self.controller.metadataController.yt_info_to_payload([('title', 'artist', 'url')])
        with redirect_stderr(io.StringIO()), patch('tp_interface.youtube.yt_download_controller.download_single_audio', side_effect=RuntimeError('Unexpected failure')):
            self.controller.ytDownloadButtonClicked()
            self.controller.threadpool.waitForDone()
            self.app.processEvents()
        self.assertEqual(self.window.progressBar.value(), 100)
        self.assertTrue(self.window.ytDownloadButton.isEnabled())
        self.assertIn('Unexpected failure', self.window.debugConsole.toPlainText())

class DownloadRetryTests(unittest.TestCase):
    def test_refreshes_stream_after_transient_forbidden_response(self):
        from urllib.error import HTTPError
        with tempfile.TemporaryDirectory() as folder:
            target = Path(folder) / 'song.webm'
            attempts = []
            class Stream:
                subtype = 'webm'
                def download(self, **kwargs):
                    attempts.append(1)
                    if len(attempts) == 1:
                        raise HTTPError('https://youtube.com', 403, 'Forbidden', {}, None)
                    target.write_bytes(b'audio fixture')
                    return str(target)
            stream = Stream()
            class Query(list):
                def first(self):
                    return self[0]
            streams = SimpleNamespace(filter=lambda **kw: SimpleNamespace(order_by=lambda k: SimpleNamespace(desc=lambda: Query([stream]))))
            with patch.object(yt_api, 'YouTube', return_value=SimpleNamespace(streams=streams)), patch.object(yt_api.time, 'sleep'):
                path, filename = yt_api.download_single_audio('url', 'song', folder)
            self.assertEqual(filename, 'song.webm')
            self.assertEqual(Path(path).read_bytes(), b'audio fixture')
