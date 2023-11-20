from tp_engine.yt_api import get_title, download_single_audio
from tp_conversion.converter import opus_to_m4a
from tp_interface.app import *


# contains a reference QmainWindow object for the main window of the application
class YtSingleController:
    def __init__(self, main_window):
        super().__init__()
        self.mw = main_window
        self.connectSignalsSlots()

    def connectSignalsSlots(self):
        self.mw.downloadButton.clicked.connect(self.downloadButtonClicked)
        self.mw.singleUrlInput.textChanged.connect(self.singleUrlInputChanged)

    def downloadButtonClicked(self):
        self.mw.downloadButton.setEnabled(False)
        self.mw.statusbar.showMessage("Downloading...")
        self.logConsole("------------- Starting download --------------")
        try:
            title = (self.mw.singleArtistInput.text() + "_" + self.mw.singleSongNameInput.text()).replace(" ", "-")
            print(title)
            self.mw.progressBar.setValue(10)
            out_file = download_single_audio(url=self.mw.singleUrlInput.text(), out_path="data", file_name=f'{title}.opus')
            self.logConsole(f"Downloaded original to {out_file}")
            self.mw.progressBar.setValue(50)
            self.logConsole(f"Converting to m4a...")
            opus_to_m4a(out_file, out_file.replace(".opus", ".m4a"), delete_in_file=True)
            self.logConsole(f"Converted {title}.opus to {title}.m4a")
            self.mw.progressBar.setValue(100)
            self.mw.statusbar.showMessage("Download successful!")
            self.mw.downloadButton.setEnabled(True)
            self.logConsole("------------- Download complete --------------")
        except Exception as e:
            self.logConsole(f"Error downloading audio: {e}")
            self.mw.statusbar.showMessage("Download failed!")
            self.mw.downloadButton.setEnabled(True)
            self.mw.progressBar.setValue(0)

    def singleUrlInputChanged(self, text):
        try:
            title = get_title(url=text)
            print(title)
            title_split = title.split("-")
            if len(title_split) >= 2:
                self.mw.singleArtistInput.setText(title_split[0].strip())
                self.mw.singleSongNameInput.setText(title_split[1].strip())
            self.logConsole(f"Youtube title found: {title}")
        except Exception as e:
            pass

    # append new line to debug console
    def logConsole(self, text):
        self.mw.debugConsole.insertPlainText(f'{text}\n')
