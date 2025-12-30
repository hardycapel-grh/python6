from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton, QTextEdit, QMessageBox
)
from PySide6.QtCore import Qt
import os

from logger import logger


class LogViewerPage(QWidget):
    def __init__(self):
        super().__init__()
        self.title = "Log Viewer"
        self.read_only = True
        self.log_path = "app.log"  # adjust if your log file is elsewhere

        self.build_ui()
        self.load_log()

    def build_ui(self):
        layout = QVBoxLayout()

        title = QLabel("Application Log Viewer")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        # Log text area
        self.text_area = QTextEdit()
        self.text_area.setReadOnly(True)
        layout.addWidget(self.text_area)

        # Buttons
        self.refresh_btn = QPushButton("Refresh Log")
        self.refresh_btn.clicked.connect(self.load_log)
        layout.addWidget(self.refresh_btn)

        self.clear_btn = QPushButton("Clear Log")
        self.clear_btn.clicked.connect(self.clear_log)
        layout.addWidget(self.clear_btn)

        self.setLayout(layout)

    def load_log(self):
        """Load the contents of the log file into the text area."""
        try:
            if not os.path.exists(self.log_path):
                self.text_area.setPlainText("Log file not found.")
                logger.warning("LogViewerPage: Log file not found")
                return

            with open(self.log_path, "r", encoding="utf-8") as f:
                content = f.read()

            self.text_area.setPlainText(content)
            logger.info("LogViewerPage: Log loaded successfully")

        except Exception as e:
            logger.error(f"LogViewerPage: Failed to load log: {e}")
            QMessageBox.critical(self, "Error", "Failed to load log file")

    def clear_log(self):
        """Clear the log file (disabled in read-only mode)."""
        if self.read_only:
            QMessageBox.warning(self, "Permission Denied", "You do not have permission to clear logs")
            return

        try:
            with open(self.log_path, "w", encoding="utf-8") as f:
                f.write("")

            self.text_area.setPlainText("")
            logger.info("LogViewerPage: Log cleared by admin")

        except Exception as e:
            logger.error(f"LogViewerPage: Failed to clear log: {e}")
            QMessageBox.critical(self, "Error", "Failed to clear log file")

    def set_read_only(self, readonly: bool):
        """Enable or disable log clearing based on permissions."""
        self.read_only = readonly
        self.clear_btn.setEnabled(not readonly)

        if readonly:
            logger.info("LogViewerPage set to read-only mode")
        else:
            logger.info("LogViewerPage set to read-write mode")