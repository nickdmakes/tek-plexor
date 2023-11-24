import sys, traceback
from PyQt6.QtCore import QObject, pyqtSignal, pyqtSlot, QRunnable
from tp_engine.yt_api import YTTitleRetrievalException, YtInfoPayload


class YtInfoWorkerSignals(QObject):
    """
    Defines the signals available from a running worker thread.
    """
    retrieval_started = pyqtSignal()
    retrieval_result = pyqtSignal(YtInfoPayload)
    retrieval_finished = pyqtSignal()
    retrieval_error = pyqtSignal(tuple)


class YtInfoWorker(QRunnable):
    def __init__(self, fn, url: str, *args, **kwargs):
        super(YtInfoWorker, self).__init__()
        # Store constructor arguments (re-used for processing)
        self.fn = fn
        self.args = args
        self.kwargs = kwargs
        self.signals = YtInfoWorkerSignals()

        self.kwargs['url'] = url

    @pyqtSlot()
    def run(self):
        # Retrieve args/kwargs here; and fire processing using them
        try:
            self.signals.retrieval_started.emit()
            info = self.fn(
                *self.args, **self.kwargs
            )
        except YTTitleRetrievalException:
            traceback.print_exc()
            exctype, value = sys.exc_info()[:2]
            self.signals.retrieval_error.emit((exctype, value, traceback.format_exc()))
        else:
            self.signals.retrieval_result.emit(info)
        finally:
            self.signals.retrieval_finished.emit()
