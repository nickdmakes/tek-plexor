from PyQt6.QtWidgets import QWidget, QMainWindow, QSpacerItem, QSizePolicy, QLineEdit

from .metadata_window_ui import Ui_MetadataWindow
from .metadata_row_ui import Ui_MetadataRow
from .metadata_payload import MetadataPayload


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
        self.mdPayloads = list[MetadataPayload]()

    def yt_info_to_payload(self, yt_info: list[tuple[str, str]]):
        self.clear_payloads()
        for info in yt_info:
            payload = MetadataPayload(title=info[0], artist=info[1], album="", year="",
                                      genre="", track="", disc="", comment="")
            self.mdPayloads.append(payload)

    def clear_payloads(self):
        self.mdPayloads = list[MetadataPayload]()

    def connectSignalsSlots(self):
        self.mdw.mdApplyCancelBox.accepted.connect(self.mdApplyButtonClicked)
        self.mdw.mdApplyCancelBox.rejected.connect(self.mdCancelButtonClicked)

    def mdApplyButtonClicked(self):
        for i in range(self.mdw.mdColumn.count()-1):
            row = self.mdw.mdColumn.itemAt(i).widget()
            self.mdPayloads[i].title = row.titleInput.text()
            self.mdPayloads[i].artist = row.artistInput.text()

        self.md_title.setText(self.mdPayloads[0].title)
        self.md_artist.setText(self.mdPayloads[0].artist)

        self.mdw.close()

    def mdCancelButtonClicked(self):
        self.mdw.close()

    def showMetadataWindow(self):
        self.mdw.show()

        # Remove all widgets from the column
        for i in reversed(range(self.mdw.mdColumn.count())):
            self.mdw.mdColumn.removeItem(self.mdw.mdColumn.itemAt(i))

        self.mdw.mdNumberAudiosLabel.setText(f"{len(self.mdPayloads)} audios")

        for info in self.mdPayloads:
            row = MetadataRow()
            # set indicator as index of row
            row.identifierLabel.setText(f"{self.mdPayloads.index(info)+1}")
            row.titleInput.setText(info.title)
            row.artistInput.setText(info.artist)
            self.mdw.mdColumn.addWidget(row)

        self.mdw.mdColumn.addItem(QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))
