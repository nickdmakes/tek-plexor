import sys
from PyQt6.QtWidgets import QApplication, QMainWindow
from tp_interface.main_window_ui import Ui_MainWindow


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
        from tp_interface.youtube.yt_download_controller import YtDownloadController

        self.setupUi(self)
        self.ytSingleController = YtDownloadController(self)


