import os
from PyQt6 import QtGui
from PyQt6.QtCore import QThreadPool
from PyQt6.QtWidgets import QFileDialog

from tp_engine.yt_api import get_yt_info_from_link, download_single_audio
from tp_conversion.converter import convert
from tp_interface.app import MainWindow
from tp_interface.debug_logger import DebugLogger
from tp_interface.shared.metadata.metadata_controller import MetadataController
from utils.Utils import YtDownloadPayload as pl

from .yt_download_worker import YtDownloadWorker
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
        self.metadataController = MetadataController(parent=self.mw, md_title=self.mw.ytTitleInput,
                                                     md_artist=self.mw.ytArtistInput)

    def connectSignalsSlots(self):
        self.mw.ytDownloadButton.clicked.connect(self.ytDownloadButtonClicked)
        self.mw.ytUrlInput.textChanged.connect(self.ytUrlInputChanged)
        self.mw.ytDestinationBrowseButton.clicked.connect(self.ytBrowseDestinationButtonClicked)
        self.mw.ytBitRateDial.valueChanged.connect(self.ytBitRateDialChanged)
        self.mw.ytEditMetadataButton.clicked.connect(self.ytEditMetadataButtonClicked)
        self.mw.ytTitleInput.textChanged.connect(self.ytTitleInputChanged)
        self.mw.ytArtistInput.textChanged.connect(self.ytArtistInputChanged)

    def setupUi(self):
        self.mw.ytUrlStatusIcon.setPixmap(QtGui.QPixmap("tp_interface/ui/icons/grey_checkmark.png"))

    def makePayload(self):
        compression = ""
        if self.mw.ytCompressionRadioOgg.isChecked():
            compression = pl.OGG
        elif self.mw.ytCompressionRadioM4a.isChecked():
            compression = pl.M4A
        elif self.mw.ytCompressionRadioMp4.isChecked():
            compression = pl.MP4
        elif self.mw.ytCompressionRadioMp3.isChecked():
            compression = pl.MP3
        
        bitrate = pl.BIT_RATES[self.mw.ytBitRateDial.value()]
        
        payload = pl(
            url=self.mw.ytUrlInput.text().strip(),
            title=self.mw.ytTitleInput.text().strip(),
            artist=self.mw.ytArtistInput.text().strip(),
            conversion_enabled=self.mw.ytConversionSettings.isChecked(),
            compression=compression,
            bitrate=bitrate,
            delete_og=self.mw.ytConversionKeepOriginal.isChecked(),
            out_path=self.mw.ytDestinationInput.text().strip()
        )
        return payload

    def ytTitleInputChanged(self, text: str):
        if not self.metadataController.mdPayloads:
            return
        self.metadataController.mdPayloads[0].title = text.strip()

    def ytArtistInputChanged(self, text: str):
        if not self.metadataController.mdPayloads:
            return
        self.metadataController.mdPayloads[0].artist = text.strip()

    def ytEditMetadataButtonClicked(self):
        self.metadataController.showMetadataWindow()

    def ytBitRateDialChanged(self, value):
        bit_rates = [96, 128, 192, 256, 320]
        self.mw.ytBitRateLabel.setText(f"{bit_rates[value]} kbps")

    def ytBrowseDestinationButtonClicked(self):
        directory = QFileDialog.getExistingDirectory(self.mw, "Select a Destination Folder")
        if directory:
            self.mw.ytDestinationInput.setText(directory)

    def ytDownloadButtonClicked(self):
        payload = self.makePayload()
        valid, reason = payload.isValid()
        if not valid:
            self.debugLogger.errorLog(f"Error: {reason}")
            return

        payload = payload.getPayload()
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

    def ytDownload_fn(self, osdsc, osdf, scs, scf, payload: dict):
        title = payload[pl.TITLE]
        artist = payload[pl.ARTIST]
        filename = f'{title} - {artist}'
        url = payload[pl.URL]
        out_path = payload[pl.OUT_PATH]
        osdsc.emit()
        # download will add the correct extension to filename
        out_file, filename = download_single_audio(url=url, out_path=out_path, filename=filename)
        osdf.emit(filename)
        if payload[pl.CONVERSION_ENABLED]:
            scs.emit()
            convert(out_file, payload)
            scf.emit(filename)

    def downloadStarted(self):
        self.mw.ytDownloadButton.setEnabled(False)
        self.mw.statusbar.showMessage("Download Started...")
        self.debugLogger.infoLog("\n-------- PROCESS STARTED: YouTube yt Download -------")
        self.mw.progressBar.setValue(5)

    def originalSongDownloadStarted(self):
        self.debugLogger.infoLog(f'Fetching high quality audio from Youtube...')
        self.mw.progressBar.setValue(30)

    def originalSongDownloadFinished(self, filename):
        self.mw.statusbar.showMessage("Downloaded song from YouTube")
        self.debugLogger.successLog(f'Downloaded {filename} from Youtube')
        self.mw.progressBar.setValue(50)

    def songConversionStarted(self):
        self.mw.statusbar.showMessage("Converting audio codecs...")
        self.debugLogger.infoLog(f'Converting original codec...')
        self.mw.progressBar.setValue(70)

    def songConversionFileExists(self, filenames):
        self.debugLogger.errorLog(f'File already exists: {filenames[0]}')
        self.debugLogger.errorLog(f'File renamed to {filenames[1]}')
        self.debugLogger.errorLog(f"Press Download again to retry")
        self.mw.ytDownloadButton.setEnabled(True)
        self.mw.statusbar.showMessage("Download failed!")
        self.mw.progressBar.setValue(0)

    def songConversionFinished(self, filename):
        self.debugLogger.successLog(f'Successfully converted {filename}')
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
            self.mw.ytEditMetadataButton.setEnabled(False)
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
        self.metadataController.yt_info_to_payload(yt_info=[info])
        self.mw.ytEditMetadataButton.setEnabled(True)

    def ytInfoRetrievalFinished(self):
        pass

    def ytInfoRetrievalError(self, error):
        self.mw.ytUrlStatusIcon.setPixmap(QtGui.QPixmap("tp_interface/ui/icons/red_x.png"))
        self.mw.statusbar.clearMessage()
        self.mw.ytEditMetadataButton.setEnabled(False)
