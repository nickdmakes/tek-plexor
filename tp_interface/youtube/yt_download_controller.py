import os
from PyQt6 import QtGui
from PyQt6.QtCore import QThreadPool
from PyQt6.QtWidgets import QFileDialog

from tp_engine.yt_api import get_yt_info_from_link, download_single_audio, YtInfoPayload
from tp_conversion.converter import convert
from tp_interface.app import MainWindow
from tp_interface.debug_logger import DebugLogger
from tp_interface.shared.metadata.metadata_controller import MetadataController
from utils.Utils import YtDownloadPayload as pl
from utils.Utils import MetadataPayload as mp

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
        self.download_process_state = (0, 0)


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
        self.metadataController.mdPayloads[0].payload[mp.TITLE] = text.strip()

    def ytArtistInputChanged(self, text: str):
        if not self.metadataController.mdPayloads:
            return
        self.metadataController.mdPayloads[0].payload[mp.ARTIST] = text.strip()

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
        download_payload = self.makePayload()
        valid, reason = download_payload.isValid()
        if not valid:
            self.debugLogger.errorLog(f"Error: {reason}")
            return

        self.debugLogger.infoLog("\n-------- PROCESS STARTED: YouTube yt Download -------")

        self.download_process_state = (0, len(self.metadataController.mdPayloads))

        for i, metadata_payload in enumerate(self.metadataController.mdPayloads):
            worker = self.makeDownloadWorker(download_payload=download_payload.getPayload(),
                                             metadata_payload=metadata_payload.getPayload())
            self.threadpool.start(worker)

    def makeDownloadWorker(self, download_payload: dict, metadata_payload: dict):
        worker = YtDownloadWorker(self.ytDownload_fn, download_payload=download_payload,
                                  metadata_payload=metadata_payload)
        worker.signals.download_started.connect(self.downloadStarted)
        worker.signals.original_song_download_started.connect(self.originalSongDownloadStarted)
        worker.signals.original_song_download_finished.connect(self.originalSongDownloadFinished)
        worker.signals.song_conversion_started.connect(self.songConversionStarted)
        worker.signals.song_conversion_file_exists.connect(self.songConversionFileExists)
        worker.signals.song_conversion_finished.connect(self.songConversionFinished)
        worker.signals.download_finished.connect(self.downloadFinished)
        worker.signals.download_error.connect(self.downloadError)
        return worker

    def ytDownload_fn(self, osdsc, osdf, scs, scf, download_payload: dict, metadata_payload: dict):
        title = metadata_payload[mp.TITLE]
        artist = metadata_payload[mp.ARTIST]
        filename = f'{title} - {artist}'
        url = metadata_payload[mp.URL]
        out_path = download_payload[pl.OUT_PATH]
        osdsc.emit()
        # download will add the correct extension to filename
        out_file, filename = download_single_audio(url=url, out_path=out_path, filename=filename)
        osdf.emit(filename)
        if download_payload[pl.CONVERSION_ENABLED]:
            scs.emit()
            convert(out_file, download_payload, metadata_payload)
            scf.emit(filename)

    def downloadStarted(self):
        self.mw.ytDownloadButton.setEnabled(False)

    def originalSongDownloadStarted(self):
        pass

    def originalSongDownloadFinished(self, filename):
        self.debugLogger.successLog(f'Downloaded {filename} from Youtube')

    def songConversionStarted(self):
        self.debugLogger.infoLog(f'Converting original codec...')

    def songConversionFileExists(self, filenames):
        self.debugLogger.errorLog(f'File already exists: {filenames[0]}')
        self.debugLogger.errorLog(f'File renamed to {filenames[1]}')
        self.debugLogger.errorLog(f"Press Download again to retry")
        self.mw.ytDownloadButton.setEnabled(True)
        self.mw.statusbar.showMessage("Download failed!")

    def songConversionFinished(self, filename):
        self.debugLogger.successLog(f'Successfully converted {filename}')

    def downloadFinished(self):
        self.mw.ytDownloadButton.setEnabled(True)
        self.download_process_state = (self.download_process_state[0] + 1, self.download_process_state[1])
        self.mw.progressBar.setValue(int((self.download_process_state[0] / self.download_process_state[1]) * 100))

    def downloadError(self, error):
        self.debugLogger.errorLog(f"Error: {error[1]}")
        self.mw.statusbar.showMessage("Download failed!")
        self.mw.ytDownloadButton.setEnabled(True)

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
        return get_yt_info_from_link(url=url)

    def ytInfoRetrievalStarted(self):
        self.mw.ytUrlStatusIcon.setPixmap(QtGui.QPixmap("tp_interface/ui/icons/grey_checkmark.png"))

    def ytInfoRetrievalResult(self, info: YtInfoPayload):
        first_title = info.info[0][0]
        first_artist = info.info[0][1]

        if info.is_playlist:
            self.debugLogger.infoLog(f"Found YouTube playlist: {len(info.info)} songs found")
        else:
            self.debugLogger.infoLog(f"Found YouTube song: {first_title} - {first_artist}")

        self.mw.ytTitleInput.setText(first_title)
        self.mw.ytArtistInput.setText(first_artist)
        self.mw.ytUrlStatusIcon.setPixmap(QtGui.QPixmap("tp_interface/ui/icons/green_checkmark.png"))
        self.metadataController.yt_info_to_payload(yt_info=info.info)
        self.mw.ytEditMetadataButton.setEnabled(True)

    def ytInfoRetrievalFinished(self):
        pass

    def ytInfoRetrievalError(self, error):
        self.mw.ytUrlStatusIcon.setPixmap(QtGui.QPixmap("tp_interface/ui/icons/red_x.png"))
        self.mw.statusbar.clearMessage()
        self.mw.ytEditMetadataButton.setEnabled(False)
