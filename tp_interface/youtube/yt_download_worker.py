import os, sys, traceback
from PyQt6.QtCore import QObject, pyqtSignal, pyqtSlot, QRunnable
from tp_conversion.converter import FileExistsException

from ..app import MainWindow


class YtDownloadPayload:
    """Factory class for creating a snapshot payload for the YouTube download worker"""
    def __init__(self, url: str = "", title: str = "", artist: str = "", conversion_enabled: bool = True,
                 compression: str = "m4a", bitrate: int = 320, delete_og: bool = False, out_path: str = ""):
        super().__init__()
        self.url = url
        self.title = title
        self.artist = artist
        self.conversion_enabled = conversion_enabled
        self.compression = compression
        self.bitrate = bitrate
        self.delete_og = delete_og
        self.out_path = out_path

    def makePayload(self, main_window: MainWindow):
        bit_rates = [96, 128, 192, 256, 320]

        self.url = main_window.ytUrlInput.text().strip()
        self.title = main_window.ytTitleInput.text().strip()
        self.artist = main_window.ytArtistInput.text().strip()
        self.conversion_enabled = main_window.ytConversionSettings.isChecked()
        if main_window.ytCompressionRadioOgg.isChecked():
            self.compression = "OGG"
        elif main_window.ytCompressionRadioM4a.isChecked():
            self.compression = "m4a"
        elif main_window.ytCompressionRadioMp3.isChecked():
            self.compression = "mp3"
        elif main_window.ytCompressionRadioMp4.isChecked():
            self.compression = "mp4"

        # If FLAC is selected, bitrate is ignored (set to 0)
        dial_position = main_window.ytBitRateDial.value()
        self.bitrate = bit_rates[dial_position]

        self.delete_og = main_window.ytConversionKeepOriginal.isChecked()
        self.out_path = main_window.ytDestinationInput.text().strip()
        return self


class YtDownloadWorkerSignals(QObject):
    """
    Defines the signals available from a running worker thread.
    """
    download_started = pyqtSignal()
    original_song_download_started = pyqtSignal()
    original_song_download_finished = pyqtSignal(str)
    song_conversion_started = pyqtSignal()
    song_conversion_file_exists = pyqtSignal(tuple)
    song_conversion_finished = pyqtSignal(str)
    download_finished = pyqtSignal()
    download_error = pyqtSignal(tuple)


class YtDownloadWorker(QRunnable):
    def __init__(self, fn, payload: YtDownloadPayload, *args, **kwargs):
        super(YtDownloadWorker, self).__init__()
        # Store constructor arguments (re-used for processing)
        self.fn = fn
        self.args = args
        self.kwargs = kwargs
        self.signals = YtDownloadWorkerSignals()

        self.kwargs['osdsc'] = self.signals.original_song_download_started
        self.kwargs['osdf'] = self.signals.original_song_download_finished
        self.kwargs['scs'] = self.signals.song_conversion_started
        self.kwargs['scf'] = self.signals.song_conversion_finished
        self.kwargs['payload'] = payload

    @pyqtSlot()
    def run(self):
        # Retrieve args/kwargs here; and fire processing using them
        try:
            self.signals.download_started.emit()
            self.fn(
                *self.args, **self.kwargs
            )
        except FileExistsException as e:
            # rename file with .bak extension
            os.rename(e.filename, f'{e.filename}.bak')
            self.signals.song_conversion_file_exists.emit((e.filename, f'{e.filename}.bak'))
        except Exception as e:
            traceback.print_exc()
            exctype, value = sys.exc_info()[:2]
            self.signals.download_error.emit((exctype, value, traceback.format_exc()))
        else:
            self.signals.download_finished.emit()
