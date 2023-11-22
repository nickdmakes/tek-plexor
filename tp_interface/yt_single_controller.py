import sys
import os
import traceback

from PyQt6 import QtGui
from PyQt6.QtCore import QRunnable, pyqtSlot, QObject, pyqtSignal, QThreadPool
from PyQt6.QtWidgets import QFileDialog

from tp_engine.yt_api import get_title, download_single_audio
from tp_conversion.converter import FileExistsException, convert_to_m4a
from tp_interface.app import MainWindow
from .debug_logger import DebugLogger


class SingleDownloadPayload:
    """Factory class for creating a snapshot payload for the single download worker"""
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

        self.url = main_window.singleUrlInput.text().strip()
        self.title = main_window.singleSongNameInput.text().strip()
        self.artist = main_window.singleArtistInput.text().strip()
        self.conversion_enabled = main_window.singleConversionSettings.isChecked()
        if main_window.singleCompressionRadioFlac.isChecked():
            self.compression = "FLAC"
        elif main_window.singleCompressionRadioM4a.isChecked():
            self.compression = "m4a"
        elif main_window.singleCompressionRadioMp3.isChecked():
            self.compression = "mp3"
        elif main_window.singleCompressionRadioMp4.isChecked():
            self.compression = "mp4"

        # If FLAC is selected, bitrate is ignored (set to 0)
        if self.compression == "FLAC":
            self.bitrate = 0
        else:
            dial_position = main_window.singleBitRateDial.value()
            self.bitrate = bit_rates[dial_position]

        self.delete_og = main_window.singleConversionKeepOriginal.isChecked()
        self.out_path = main_window.singleDestinationInput.text().strip()
        return self


# contains a reference QmainWindow object for the main window of the application
class YtSingleController:
    def __init__(self, main_window: MainWindow):
        super().__init__()
        self.mw = main_window
        self.connectSignalsSlots()
        self.threadpool = QThreadPool()
        self.setupUi()
        self.debugLogger = DebugLogger(self.mw.debugConsole)
        self.downloadPayload = SingleDownloadPayload()

    def connectSignalsSlots(self):
        self.mw.singleDownloadButton.clicked.connect(self.singleDownloadButtonClicked)
        self.mw.singleUrlInput.textChanged.connect(self.singleUrlInputChanged)
        self.mw.singleBrowseButton.clicked.connect(self.singleBrowseDestinationButtonClicked)
        self.mw.singleCompressionRadioFlac.clicked.connect(self.singleCompressionRadioToggled)
        self.mw.singleCompressionRadioM4a.clicked.connect(self.singleCompressionRadioToggled)
        self.mw.singleCompressionRadioMp3.clicked.connect(self.singleCompressionRadioToggled)
        self.mw.singleCompressionRadioMp4.clicked.connect(self.singleCompressionRadioToggled)
        self.mw.singleBitRateDial.valueChanged.connect(self.singleBitRateDialChanged)

    def setupUi(self):
        self.mw.singleUrlStatusIcon.setPixmap(QtGui.QPixmap("tp_interface/ui/icons/grey_checkmark.png"))

    def fieldsValid(self):
        fields_set = True
        if self.mw.singleUrlInput.text() == "":
            fields_set = False
        if self.mw.singleSongNameInput.text() == "":
            fields_set = False
        if self.mw.singleArtistInput.text() == "":
            fields_set = False
        if self.mw.singleDestinationInput.text() == "":
            fields_set = False
        return fields_set

    def singleCompressionRadioToggled(self):
        if self.mw.singleCompressionRadioFlac.isChecked():
            self.mw.singleBitRateSettings.setEnabled(False)
            self.mw.singleBitRateLabel.setText("FLAC")
        else:
            self.mw.singleBitRateSettings.setEnabled(True)
            self.mw.singleBitRateDial.valueChanged.emit(self.mw.singleBitRateDial.value())

    def singleBitRateDialChanged(self, value):
        bit_rates = [96, 128, 192, 256, 320]
        self.mw.singleBitRateLabel.setText(f"{bit_rates[value]} kbps")

    def singleConversionEnabledCheckBoxChanged(self, state):
        if state == 2:
            self.mw.singleConversionSettings.setEnabled(True)
        else:
            self.mw.singleConversionSettings.setEnabled(False)

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

    def songConversionFileExists(self, filenames):
        self.debugLogger.errorLog(f'File already exists: {filenames[0]}')
        self.debugLogger.errorLog(f'File renamed to {filenames[1]}')
        self.debugLogger.errorLog(f"Press 'Download' again to retry")
        self.mw.singleDownloadButton.setEnabled(True)
        self.mw.statusbar.showMessage("Download failed!")
        self.mw.progressBar.setValue(0)

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
        if not self.fieldsValid():
            self.debugLogger.errorLog("Error: One or more fields are empty")
            return

        payload = SingleDownloadPayload().makePayload(self.mw)

        worker = SingleDownloadWorker(self.singleDownload_fn, payload=payload)
        worker.signals.download_started.connect(self.downloadStarted)
        worker.signals.original_song_download_started.connect(self.originalSongDownloadStarted)
        worker.signals.original_song_download_finished.connect(self.originalSongDownloadFinished)
        worker.signals.song_conversion_started.connect(self.songConversionStarted)
        worker.signals.song_conversion_file_exists.connect(self.songConversionFileExists)
        worker.signals.song_conversion_finished.connect(self.songConversionFinished)
        worker.signals.download_finished.connect(self.downloadFinished)
        worker.signals.download_error.connect(self.downloadError)
        self.threadpool.start(worker)

    def singleBrowseDestinationButtonClicked(self):
        directory = QFileDialog.getExistingDirectory(self.mw, "Select a Destination Folder")
        if directory:
            self.mw.singleDestinationInput.setText(directory)

    def singleDownload_fn(self, osdsc, osdf, scs, scf, payload: SingleDownloadPayload):
        title = self.mw.singleSongNameInput.text().strip()
        artist = self.mw.singleArtistInput.text().strip()
        filename = f'{payload.title} - {payload.artist}'
        osdsc.emit()
        # download will add the correct extension to filename
        out_file, filename = download_single_audio(url=payload.url, out_path=payload.out_path,
                                                   filename=filename)
        osdf.emit(filename)
        if payload.conversion_enabled:
            scs.emit()
            convert_to_m4a(out_file, title, artist, delete_in_file=payload.delete_og)
            scf.emit(filename)

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
    song_conversion_file_exists = pyqtSignal(tuple)
    song_conversion_finished = pyqtSignal(str)
    download_finished = pyqtSignal()
    download_error = pyqtSignal(tuple)


class SingleDownloadWorker(QRunnable):
    def __init__(self, fn, payload: SingleDownloadPayload, *args, **kwargs):
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
