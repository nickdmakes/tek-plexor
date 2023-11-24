from PyQt6.QtWidgets import QWidget, QMainWindow, QSpacerItem, QSizePolicy, QLineEdit

from .metadata_window_ui import Ui_MetadataWindow
from .metadata_row_ui import Ui_MetadataRow

from utils.Utils import MetadataPayload as mp


class MetadataWindow(QWidget, Ui_MetadataWindow):
    def __init__(self, parent: QMainWindow = None):
        super().__init__()
        self.setupUi(self)
        self.parent = parent


class MetadataRow(QWidget, Ui_MetadataRow):
    def __init__(self):
        super(MetadataRow, self).__init__()
        self.setupUi(self)


class MetadataController:
    def __init__(self, parent: QMainWindow = None, md_title: QLineEdit = None, md_artist: QLineEdit = None):
        super().__init__()
        # References to the main window's title and artist inputs. They update when the metadata apply button is clicked
        self.md_title = md_title
        self.md_artist = md_artist
        # Reference to the metadata UI window
        self.mdw = MetadataWindow(parent=parent)
        self.connectSignalsSlots()
        self.mdPayloads = list[mp]()

    def yt_info_to_payload(self, yt_info: list[tuple[str, str, str]]):
        self.clear_payloads()
        for info in yt_info:
            payload = mp()
            payload.payload[mp.TITLE] = info[0]
            payload.payload[mp.ARTIST] = info[1]
            payload.payload[mp.URL] = info[2]
            self.mdPayloads.append(payload)

    def clear_payloads(self):
        self.mdPayloads = list[mp]()

    def connectSignalsSlots(self):
        self.mdw.mdCancelButton.clicked.connect(self.mdCancelButtonClicked)
        self.mdw.mdApplyButton.clicked.connect(self.mdApplyButtonClicked)

    def mdApplyButtonClicked(self):
        try:
            for i in range(self.mdw.mdColumn.count()-1):
                row = self.mdw.mdColumn.itemAt(i).widget()
                self.mdPayloads[i].payload[mp.TITLE] = row.titleInput.text()
                self.mdPayloads[i].payload[mp.ARTIST] = row.artistInput.text()

            self.md_title.setText(self.mdPayloads[0].payload[mp.TITLE])
            self.md_artist.setText(self.mdPayloads[0].payload[mp.ARTIST])

            self.mdw.close()
        except Exception as e:
            print(e)

    def mdCancelButtonClicked(self):
        self.mdw.close()

    def showMetadataWindow(self):
        self.mdw.show()

        # Remove all widgets from the column
        while self.mdw.mdColumn.count() > 1:
            item = self.mdw.mdColumn.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()

        # delete the spacer item at the end of the column
        self.mdw.mdColumn.removeItem(self.mdw.mdColumn.itemAt(0))

        self.mdw.mdNumberAudiosLabel.setText(f"{len(self.mdPayloads)} audios")

        for metadata in self.mdPayloads:
            row = MetadataRow()
            # set indicator as index of row
            row.identifierLabel.setText(f"{self.mdPayloads.index(metadata)+1}")
            row.titleInput.setText(metadata.payload[mp.TITLE])
            row.artistInput.setText(metadata.payload[mp.ARTIST])
            self.mdw.mdColumn.addWidget(row)

        # add spacer item at the end of the column
        self.mdw.mdColumn.addItem(QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))
