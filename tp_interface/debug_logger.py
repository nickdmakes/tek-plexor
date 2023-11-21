from PyQt6.QtWidgets import QTextBrowser


class DebugLogger:
    def __init__(self, debug_window: QTextBrowser):
        super().__init__()
        self.dw = debug_window

    # send messages to the debug window
    def infoLog(self, message):
        self.dw.append(message)

    # send error messages to the debug window in red
    def errorLog(self, message):
        self.dw.append(f"<font color='red'>{message}</font>")

    # send warning messages to the debug window in yellow
    def warningLog(self, message):
        self.dw.append(f"<font color='yellow'>{message}</font>")

    # send success messages to the debug window in green
    def successLog(self, message):
        self.dw.append(f"<font color='green'>{message}</font>")
