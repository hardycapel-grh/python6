from PySide6.QtGui import QSyntaxHighlighter, QTextCharFormat, QColor
import re

class SearchHighlighter(QSyntaxHighlighter):
    def __init__(self, parent):
        super().__init__(parent)
        self.query = ""
        self.regex = False
        self.case_sensitive = False

    def set_search(self, query, regex=False, case_sensitive=False):
        self.query = query
        self.regex = regex
        self.case_sensitive = case_sensitive
        self.rehighlight()

    def highlightBlock(self, text):
        if not self.query:
            return

        flags = 0 if self.case_sensitive else re.IGNORECASE

        try:
            if self.regex:
                pattern = re.compile(self.query, flags)
                matches = pattern.finditer(text)
            else:
                q = self.query if self.case_sensitive else self.query.lower()
                hay = text if self.case_sensitive else text.lower()
                matches = []
                start = 0
                while True:
                    idx = hay.find(q, start)
                    if idx == -1:
                        break
                    matches.append((idx, len(q)))
                    start = idx + len(q)
        except re.error:
            return

        fmt = QTextCharFormat()
        fmt.setBackground(QColor("#ffff66"))  # soft yellow

        if self.regex:
            for m in matches:
                start = m.start()
                length = m.end() - m.start()
                self.setFormat(start, length, fmt)
        else:
            for start, length in matches:
                self.setFormat(start, length, fmt)