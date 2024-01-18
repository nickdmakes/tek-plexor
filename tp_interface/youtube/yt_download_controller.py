import time
from datetime import datetime
from PyQt6 import QtGui
from PyQt6.QtCore import QThreadPool
from PyQt6.QtWidgets import QFileDialog
from multiprocessing import cpu_count
from pathvalidate import sanitize_filename

from tp_engine.yt_api import get_yt_info_from_link, download_single_audio, YtInfoPayload
from tp_conversion.converter import convert
from tp_interface.app import MainWindow
from tp_interface.debug_logger import DebugLogger
from tp_interface.shared.metadata.metadata_controller import MetadataController
from utils.Utils import YtDownloadPayload as dp
from utils.Utils import MetadataPayload as mp

from .yt_download_worker import YtDownloadWorker
from .yt_info_worker import YtInfoWorker


# class that contains the current state of the download process
# It is used to update the progress bar and also to know when the download is finished
# It should get stats for the download process like time elapsed
class YtDownloadState:
    def __init__(self, n_processes: int, nuggets: int = 1):
        self.n_processes = n_processes
        self.n_download_failed = 0
        self.n_conversions_failed = 0
        self.n_nuggets = n_processes * nuggets
        self.nuggets_completed = 0
        self.start_time = time.time()

    def complete_nugget(self, n: int = 1):
        self.nuggets_completed += n

    def increment_download_failed(self):
        self.n_download_failed += 1

    def increment_conversion_failed(self):
        self.n_conversions_failed += 1

    def are_nuggets_done(self):
        return self.nuggets_completed == self.n_nuggets

    def get_stats_str(self):
        n_success = self.n_processes - self.n_download_failed
        # get elapsed time. Use datetime to format it as 00:00.00
        # round to 2 decimal places
        elapsed_time = datetime.fromtimestamp(time.time() - self.start_time).strftime("%M:%S.%f")[:-4]

        downloads_ratio = f"{self.n_processes-self.n_download_failed}/{self.n_processes}"
        conversions_ratio = f"{(self.n_processes-self.n_download_failed)-self.n_conversions_failed}/{self.n_processes-self.n_download_failed}"

        return f"downloads: {downloads_ratio}\nconversions: {conversions_ratio}\nerrors: {self.n_download_failed + self.n_conversions_failed}\nTime elapsed: {elapsed_time}"


# contains a reference QmainWindow object for the main window of the application
class YtDownloadController:
    def __init__(self, main_window: MainWindow):
        super().__init__()
        self.mw = main_window
        self.connectSignalsSlots()
        self.threadpool = QThreadPool()
        self.threadpool.setMaxThreadCount(cpu_count()-1)
        self.setupUi()
        self.debugLogger = DebugLogger(self.mw.debugConsole)
        self.metadataController = MetadataController(parent=self.mw, md_title=self.mw.ytTitleInput,
                                                     md_artist=self.mw.ytArtistInput)
        self.downloadState = YtDownloadState(n_processes=0)

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

    def update_progress_bar(self):
        self.mw.progressBar.setValue(int(self.downloadState.nuggets_completed / self.downloadState.n_nuggets * 100))

    def makePayload(self):
        compression = ""
        if self.mw.ytCompressionRadioOgg.isChecked():
            compression = dp.OGG
        elif self.mw.ytCompressionRadioM4a.isChecked():
            compression = dp.M4A
        elif self.mw.ytCompressionRadioMp4.isChecked():
            compression = dp.MP4
        elif self.mw.ytCompressionRadioMp3.isChecked():
            compression = dp.MP3

        bitrate = dp.BIT_RATES[self.mw.ytBitRateDial.value()]

        payload = dp(
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
        self.mw.ytBitRateLabel.setText(f"{dp.BIT_RATES[value]} kbps")

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

        self.downloadState = YtDownloadState(n_processes=len(self.metadataController.mdPayloads), nuggets=2)

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
        worker.signals.original_song_download_error.connect(self.originalSongDownloadError)
        worker.signals.song_conversion_started.connect(self.songConversionStarted)
        worker.signals.song_conversion_file_exists_error.connect(self.songConversionFileExists)
        worker.signals.song_conversion_finished.connect(self.songConversionFinished)
        worker.signals.song_conversion_error.connect(self.songConversionError)
        worker.signals.download_result.connect(self.downloadResult)
        worker.signals.download_finished.connect(self.downloadFinished)
        worker.signals.download_error.connect(self.downloadError)
        return worker

    def ytDownload_fn(self, osdsc, osdf, scs, scf, download_payload: dict, metadata_payload: dict):
        title = metadata_payload[mp.TITLE]
        artist = metadata_payload[mp.ARTIST]
        filename = sanitize_filename(f'{title} - {artist}')
        url = metadata_payload[mp.URL]
        out_path = download_payload[dp.OUT_PATH]
        osdsc.emit()
        # download will add the correct extension to filename
        out_file, filename = download_single_audio(url=url, out_path=out_path, filename=filename)
        osdf.emit(filename)
        if download_payload[dp.CONVERSION_ENABLED]:
            scs.emit()
            convert(out_file, download_payload, metadata_payload)
            scf.emit(filename)

    def downloadStarted(self):
        self.mw.ytDownloadButton.setEnabled(False)

    def originalSongDownloadStarted(self):
        self.mw.statusbar.showMessage("Downloading...")
        pass

    def originalSongDownloadFinished(self, filename):
        self.downloadState.complete_nugget()
        self.debugLogger.successLog(f'Downloaded {filename} from Youtube')
        self.update_progress_bar()

    def originalSongDownloadError(self, error):
        self.downloadState.increment_download_failed()
        self.downloadState.complete_nugget(n=2)
        self.debugLogger.errorLog(f'Error: {error[1]}')

    def songConversionStarted(self):
        self.mw.statusbar.showMessage("Converting...")

    def songConversionFileExists(self, filenames):
        self.downloadState.increment_conversion_failed()
        self.downloadState.complete_nugget()
        self.debugLogger.errorLog(f'File already exists: {filenames[0]}')
        self.debugLogger.warningLog(f'File renamed to {filenames[1].split("/")[-1]}')

    def songConversionFinished(self, filename):
        self.downloadState.complete_nugget()
        self.debugLogger.successLog(f'Successfully converted {filename}')
        self.update_progress_bar()

    def songConversionError(self, error):
        self.downloadState.increment_conversion_failed()
        self.downloadState.complete_nugget()
        self.debugLogger.errorLog(f'Error: {error[1]}')

    def downloadResult(self):
        pass

    def downloadFinished(self):
        if self.downloadState.are_nuggets_done():
            self.debugLogger.infoLog(self.downloadState.get_stats_str())
            self.debugLogger.infoLog("-------- PROCESS FINISHED: YouTube yt Download -------")
            self.mw.ytDownloadButton.setEnabled(True)
            self.mw.statusbar.showMessage("Download finished!")
        self.update_progress_bar()

    def downloadError(self, error):
        self.debugLogger.errorLog(f"Error: {error[1]}")
        self.mw.statusbar.showMessage("Download failed!")
        self.mw.ytDownloadButton.setEnabled(True)

    def ytUrlInputChanged(self, text: str):
        """change the status icon to green if the url is valid. Also,
        if the title is found, split it and put the artist"""
        self.mw.ytUrlStatusIcon.setPixmap(QtGui.QPixmap("tp_interface/ui/icons/grey_checkmark.png"))
        self.metadataController.clear_payloads()
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
