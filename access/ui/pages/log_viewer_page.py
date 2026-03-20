from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QTextEdit, QPushButton, QHBoxLayout, QCheckBox
)
from PySide6.QtCore import QTimer
from ui.components.logger import logger
import os


class LogViewerPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        layout = QVBoxLayout(self)

        # --- Controls row ---
        controls = QHBoxLayout()

        self.refresh_btn = QPushButton("Refresh")
        self.refresh_btn.clicked.connect(self.load_log_file)
        controls.addWidget(self.refresh_btn)

        self.tail_checkbox = QCheckBox("Tail -f")
        self.tail_checkbox.stateChanged.connect(self._toggle_tail)
        controls.addWidget(self.tail_checkbox)

        controls.addStretch()
        layout.addLayout(controls)

        # --- Log text area ---
        self.text_area = QTextEdit()
        self.text_area.setReadOnly(True)
        layout.addWidget(self.text_area)

        # Timer for tail -f
        self.tail_timer = QTimer()
        self.tail_timer.setInterval(1000)  # 1 second
        self.tail_timer.timeout.connect(self.load_log_file)

        logger.info("LogViewerPage loaded")

        QTimer.singleShot(0, self.load_log_file)

    def _safe_read(self, path):
        import time
        for _ in range(3):  # retry a few times
            try:
                with open(path, "r", encoding="utf-8") as f:
                    return f.read()
            except Exception:
                time.sleep(0.05)  # wait 50ms
        return None

    # ---------------------------------------------------------
    # Load log file
    # ---------------------------------------------------------
    def load_log_file(self):
        # If widget is not visible or not fully constructed, skip update
        if not self.isVisible():
            return

        if not hasattr(self, "text_area") or self.text_area is None:
            return

        log_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
            "logs",
            "app.log"
        )

        if not os.path.exists(log_path):
            self.text_area.setText("Log file not found.")
            return

        try:
            content = self._safe_read(log_path)

            if content is None:
                # File is temporarily locked — skip this cycle silently
                return

            # Tail mode
            if self.tail_checkbox.isChecked():
                self.text_area.setPlainText(content)

                # Safe scroll-to-bottom
                try:
                    cursor = self.text_area.textCursor()
                    cursor.movePosition(cursor.End)
                    self.text_area.setTextCursor(cursor)
                except Exception:
                    pass

            else:
                # Preserve scroll position
                try:
                    scroll = self.text_area.verticalScrollBar().value()
                    self.text_area.setPlainText(content)
                    self.text_area.verticalScrollBar().setValue(scroll)
                except Exception:
                    self.text_area.setPlainText(content)

        except Exception as e:
            self.text_area.setText(f"Error reading log file:\n{e}")

    # ---------------------------------------------------------
    # Tail -f toggle
    # ---------------------------------------------------------
    def _toggle_tail(self, state):
        if state:
            self.tail_timer.start()
        else:
            self.tail_timer.stop()

    def closeEvent(self, event):
        self.tail_timer.stop()
        super().closeEvent(event)

        

