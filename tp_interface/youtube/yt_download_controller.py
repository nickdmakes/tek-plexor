from PyQt6 import QtGui
from PyQt6.QtCore import QThreadPool
from PyQt6.QtWidgets import QFileDialog

from tp_engine.yt_api import get_yt_info_from_link, download_single_audio, YTTitleRetrievalException
from tp_conversion.converter import convert_to_m4a
from tp_interface.app import MainWindow
from tp_interface.debug_logger import DebugLogger

from .yt_download_worker import YtDownloadWorker, YtDownloadPayload
from .yt_info_worker import YtInfoWorker


# contains a reference QmainWindow object for the main window of the application
class YtDownloadController:
    def __init__(self, main_window: MainWindow):
        super().__init__()
        self.mw = main_window
        self.connectSignalsSlots()
        self.threadpool = QThreadPool()
        self.setupUi()
        self.debugLogger = DebugLogger(self.mw.debugConsole)

    def connectSignalsSlots(self):
        self.mw.ytDownloadButton.clicked.connect(self.ytDownloadButtonClicked)
        self.mw.ytUrlInput.textChanged.connect(self.ytUrlInputChanged)
        self.mw.ytDestinationBrowseButton.clicked.connect(self.ytBrowseDestinationButtonClicked)
        self.mw.ytBitRateDial.valueChanged.connect(self.ytBitRateDialChanged)

    def setupUi(self):
        self.mw.ytUrlStatusIcon.setPixmap(QtGui.QPixmap("tp_interface/ui/icons/grey_checkmark.png"))

    def fieldsValid(self):
        fields_set = True
        if self.mw.ytUrlInput.text() == "":
            fields_set = False
        if self.mw.ytTitleInput.text() == "":
            fields_set = False
        if self.mw.ytArtistInput.text() == "":
            fields_set = False
        if self.mw.ytDestinationInput.text() == "":
            fields_set = False
        return fields_set

    def ytBitRateDialChanged(self, value):
        bit_rates = [96, 128, 192, 256, 320]
        self.mw.ytBitRateLabel.setText(f"{bit_rates[value]} kbps")

    def ytBrowseDestinationButtonClicked(self):
        directory = QFileDialog.getExistingDirectory(self.mw, "Select a Destination Folder")
        if directory:
            self.mw.ytDestinationInput.setText(directory)

    def ytDownloadButtonClicked(self):
        if not self.fieldsValid():
            self.debugLogger.errorLog("Error: One or more fields are empty")
            return
        payload = YtDownloadPayload().makePayload(self.mw)
        worker = YtDownloadWorker(self.ytDownload_fn, payload=payload)
        worker.signals.download_started.connect(self.downloadStarted)
        worker.signals.original_song_download_started.connect(self.originalSongDownloadStarted)
        worker.signals.original_song_download_finished.connect(self.originalSongDownloadFinished)
        worker.signals.song_conversion_started.connect(self.songConversionStarted)
        worker.signals.song_conversion_file_exists.connect(self.songConversionFileExists)
        worker.signals.song_conversion_finished.connect(self.songConversionFinished)
        worker.signals.download_finished.connect(self.downloadFinished)
        worker.signals.download_error.connect(self.downloadError)
        self.threadpool.start(worker)

    def ytDownload_fn(self, osdsc, osdf, scs, scf, payload: YtDownloadPayload):
        title = self.mw.ytTitleInput.text().strip()
        artist = self.mw.ytArtistInput.text().strip()
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

    def downloadStarted(self):
        self.mw.ytDownloadButton.setEnabled(False)
        self.mw.statusbar.showMessage("Download Started...")
        self.debugLogger.infoLog("\n-------- PROCESS STARTED: YouTube yt Download -------")
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
        self.mw.ytDownloadButton.setEnabled(True)
        self.mw.statusbar.showMessage("Download failed!")
        self.mw.progressBar.setValue(0)

    def songConversionFinished(self, filename):
        self.debugLogger.successLog(f'successfully converted {filename} to m4a')
        self.mw.progressBar.setValue(90)

    def downloadFinished(self):
        self.mw.statusbar.showMessage("Download successful!")
        self.mw.ytDownloadButton.setEnabled(True)
        self.mw.progressBar.setValue(100)
        self.debugLogger.infoLog("-------- PROCESS COMPLETE: YouTube yt Download -------\n")

    def downloadError(self, error):
        self.debugLogger.errorLog(f"Error: {error[1]}")
        self.mw.statusbar.showMessage("Download failed!")
        self.mw.ytDownloadButton.setEnabled(True)
        self.mw.progressBar.setValue(0)

    def ytUrlInputChanged(self, text: str):
        """change the status icon to green if the url is valid. Also,
        if the title is found, split it and put the artist"""
        self.mw.ytUrlStatusIcon.setPixmap(QtGui.QPixmap("tp_interface/ui/icons/grey_checkmark.png"))
        if text == "":
            return

        worker = YtInfoWorker(self.ytInfo_fn, url=text.strip())
        worker.signals.retrieval_started.connect(self.ytInfoRetrievalStarted)
        worker.signals.retrieval_result.connect(self.ytInfoRetrievalResult)
        worker.signals.retrieval_finished.connect(self.ytInfoRetrievalFinished)
        worker.signals.retrieval_error.connect(self.ytInfoRetrievalError)
        self.threadpool.start(worker)

    def ytInfo_fn(self, url):
        title, artist = get_yt_info_from_link(url=url)
        return title, artist

    def ytInfoRetrievalStarted(self):
        self.mw.ytUrlStatusIcon.setPixmap(QtGui.QPixmap("tp_interface/ui/icons/grey_checkmark.png"))

    def ytInfoRetrievalResult(self, info):
        title, artist = info
        self.mw.ytTitleInput.setText(title)
        self.mw.ytArtistInput.setText(artist)
        self.mw.ytUrlStatusIcon.setPixmap(QtGui.QPixmap("tp_interface/ui/icons/green_checkmark.png"))
        self.mw.statusbar.showMessage("YouTube video info retrieved")
        self.debugLogger.infoLog(f"Found metadata: {title} - {artist}")

    def ytInfoRetrievalFinished(self):
        pass

    def ytInfoRetrievalError(self, error):
        self.mw.ytUrlStatusIcon.setPixmap(QtGui.QPixmap("tp_interface/ui/icons/red_x.png"))
        self.mw.statusbar.clearMessage()