import io
import os
os.environ.setdefault('QT_QPA_PLATFORM', 'offscreen')
from contextlib import redirect_stderr
import unittest
from PyQt6.QtWidgets import QApplication
from tp_engine.yt_api import YTAudioDownloadException, YTTitleRetrievalException, YtInfoPayload
from tp_conversion.converter import AudioConversionException, FileExistsException
from tp_interface.youtube.yt_download_worker import YtDownloadWorker
from tp_interface.youtube.yt_info_worker import YtInfoWorker


class WorkerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])

    def test_each_download_outcome_emits_finished_once(self):
        for exception, expected in [
            (None, 'result'),
            (YTAudioDownloadException('network'), 'original-error'),
            (AudioConversionException('codec'), 'conversion-error'),
            (FileExistsException('exists', 'song.m4a'), 'file-exists'),
            (RuntimeError('unexpected'), 'error'),
        ]:
            with self.subTest(exception=type(exception).__name__):
                def task(**kwargs):
                    if exception:
                        raise exception
                worker = YtDownloadWorker(task, {}, {})
                events = []
                worker.signals.download_started.connect(lambda: events.append('started'))
                worker.signals.download_result.connect(lambda: events.append('result'))
                worker.signals.original_song_download_error.connect(lambda _: events.append('original-error'))
                worker.signals.song_conversion_error.connect(lambda _: events.append('conversion-error'))
                worker.signals.song_conversion_file_exists_error.connect(lambda _: events.append('file-exists'))
                worker.signals.download_error.connect(lambda _: events.append('error'))
                worker.signals.download_finished.connect(lambda: events.append('finished'))
                with redirect_stderr(io.StringIO()):
                    worker.run()
                self.assertEqual(events, ['started', expected, 'finished'])

    def test_retrieval_success_returns_payload_then_finishes(self):
        expected = YtInfoPayload([('song', 'artist', 'url')], False)
        worker = YtInfoWorker(lambda url: expected, 'url')
        events = []
        worker.signals.retrieval_result.connect(lambda result: events.append(result.info))
        worker.signals.retrieval_finished.connect(lambda: events.append('finished'))
        worker.run()
        self.assertEqual(events, [[('song', 'artist', 'url')], 'finished'])

    def test_retrieval_failure_emits_error_and_finishes(self):
        def fail(url):
            raise YTTitleRetrievalException('unavailable')
        worker = YtInfoWorker(fail, 'url')
        events = []
        worker.signals.retrieval_error.connect(lambda error: events.append(str(error[1])))
        worker.signals.retrieval_finished.connect(lambda: events.append('finished'))
        with redirect_stderr(io.StringIO()):
            worker.run()
        self.assertEqual(events, ['unavailable', 'finished'])
