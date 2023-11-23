from PyQt6.QtWidgets import QWidget, QMainWindow, QSpacerItem, QSizePolicy

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
    def __init__(self, parent: QMainWindow = None):
        super().__init__()
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
        pass

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
