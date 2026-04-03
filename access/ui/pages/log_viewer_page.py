from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QTextEdit, QPushButton,
    QHBoxLayout, QCheckBox, QLineEdit, QLabel
)
from PySide6.QtCore import QTimer
from ui.components.logger import logger
import os


class LogViewerPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self._full_content = ""  # raw log text (unfiltered)

        layout = QVBoxLayout(self)

        # --- Controls row ---
        controls = QHBoxLayout()

        self.refresh_btn = QPushButton("Refresh")
        self.refresh_btn.clicked.connect(self.load_log_file)
        controls.addWidget(self.refresh_btn)

        self.tail_checkbox = QCheckBox("Tail -f")
        self.tail_checkbox.stateChanged.connect(self._toggle_tail)
        controls.addWidget(self.tail_checkbox)

        self.autoscroll_checkbox = QCheckBox("Auto-scroll")
        self.autoscroll_checkbox.setChecked(True)
        controls.addWidget(self.autoscroll_checkbox)

        self.open_folder_btn = QPushButton("Open Folder")
        self.open_folder_btn.clicked.connect(self._open_log_folder)
        controls.addWidget(self.open_folder_btn)

        controls.addStretch()
        layout.addLayout(controls)

        # --- Search row ---
        search_row = QHBoxLayout()

        search_row.addWidget(QLabel("Filter:"))
        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText("Type to filter log lines...")
        self.search_edit.textChanged.connect(self._apply_filter)
        search_row.addWidget(self.search_edit)

        layout.addLayout(search_row)

        # --- Log level filter row ---
        level_row = QHBoxLayout()

        self.filter_info = QCheckBox("INFO")
        self.filter_info.setChecked(True)
        level_row.addWidget(self.filter_info)

        self.filter_warning = QCheckBox("WARNING")
        self.filter_warning.setChecked(True)
        level_row.addWidget(self.filter_warning)

        self.filter_error = QCheckBox("ERROR")
        self.filter_error.setChecked(True)
        level_row.addWidget(self.filter_error)

        self.filter_debug = QCheckBox("DEBUG")
        self.filter_debug.setChecked(True)
        level_row.addWidget(self.filter_debug)

        level_row.addStretch()
        layout.addLayout(level_row)

        # Re-filter when any level checkbox changes
        self.filter_info.stateChanged.connect(self._apply_filter)
        self.filter_warning.stateChanged.connect(self._apply_filter)
        self.filter_error.stateChanged.connect(self._apply_filter)
        self.filter_debug.stateChanged.connect(self._apply_filter)

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
        for _ in range(3):
            try:
                with open(path, "r", encoding="utf-8") as f:
                    return f.read()
            except Exception:
                time.sleep(0.05)
        return None

    # ---------------------------------------------------------
    # Load log file
    # ---------------------------------------------------------
    def load_log_file(self):
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
            self._full_content = ""
            self.text_area.setText("Log file not found.")
            return

        try:
            content = self._safe_read(log_path)

            if content is None:
                return

            self._full_content = content
            self._apply_filter()

        except Exception as e:
            self.text_area.setText(f"Error reading log file:\n{e}")

    # ---------------------------------------------------------
    # Apply filter + level filters + highlighting
    # ---------------------------------------------------------
    def _apply_filter(self):
        if not self._full_content:
            self.text_area.clear()
            return

        # 1. Text filter
        query = self.search_edit.text().strip().lower()
        lines = self._full_content.splitlines()

        if query:
            lines = [ln for ln in lines if query in ln.lower()]

        # 2. Log-level filters
        def level_allowed(line: str) -> bool:
            lower = line.lower()

            if "error" in lower and not self.filter_error.isChecked():
                return False
            if "warning" in lower and not self.filter_warning.isChecked():
                return False
            if "debug" in lower and not self.filter_debug.isChecked():
                return False
            if "info" in lower and not self.filter_info.isChecked():
                return False

            return True

        lines = [ln for ln in lines if level_allowed(ln)]

        # 3. Highlighting
        def highlight(line: str) -> str:
            lower = line.lower()

            if "error" in lower:
                return f'<span style="color:#d9534f; font-weight:bold;">{line}</span>'
            if "warning" in lower:
                return f'<span style="color:#f0ad4e;">{line}</span>'
            if "debug" in lower:
                return f'<span style="color:#0275d8;">{line}</span>'
            if "info" in lower:
                return f'<span style="color:#5bc0de;">{line}</span>'

            return line

        highlighted = [highlight(ln) for ln in lines]
        html = "<br>".join(highlighted)

        # 4. Scroll behaviour
        should_autoscroll = (
            self.autoscroll_checkbox.isChecked()
            and self._is_at_bottom()
        )

        try:
            if not self.tail_checkbox.isChecked():
                if not should_autoscroll:
                    scroll = self.text_area.verticalScrollBar().value()
                    self.text_area.setHtml(html)
                    self.text_area.verticalScrollBar().setValue(scroll)
                else:
                    self.text_area.setHtml(html)
                    cursor = self.text_area.textCursor()
                    cursor.movePosition(cursor.End)
                    self.text_area.setTextCursor(cursor)
            else:
                self.text_area.setHtml(html)
                cursor = self.text_area.textCursor()
                cursor.movePosition(cursor.End)
                self.text_area.setTextCursor(cursor)
        except Exception:
            self.text_area.setHtml(html)

    # ---------------------------------------------------------
    # Tail -f toggle
    # ---------------------------------------------------------
    def _toggle_tail(self, state):
        if state:
            self.tail_timer.start()
        else:
            self.tail_timer.stop()

    def _is_at_bottom(self):
        bar = self.text_area.verticalScrollBar()
        return bar.value() >= bar.maximum() - 3

    def _open_log_folder(self):
        log_dir = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
            "logs"
        )

        if not os.path.exists(log_dir):
            os.makedirs(log_dir, exist_ok=True)

        try:
            os.startfile(log_dir)
        except Exception as e:
            self.text_area.setText(f"Could not open folder:\n{e}")

    def closeEvent(self, event):
        self.tail_timer.stop()
        super().closeEvent(event)