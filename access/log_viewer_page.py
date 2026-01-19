from PySide6.QtWidgets import (
    QVBoxLayout, QLabel, QPushButton, QTextEdit, QMessageBox, QPlainTextEdit, QApplication
    , QHBoxLayout
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QTextCursor
import os

from logger import logger
from base_page import BasePage, QComboBox, QLineEdit
from collections import deque
from PySide6.QtWidgets import QCheckBox
from PySide6.QtCore import QTimer






class LogViewerPage(BasePage):
    title = "Log Viewer"

    def __init__(self):
        super().__init__()
        self.log_path = "app.log"  # adjust if needed

        self.build_ui()
        self.load_log()
        self._raw_log_content = ""
        self._match_positions = []
        self._current_match_index = -1

    def build_ui(self):
        layout = QVBoxLayout()
        self.setLayout(layout)

        title = QLabel("Application Log Viewer", self)
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)


        # Line count selector
        self.line_count = QComboBox(self)
        self.line_count.addItems(["100", "500", "1000"])
        self.line_count.setCurrentText("500")
        self.line_count.setObjectName("safe")  # always allowed
        self.line_count.currentTextChanged.connect(self.load_log)
        layout.addWidget(self.line_count)

        # Log text area (always read-only)
        self.text_area = QTextEdit(self)
        self.text_area.setReadOnly(True)
        layout.addWidget(self.text_area)
        # Copy to clipboard button
        copy_btn = QPushButton("Copy to Clipboard", self)
        copy_btn.setObjectName("safe")  # always enabled
        copy_btn.clicked.connect(
            lambda: QApplication.clipboard().setText(self._raw_log_content)
        )
        layout.addWidget(copy_btn)

        # Search navigation buttons
        nav_layout = QHBoxLayout()

        self.prev_btn = QPushButton("Previous", self)
        self.prev_btn.setObjectName("safe")
        self.prev_btn.clicked.connect(self.goto_prev_match)
        nav_layout.addWidget(self.prev_btn)

        self.next_btn = QPushButton("Next", self)
        self.next_btn.setObjectName("safe")
        self.next_btn.clicked.connect(self.goto_next_match)
        nav_layout.addWidget(self.next_btn)

        layout.addLayout(nav_layout)

        # Auto-refresh checkbox
        self.auto_refresh = QCheckBox("Auto-refresh (tail -f)", self)
        self.auto_refresh.setObjectName("safe")
        layout.addWidget(self.auto_refresh)

        # Timer for tailing
        self.timer = QTimer(self)
        self.timer.setInterval(2000)  # refresh every 2 seconds
        self.timer.timeout.connect(self.load_log)

        # Start/stop timer when checkbox toggles
        self.auto_refresh.stateChanged.connect(
            lambda state: self.timer.start() if state else self.timer.stop()
        )

        # Refresh button (always allowed)
        self.refresh_btn = QPushButton("Refresh Log", self)
        self.refresh_btn.setObjectName("safe")   # <-- stays enabled in RO mode
        self.refresh_btn.clicked.connect(self.load_log)
        layout.addWidget(self.refresh_btn)

        # Clear button (disabled in RO mode)
        self.clear_btn = QPushButton("Clear Log", self)
        self.clear_btn.clicked.connect(self.clear_log)
        layout.addWidget(self.clear_btn)

        # Search bar
        self.search_bar = QLineEdit(self)
        self.search_bar.setPlaceholderText("Search logs...")
        self.search_bar.setObjectName("safe")
        self.search_bar.textChanged.connect(self.apply_filter)
        layout.addWidget(self.search_bar)

    def apply_filter(self):
        query = self.search_bar.text().strip()

        if not query:
            colored = self.colorize(self._raw_log_content)
            self.text_area.setHtml(colored)
            return

        filtered = [
            line for line in self._raw_log_content.splitlines()
            if query.lower() in line.lower()
        ]

        filtered_text = "\n".join(filtered)

        # Track match positions for navigation
        self._match_positions = []
        self._current_match_index = -1

        if query:
            lower_text = filtered_text.lower()
            lower_query = query.lower()
            start = 0
            qlen = len(lower_query)

            while True:
                idx = lower_text.find(lower_query, start)
                if idx == -1:
                    break
                self._match_positions.append(idx)
                start = idx + qlen

        # Highlight matches BEFORE colorizing
        highlighted = self.highlight_matches(filtered_text, query)

        colored = self.colorize(highlighted)
        self.text_area.setHtml(colored)



    def load_log(self):
        try:
            # Detect if user is already at bottom
            at_bottom = self.text_area.verticalScrollBar().value() == \
            self.text_area.verticalScrollBar().maximum()
            if not os.path.exists(self.log_path):
                self.text_area.setPlainText("Log file not found.")
                logger.warning("LogViewerPage: Log file not found")
                return

            max_size = 5_000_000
            size = os.path.getsize(self.log_path)
            if size > max_size:
                logger.warning(
                    f"LogViewerPage: Log file too large ({size:,} bytes). "
                    "Loading last lines only."
                )

            max_lines = int(self.line_count.currentText())
            last_lines = deque(maxlen=max_lines)

            with open(self.log_path, "r", encoding="utf-8") as f:
                for line in f:
                    last_lines.append(line)

            content = "".join(last_lines)

            # Store raw content
            self._raw_log_content = content

            # Apply search + colour
            self.apply_filter()
            self.text_area.moveCursor(QTextCursor.End)
            # Only auto-scroll if user was already at bottom
            if at_bottom:
                self.text_area.moveCursor(QTextCursor.End)
            
            logger.info("LogViewerPage: Loaded last lines")


        except Exception as e:
            logger.error(f"LogViewerPage: Failed to load log: {e}")
            QMessageBox.critical(self, "Error", "Failed to load log file")


    def clear_log(self):
        """Clear the log file (disabled in read-only mode)."""
        try:
            with open(self.log_path, "w", encoding="utf-8") as f:
                f.write("")

            self.text_area.setPlainText("")
            logger.info("LogViewerPage: Log cleared by admin")

        except Exception as e:
            logger.error(f"LogViewerPage: Failed to clear log: {e}")
            QMessageBox.critical(self, "Error", "Failed to clear log file")

    def colorize(self, text: str) -> str:
        lines = []
        for line in text.splitlines():
            if "ERROR" in line:
                lines.append(f'<span style="color:#ff5555;">{line}</span>')
            elif "WARNING" in line:
                lines.append(f'<span style="color:#ffaa00;">{line}</span>')
            elif "INFO" in line:
                lines.append(f'<span style="color:#55aaff;">{line}</span>')
            else:
                lines.append(line)

        return "<br>".join(lines)
    
    def highlight_matches(self, text: str, query: str) -> str:
        if not query:
            return text

        # Case-insensitive highlight
        lower_text = text.lower()
        lower_query = query.lower()

        result = ""
        i = 0
        qlen = len(lower_query)

        while i < len(text):
            if lower_text[i:i+qlen] == lower_query:
                result += f'<span style="background-color: yellow; color: black;">{text[i:i+qlen]}</span>'
                i += qlen
            else:
                result += text[i]
                i += 1

        return result
    
    def goto_next_match(self):
        if not self._match_positions:
            return

        self._current_match_index = (self._current_match_index + 1) % len(self._match_positions)
        self._scroll_to_match()

    def goto_prev_match(self):
        if not self._match_positions:
            return

        self._current_match_index = (self._current_match_index - 1) % len(self._match_positions)
        self._scroll_to_match()

    def _scroll_to_match(self):
        pos = self._match_positions[self._current_match_index]

        cursor = self.text_area.textCursor()
        cursor.setPosition(pos)
        self.text_area.setTextCursor(cursor)
        self.text_area.ensureCursorVisible()