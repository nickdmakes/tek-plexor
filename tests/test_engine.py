import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from urllib.error import HTTPError
from unittest.mock import patch
from tp_engine import yt_api


class InfoTests(unittest.TestCase):
    def test_title_artist_normalization(self):
        for title, author, fallback, expected in [
            (' Artist - Song ', 'Uploader', '', ('Song', 'Artist', 'url')),
            (' Song ', ' Artist ', '', ('Song', 'Artist', 'url')),
            ('Song', '', 'Fallback', ('Song', 'Fallback', 'url')),
            ('A - B - C', 'Uploader', '', ('A - B - C', 'Uploader', 'url')),
        ]:
            with self.subTest(title=title):
                self.assertEqual(yt_api.optimize_yt_info(title, author, fallback, 'url'), expected)

    def test_empty_playlist_returns_domain_error(self):
        with patch.object(yt_api, 'Playlist', return_value=SimpleNamespace(video_urls=[])):
            with self.assertRaisesRegex(yt_api.YTTitleRetrievalException, 'video urls'):
                yt_api.get_yt_info_from_link('https://youtube.com/playlist?list=PLempty')

    def test_missing_optional_video_details_does_not_break_retrieval(self):
        video = SimpleNamespace(title='Artist - Song', author='Artist', vid_info={}, watch_url='url')
        with patch.object(yt_api, 'YouTube', return_value=video):
            info = yt_api.get_yt_info_from_link('https://youtube.com/watch?v=aaaaaaaaaaa')
        self.assertFalse(info.is_playlist)
        self.assertEqual(info.info, [('Song', 'Artist', 'url')])

    def test_network_error_is_wrapped_for_ui(self):
        with patch.object(yt_api, 'YouTube', side_effect=OSError('connection failed')):
            with self.assertRaisesRegex(yt_api.YTTitleRetrievalException, 'connection failed'):
                yt_api.get_yt_info_from_link('https://youtube.com/watch?v=aaaaaaaaaaa')


class DownloadTests(unittest.TestCase):
    def video(self, stream):
        class Query(list):
            def first(self):
                return self[0] if self else None
        streams = SimpleNamespace(filter=lambda **kw: SimpleNamespace(
            order_by=lambda key: SimpleNamespace(desc=lambda: Query([] if stream is None else [stream]))))
        return SimpleNamespace(streams=streams)

    def test_permanent_http_error_is_not_retried(self):
        stream = SimpleNamespace(subtype='webm', download=lambda **kw: (_ for _ in ()).throw(
            HTTPError('https://youtube.com', 404, 'Not found', {}, None)))
        with patch.object(yt_api, 'YouTube', return_value=self.video(stream)) as factory:
            with self.assertRaises(yt_api.YTAudioDownloadException):
                yt_api.download_single_audio('url', 'song')
        self.assertEqual(factory.call_count, 1)

    def test_transient_http_errors_stop_after_three_attempts(self):
        stream = SimpleNamespace(subtype='webm', download=lambda **kw: (_ for _ in ()).throw(
            HTTPError('https://youtube.com', 503, 'Unavailable', {}, None)))
        with patch.object(yt_api, 'YouTube', return_value=self.video(stream)) as factory, patch.object(yt_api.time, 'sleep'):
            with self.assertRaises(yt_api.YTAudioDownloadException):
                yt_api.download_single_audio('url', 'song')
        self.assertEqual(factory.call_count, 3)

    def test_no_audio_stream_is_actionable_error(self):
        with patch.object(yt_api, 'YouTube', return_value=self.video(None)):
            with self.assertRaisesRegex(yt_api.YTAudioDownloadException, 'No audio stream'):
                yt_api.download_single_audio('url', 'song')

    def test_untrusted_filename_cannot_escape_destination(self):
        with tempfile.TemporaryDirectory() as folder:
            def download(filename, output_path, skip_existing, timeout):
                path = Path(output_path) / filename
                if path.parent != Path(folder) or timeout != 30:
                    raise AssertionError('Unsafe download boundary')
                path.write_bytes(b'audio')
                return str(path)
            stream = SimpleNamespace(subtype='webm', download=download)
            with patch.object(yt_api, 'YouTube', return_value=self.video(stream)):
                path, name = yt_api.download_single_audio('url', '../../outside/song', folder)
            self.assertEqual(Path(path).parent, Path(folder))
            self.assertNotIn('/', name)
            self.assertEqual(Path(path).read_bytes(), b'audio')
