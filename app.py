from PyQt5.QtCore import pyqtSignal, QObject, Qt
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QPlainTextEdit, QApplication, QSystemTrayIcon, QMenu, QAction
from PyQt5.QtGui import QIcon
from collections import deque
import logging
import sys


class QtSignalLogHandler(QObject, logging.Handler):
    signal = pyqtSignal(str)

    def __init__(self):
        QObject.__init__(self)
        logging.Handler.__init__(self)

    def emit(self, record):
        msg = self.format(record)
        self.signal.emit(msg)


class LogViewerApp(QWidget):
    def __init__(self, app: QApplication,
                 log_maxlen=1000,
                 log_format='%(asctime)s - %(message)s',
                 log_level=logging.INFO,
                 show_at_run=True,
                 ):
        super().__init__()
        self.show_at_run = show_at_run
        self.app = app
        self.app.setQuitOnLastWindowClosed(False)
        self.setWindowTitle("Log Viewer")

        self._build_layout()
        self._build_tray_icon()

        # log handler
        self.log_queue = deque(maxlen=log_maxlen)
        handler = QtSignalLogHandler()
        handler.signal.connect(self.add_log, Qt.QueuedConnection)
        handler.setFormatter(logging.Formatter(log_format))

        logging.getLogger().addHandler(handler)
        logging.getLogger().setLevel(log_level)

    def _build_layout(self):
        self.plain_text_edit = QPlainTextEdit()
        self.plain_text_edit.setLineWrapMode(QPlainTextEdit.NoWrap)
        self.plain_text_edit.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.plain_text_edit.setReadOnly(True)

        layout = QVBoxLayout()
        layout.addWidget(self.plain_text_edit)
        self.setLayout(layout)

    def _build_tray_icon(self):
        self.tray_icon = QSystemTrayIcon()
        self.tray_icon.setIcon(QIcon('icon.png'))
        self.tray_icon.setVisible(True)

        show_logs_action = QAction("Logs", self)
        show_logs_action.triggered.connect(self.show)

        quit_action = QAction("Exit", self)
        quit_action.triggered.connect(self.app.quit)

        tray_menu = QMenu(self)
        tray_menu.addAction(show_logs_action)
        tray_menu.addAction(quit_action)
        self.tray_icon.setContextMenu(tray_menu)

    def closeEvent(self, event):
        event.ignore()
        self.hide()

    def add_log(self, message: str):
        self.log_queue.append(message)
        self.plain_text_edit.appendPlainText(message)

        if self.plain_text_edit.document().blockCount() > self.log_queue.maxlen*1.5:
            self.plain_text_edit.setPlainText('\n'.join(list(self.log_queue)))

    def run(self):
        if self.show_at_run:
            self.show()
        sys.exit(self.app.exec_())
