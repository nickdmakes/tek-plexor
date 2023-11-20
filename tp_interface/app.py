import sys
from PyQt6.QtWidgets import QApplication, QDialog, QMainWindow, QMessageBox
from .main_window_ui import Ui_MainWindow


# show the main window
def start_app():
    app = QApplication(sys.argv)
    window = Window()
    window.show()
    sys.exit(app.exec())


class Window(QMainWindow, Ui_MainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)
        self.connectSignalsSlots()

    def connectSignalsSlots(self):
        self.downloadButton.clicked.connect(self.downloadButtonClicked)

    def downloadButtonClicked(self):
        self.statusbar.showMessage("Downloading...")
