from PySide6.QtWidgets import QWidget, QVBoxLayout, QTextEdit
from ui.components.logger import logger
import os


class LogViewerPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        layout = QVBoxLayout(self)

        # Main text area for logs
        self.text_area = QTextEdit()
        self.text_area.setReadOnly(True)
        layout.addWidget(self.text_area)

        logger.info("LogViewerPage loaded")

        self.load_log_file()

    def load_log_file(self):
        """Load the main application log into the viewer."""
        log_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
            "logs",
            "app.log"
        )

        if not os.path.exists(log_path):
            logger.error("Log file not found")
            self.text_area.setText("Log file not found.")
            return

        try:
            with open(log_path, "r", encoding="utf-8") as f:
                content = f.read()
                self.text_area.setText(content)
                logger.info("Log file loaded into viewer")
        except Exception as e:
            logger.error(f"Failed to read log file: {e}")
            self.text_area.setText("Error reading log file.")