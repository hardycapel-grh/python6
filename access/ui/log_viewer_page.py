from PySide6.QtWidgets import (
    QVBoxLayout, QLabel, QPushButton, QTextEdit, QMessageBox, QApplication,
    QHBoxLayout, QCheckBox
)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QTextCursor
import os
import re
from collections import deque

from ui.logger import logger
from base_page import BasePage, QComboBox, QLineEdit
from PySide6.QtWidgets import QFrame
from ui.search_highlighter import SearchHighlighter


class LogViewerPage(BasePage):
    title = "Log Viewer"

    def __init__(self):
        super().__init__()

        # Determine the folder this file lives in
        BASE_DIR = os.path.dirname(os.path.abspath(__file__))

        # Build a path to logs/app.log relative to this file
        self.log_path = os.path.abspath(os.path.join(BASE_DIR,"..", "logs", "app.log"))

        # 1. Build UI
        self.build_ui()

        # 2. Internal state required for tail-f
        self._raw_log_content = ""
        self._last_file_pos = 0

        # 3. Highlighter
        from ui.search_highlighter import SearchHighlighter
        self.highlighter = SearchHighlighter(self.text_area.document())

        # 4. Connect signals
        self.connect_signals()

        # 5. Start timer
        if self.auto_refresh.isChecked():
            self.timer.start()

        # 6. Load log
        self.load_log()

    def toggle_advanced_tools(self):
        if self.adv_toggle.isChecked():
            self.adv_toggle.setText("Advanced Tools ▼")
            self.advanced_frame.show()
        else:
            self.adv_toggle.setText("Advanced Tools ▲")
            self.advanced_frame.hide()

    def connect_signals(self):
        self.line_count.currentTextChanged.connect(self.load_log)
        self.severity_filter.currentTextChanged.connect(self.apply_filter)
        self.regex_checkbox.stateChanged.connect(self.apply_filter)
        self.case_checkbox.stateChanged.connect(self.apply_filter)
        self.export_btn.clicked.connect(self.export_filtered_results)
        self.clear_btn.clicked.connect(self.clear_log)
        self.refresh_btn.clicked.connect(self.load_log)
        self.search_bar.textChanged.connect(self.apply_filter)
        self.prev_btn.clicked.connect(self.goto_prev_match)
        self.next_btn.clicked.connect(self.goto_next_match)
        self.timer.timeout.connect(self.load_log)
        self.auto_refresh.stateChanged.connect(
            lambda state: self.timer.start() if state else self.timer.stop()
        )

    def build_ui(self):
        layout = QVBoxLayout()
        self.setLayout(layout)

        title = QLabel("Application Log Viewer", self)
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        self.line_count = QComboBox(self)
        self.line_count.addItems(["100", "500", "1000"])
        self.line_count.setCurrentText("500")
        self.line_count.setObjectName("safe")
        layout.addWidget(self.line_count)

        self.severity_filter = QComboBox(self)
        self.severity_filter.addItems(["All Levels", "ERROR", "WARNING", "INFO", "DEBUG"])
        self.severity_filter.setObjectName("safe")
        layout.addWidget(self.severity_filter)

        self.advanced_frame = QFrame(self)
        self.advanced_frame.setFrameShape(QFrame.StyledPanel)
        adv_layout = QVBoxLayout(self.advanced_frame)
        adv_layout.setContentsMargins(6, 6, 6, 6)
        adv_layout.setSpacing(6)

        self.regex_checkbox = QCheckBox("Regex", self)
        self.regex_checkbox.setObjectName("safe")
        adv_layout.addWidget(self.regex_checkbox)

        self.case_checkbox = QCheckBox("Case sensitive", self)
        self.case_checkbox.setObjectName("safe")
        adv_layout.addWidget(self.case_checkbox)

        self.auto_refresh = QCheckBox("Auto-refresh (tail -f)", self)
        self.auto_refresh.setObjectName("safe")
        adv_layout.addWidget(self.auto_refresh)

        self.export_btn = QPushButton("Export Filtered Results", self)
        self.export_btn.setObjectName("safe")
        adv_layout.addWidget(self.export_btn)

        self.clear_btn = QPushButton("Clear Log", self)
        self.clear_btn.setObjectName("safe")
        adv_layout.addWidget(self.clear_btn)

        self.refresh_btn = QPushButton("Refresh Log", self)
        self.refresh_btn.setObjectName("safe")
        adv_layout.addWidget(self.refresh_btn)

        self.text_area = QTextEdit(self)
        self.text_area.setReadOnly(True)
        layout.addWidget(self.text_area)

        self.search_bar = QLineEdit(self)
        self.search_bar.setPlaceholderText("Search logs...")
        self.search_bar.setObjectName("safe")
        layout.addWidget(self.search_bar)

        nav_layout = QHBoxLayout()
        self.prev_btn = QPushButton("Previous", self)
        self.prev_btn.setObjectName("safe")
        nav_layout.addWidget(self.prev_btn)

        self.next_btn = QPushButton("Next", self)
        self.next_btn.setObjectName("safe")
        nav_layout.addWidget(self.next_btn)

        self.match_label = QLabel("No matches", self)
        nav_layout.addWidget(self.match_label)

        layout.addLayout(nav_layout)

        self.timer = QTimer(self)
        self.timer.setInterval(2000)

    # ----------------------------------------------------------------------
    # FILTERING PIPELINE
    # ----------------------------------------------------------------------
    def apply_filter(self):
        """
        Applies all active filters:
        - Severity filter
        - Search query
        - Regex toggle
        - Case sensitivity
        - Line count limit
        And updates:
        - Log text area
        - Search Results dock
        - Match navigation counters
        """
        if not hasattr(self, "highlighter"):
            return
        if not hasattr(self, "_raw_log_content"):
            return

        text = self._raw_log_content
        query = self.search_bar.text()
        severity = self.severity_filter.currentText()
        use_regex = self.regex_checkbox.isChecked()
        case_sensitive = self.case_checkbox.isChecked()

        # ------------------------------------------------------------
        # 1. Apply severity filter
        # ------------------------------------------------------------
        lines = text.splitlines()
        if severity != "All Levels":
            lines = [line for line in lines if severity in line]

        # ------------------------------------------------------------
        # 2. Apply search filter (regex or normal)
        # ------------------------------------------------------------
        if query:
            filtered_lines = []
            flags = 0 if case_sensitive else re.IGNORECASE

            try:
                if use_regex:
                    pattern = re.compile(query, flags)
                    filtered_lines = [line for line in lines if pattern.search(line)]
                else:
                    q = query if case_sensitive else query.lower()
                    for line in lines:
                        hay = line if case_sensitive else line.lower()
                        if q in hay:
                            filtered_lines.append(line)
            except re.error:
                # Invalid regex → show nothing but avoid crashing
                filtered_lines = []
        else:
            filtered_lines = lines

        # ------------------------------------------------------------
        # 3. Apply line count limit
        # ------------------------------------------------------------
        try:
            limit = int(self.line_count.currentText())
            filtered_lines = filtered_lines[-limit:]
        except ValueError:
            pass

        # ------------------------------------------------------------
        # 4. Update the log display
        # ------------------------------------------------------------
        filtered_text = "\n".join(filtered_lines)
        self._set_text_safely(filtered_text)

        # ------------------------------------------------------------
        # 5. Update Search Results dock
        # ------------------------------------------------------------
        self.update_search_results(filtered_text, query)

        # ------------------------------------------------------------
        # 6. Update match counter for navigation
        # ------------------------------------------------------------
        if query:
            self.match_positions = [
                i for i, line in enumerate(filtered_lines)
            ]
            self.match_label.setText(f"{len(self.match_positions)} matches")
        else:
            self.match_positions = []
            self.match_label.setText("No matches")
        self.highlighter.set_search(
            query,
            regex=use_regex,
            case_sensitive=case_sensitive
        )


    # ----------------------------------------------------------------------
    # LOAD LOG
    # ----------------------------------------------------------------------
    def load_log(self):
        print("LOAD_LOG CALLED — log_path =", getattr(self, "log_path", None))
        try:
            at_bottom = (
                self.text_area.verticalScrollBar().value() ==
                self.text_area.verticalScrollBar().maximum()
            )

            if not os.path.exists(self.log_path):
                self.text_area.setPlainText("Log file not found.")
                logger.warning("LogViewerPage: Log file not found")
                return

            max_lines = int(self.line_count.currentText())

            # ------------------------------------------------------------
            # Incremental tail-f logic (safe version)
            # ------------------------------------------------------------
            with open(self.log_path, "r", encoding="utf-8", errors="replace") as f:
                f.seek(0, os.SEEK_END)
                file_size = f.tell()

                # File truncated (rotation or clear)
                if file_size < self._last_file_pos:
                    self._last_file_pos = 0

                # Seek to last known position
                f.seek(self._last_file_pos)

                # Read only new data
                new_data = f.read()

                # Update offset
                self._last_file_pos = f.tell()

            # ------------------------------------------------------------
            # Merge new data
            # ------------------------------------------------------------
            if new_data:
                self._raw_log_content += new_data

            # Keep only last N lines
            lines = self._raw_log_content.splitlines()
            if len(lines) > max_lines:
                lines = lines[-max_lines:]
                self._raw_log_content = "\n".join(lines)

            # ------------------------------------------------------------
            # Apply full filtering pipeline
            # ------------------------------------------------------------
            self.apply_filter()

            # ------------------------------------------------------------
            # Scroll only if user was already at bottom
            # ------------------------------------------------------------
            if at_bottom:
                self.text_area.moveCursor(QTextCursor.End)

            logger.info("LogViewerPage: Incremental tail-f update complete")

        except Exception as e:
            print("TAIL-F ERROR:", e)  # Debug to console
            logger.error(f"TAIL-F ERROR: {e}", exc_info=True)  # Full traceback in log
            QMessageBox.critical(self, "Error", "Failed to update log view.")

    # ----------------------------------------------------------------------
    # CLEAR LOG
    # ----------------------------------------------------------------------
    def clear_log(self):
        try:
            with open(self.log_path, "w", encoding="utf-8") as f:
                f.write("")
            self.text_area.setPlainText("")
            logger.info("LogViewerPage: Log cleared by admin")
        except Exception as e:
            logger.error(f"LogViewerPage: Failed to clear log: {e}")
            QMessageBox.critical(self, "Error", "Failed to clear log file")

    def export_filtered_results(self):
        try:
            if not self._filtered_text.strip():
                QMessageBox.information(self, "No Data", "There is no filtered data to export.")
                return

            from PySide6.QtWidgets import QFileDialog

            path, _ = QFileDialog.getSaveFileName(
                self,
                "Export Filtered Log",
                "filtered_log.txt",
                "Text Files (*.txt);;All Files (*)"
            )

            if not path:
                return  # user cancelled

            with open(path, "w", encoding="utf-8") as f:
                f.write(self._filtered_text)

            QMessageBox.information(self, "Export Complete", "Filtered log exported successfully.")

        except Exception as e:
            logger.error(f"LogViewerPage: Failed to export filtered results: {e}")
            QMessageBox.critical(self, "Error", "Failed to export filtered results.")

    # ----------------------------------------------------------------------
    # COLOURIZER
    # ----------------------------------------------------------------------
    def colorize(self, text: str) -> str:
        lines = []
        for line in text.splitlines():
            lower = line.lower()

            # Timestamp highlight
            line = re.sub(
                r"^\d{4}-\d{2}-\d{2}[ T]\d{2}:\d{2}:\d{2}(?:,\d+)?",
                lambda m: f'<span style="color:#888;">{m.group(0)}</span>',
                line
            )

            if re.search(r"\berror\b", lower):
                lines.append(f'<span style="color:#ff5555;">{line}</span>')
            elif re.search(r"\bwarning\b|\bwarn\b", lower):
                lines.append(f'<span style="color:#ffaa00;">{line}</span>')
            elif re.search(r"\bdebug\b", lower):
                lines.append(f'<span style="color:#77dd77;">{line}</span>')
            elif re.search(r"\binfo\b", lower):
                lines.append(f'<span style="color:#55aaff;">{line}</span>')
            else:
                lines.append(line)

        return "<br>".join(lines)

    # ----------------------------------------------------------------------
    # HIGHLIGHT MATCHES
    # ----------------------------------------------------------------------
    # def highlight_matches(self, text: str, query: str, current_index: int | None, use_regex: bool):
    def highlight_matches(self, text: str, query: str, current_index: int | None,
                      use_regex: bool, case_sensitive: bool):
        """
        Returns HTML‑safe text with all matches highlighted.
        The current match (if any) is highlighted differently.
        """

        if not query:
            return text

        matches = []

        # ------------------------------------------------------------
        # 1. Build match list
        # ------------------------------------------------------------
        if use_regex:
            try:
                flags = 0 if case_sensitive else re.IGNORECASE
                pattern = re.compile(query, flags)
                matches = list(pattern.finditer(text))
            except re.error:
                return text  # invalid regex → no highlighting
        else:
            if case_sensitive:
                q = query
                qlen = len(q)
                pos = 0
                while True:
                    idx = text.find(q, pos)
                    if idx == -1:
                        break
                    matches.append((idx, idx + qlen))
                    pos = idx + qlen
            else:
                lower = text.lower()
                q = query.lower()
                qlen = len(q)
                pos = 0
                while True:
                    idx = lower.find(q, pos)
                    if idx == -1:
                        break
                    matches.append((idx, idx + qlen))
                    pos = idx + qlen

        # ------------------------------------------------------------
        # 2. Rebuild text with highlight spans
        # ------------------------------------------------------------
        out = []
        last = 0

        for i, match in enumerate(matches):
            start = match.start() if use_regex else match[0]
            end   = match.end()   if use_regex else match[1]

            # Add text before match
            out.append(text[last:start])

            # Current match gets orange highlight
            if current_index is not None and i == current_index:
                out.append(
                    f'<span style="background-color: orange; color: black; font-weight: bold;">'
                    f'{text[start:end]}</span>'
                )
            else:
                out.append(
                    f'<span style="background-color: yellow; color: black;">'
                    f'{text[start:end]}</span>'
                )

            last = end

        # Add remaining text
        out.append(text[last:])

        return "".join(out)

    # ----------------------------------------------------------------------
    # NAVIGATION
    # ----------------------------------------------------------------------
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
        if not self._match_positions or self._current_match_index == -1:
            return

        query = self.search_bar.text().strip()
        use_regex = self.regex_checkbox.isChecked()
        case_sensitive = self.case_checkbox.isChecked()

        # Rebuild highlighted text with the current match emphasized
        highlighted = self.highlight_matches(
            self._filtered_text,
            query,
            self._current_match_index,
            use_regex=use_regex,
            case_sensitive=case_sensitive
        )

        # Apply colourization
        colored = self.colorize(highlighted)
        self.text_area.setHtml(colored)

        # Scroll to the match position
        pos = self._match_positions[self._current_match_index]
        cursor = self.text_area.textCursor()
        cursor.setPosition(pos)
        self.text_area.setTextCursor(cursor)
        self.text_area.ensureCursorVisible()

        # Update match label
        total = len(self._match_positions)
        current = self._current_match_index + 1
        self.match_label.setText(f"{current} of {total}")

    def update_search_results(self, filtered_text, query):
        if not hasattr(self, "search_results_list"):
            return  # Dock not created yet

        self.search_results_list.clear()

        if not query:
            return

        lines = filtered_text.splitlines()

        for idx, line in enumerate(lines, start=1):
            if query.lower() in line.lower():
                item_text = f"{idx}: {line[:120]}"
                self.search_results_list.addItem(item_text)

        # Connect click handler
        self.search_results_list.itemClicked.connect(self.jump_to_result)

    def jump_to_result(self, item):
        text = item.text()
        line_number = int(text.split(":", 1)[0])

        cursor = self.text_area.textCursor()
        cursor.movePosition(QTextCursor.Start)
        cursor.movePosition(QTextCursor.Down, QTextCursor.MoveAnchor, line_number - 1)
        self.text_area.setTextCursor(cursor)
        self.text_area.ensureCursorVisible()

    def _set_text_safely(self, text):
        # Temporarily disable highlighter to avoid update conflicts
        self.highlighter.blockSignals(True)
        self.text_area.blockSignals(True)

        self.text_area.setPlainText(text)

        self.text_area.blockSignals(False)
        self.highlighter.blockSignals(False)

        # Re-run highlighting
        self.highlighter.rehighlight()