from .metadata_window_ui import Ui_MetadataWindow
from .metadata_payload import MetadataPayload


class YtDownloadController:
    def __init__(self):
        super().__init__()
        self.mdw = Ui_MetadataWindow()
        self.connectSignalsSlots()

    def connectSignalsSlots(self):
        pass

    def addMetaDataFields(self):
        pass
