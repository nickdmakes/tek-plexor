import os, sys, traceback
from PyQt6.QtCore import QObject, pyqtSignal, pyqtSlot, QRunnable
from tp_conversion.converter import FileExistsException


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
    def __init__(self, fn, payload: dict, *args, **kwargs):
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
