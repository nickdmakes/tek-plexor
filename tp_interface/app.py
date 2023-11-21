import sys
from PyQt6.QtWidgets import QApplication, QDialog, QMainWindow, QMessageBox
from .main_window_ui import Ui_MainWindow


# show the main window
def start_app():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        # Controller imports must be done here to avoid circular imports
        from .YtSingleController import YtSingleController

        self.setupUi(self)
        self.ytSingleController = YtSingleController(self)
        # state variables
        self.downloading = False

    def setDownloading(self, new_state: bool = False):
        self.downloading = new_state
