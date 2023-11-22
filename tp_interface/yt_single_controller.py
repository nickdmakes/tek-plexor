import sys
import traceback

from PyQt6 import QtGui
from PyQt6.QtCore import QRunnable, pyqtSlot, QObject, pyqtSignal, QThreadPool
from PyQt6.QtWidgets import QFileDialog

from tp_engine.yt_api import get_title, download_single_audio
from tp_conversion.converter import opus_to_m4a2
from tp_interface.app import MainWindow
from .debug_logger import DebugLogger


# contains a reference QmainWindow object for the main window of the application
class YtSingleController:
    def __init__(self, main_window: MainWindow):
        super().__init__()
        self.mw = main_window
        self.connectSignalsSlots()
        self.threadpool = QThreadPool()
        self.setupUi()
        self.debugLogger = DebugLogger(self.mw.debugConsole)

    def connectSignalsSlots(self):
        self.mw.singleDownloadButton.clicked.connect(self.singleDownloadButtonClicked)
        self.mw.singleUrlInput.textChanged.connect(self.singleUrlInputChanged)
        self.mw.singleBrowseButton.clicked.connect(self.singleBrowseDestinationButtonClicked)

    def setupUi(self):
        self.mw.singleUrlStatusIcon.setPixmap(QtGui.QPixmap("tp_interface/ui/icons/grey_checkmark.png"))

    def downloadStarted(self):
        self.mw.singleDownloadButton.setEnabled(False)
        self.mw.statusbar.showMessage("Download Started...")
        self.debugLogger.infoLog("\n-------- PROCESS STARTED: YouTube Single Download -------")
        self.mw.progressBar.setValue(5)

    def originalSongDownloadStarted(self):
        self.debugLogger.infoLog(f'fetching high quality audio from Youtube...')
        self.mw.progressBar.setValue(30)

    def originalSongDownloadFinished(self, filename):
        self.mw.statusbar.showMessage("Downloaded song from YouTube")
        self.debugLogger.successLog(f'downloaded {filename} from Youtube')
        self.mw.progressBar.setValue(50)

    def songConversionStarted(self):
        self.mw.statusbar.showMessage("Converting audio codecs...")
        self.debugLogger.infoLog(f'converting original codec to m4a...')
        self.mw.progressBar.setValue(70)

    def songConversionFinished(self, filename):
        self.debugLogger.successLog(f'successfully converted {filename} to m4a')
        self.mw.progressBar.setValue(90)

    def downloadFinished(self):
        self.mw.statusbar.showMessage("Download successful!")
        self.mw.singleDownloadButton.setEnabled(True)
        self.mw.progressBar.setValue(100)
        self.debugLogger.infoLog("-------- PROCESS COMPLETE: YouTube Single Download -------\n")

    def downloadError(self, error):
        self.debugLogger.errorLog(f"Error: {error[1]}")
        self.mw.statusbar.showMessage("Download failed!")
        self.mw.singleDownloadButton.setEnabled(True)
        self.mw.progressBar.setValue(0)

    def singleDownloadButtonClicked(self):
        worker = SingleDownloadWorker(self.singleDownload_fn)
        worker.signals.download_started.connect(self.downloadStarted)
        worker.signals.original_song_download_started.connect(self.originalSongDownloadStarted)
        worker.signals.original_song_download_finished.connect(self.originalSongDownloadFinished)
        worker.signals.song_conversion_started.connect(self.songConversionStarted)
        worker.signals.song_conversion_finished.connect(self.songConversionFinished)
        worker.signals.download_finished.connect(self.downloadFinished)
        worker.signals.download_error.connect(self.downloadError)
        self.threadpool.start(worker)

    def singleBrowseDestinationButtonClicked(self):
        directory = QFileDialog.getExistingDirectory(self.mw, "Select a Destination Folder")
        if directory:
            self.mw.singleDestinationInput.setText(directory)

    def singleDownload_fn(self, osdsc, osdf, scs, scf):
        title = self.mw.singleSongNameInput.text().strip().replace(" ", "_")
        osdsc.emit()
        out_path = self.mw.singleDestinationInput.text().strip()
        out_file = download_single_audio(url=self.mw.singleUrlInput.text(), out_path=f'{out_path}', file_name=f'{title}.opus')
        osdf.emit(f'{title}.opus')
        scs.emit()
        opus_to_m4a2(out_file, out_file.replace(".opus", ".m4a"), delete_in_file=True)
        scf.emit(f'{title}.m4a')

    def singleUrlInputChanged(self, text):
        """change the status icon to green if the url is valid. Also,
        if the title is found, split it and put the artist"""
        self.mw.singleUrlStatusIcon.setPixmap(QtGui.QPixmap("tp_interface/ui/icons/grey_checkmark.png"))
        if text == "":
            return
        try:
            title, artist = get_title(url=text)
            self.mw.singleSongNameInput.setText(title)
            self.mw.singleArtistInput.setText(artist)
            self.debugLogger.infoLog(f"Youtube title found: {title}")
            self.mw.singleUrlStatusIcon.setPixmap(QtGui.QPixmap("tp_interface/ui/icons/green_checkmark.png"))
        except Exception as e:
            self.mw.singleUrlStatusIcon.setPixmap(QtGui.QPixmap("tp_interface/ui/icons/red_x.png"))
            pass


class SingleDownloadWorkerSignals(QObject):
    """
    Defines the signals available from a running worker thread.
    """
    download_started = pyqtSignal()
    original_song_download_started = pyqtSignal()
    original_song_download_finished = pyqtSignal(str)
    song_conversion_started = pyqtSignal()
    song_conversion_finished = pyqtSignal(str)
    download_finished = pyqtSignal()
    download_error = pyqtSignal(tuple)


class SingleDownloadWorker(QRunnable):
    def __init__(self, fn, *args, **kwargs):
        super(SingleDownloadWorker, self).__init__()
        # Store constructor arguments (re-used for processing)
        self.fn = fn
        self.args = args
        self.kwargs = kwargs
        self.signals = SingleDownloadWorkerSignals()

        self.kwargs['osdsc'] = self.signals.original_song_download_started
        self.kwargs['osdf'] = self.signals.original_song_download_finished
        self.kwargs['scs'] = self.signals.song_conversion_started
        self.kwargs['scf'] = self.signals.song_conversion_finished

    @pyqtSlot()
    def run(self):
        # Retrieve args/kwargs here; and fire processing using them
        try:
            self.signals.download_started.emit()
            self.fn(
                *self.args, **self.kwargs
            )
        except Exception as e:
            traceback.print_exc()
            exctype, value = sys.exc_info()[:2]
            self.signals.download_error.emit((exctype, value, traceback.format_exc()))
        else:
            self.signals.download_finished.emit()
