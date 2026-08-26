from PySide6.QtWidgets import QStyledItemDelegate, QDialog, QVBoxLayout, QTextEdit
from PySide6.QtGui import QTextOption
import json

class JsonPrettyDelegate(QStyledItemDelegate):
    """Pretty‑print JSON/dict fields in a QTableView."""

    def displayText(self, value, locale):
        """What appears in the table cell."""
        try:
            if isinstance(value, dict):
                # Short preview
                return json.dumps(value, indent=2)[:40] + " ..."
            return str(value)
        except Exception:
            return str(value)

    def createEditor(self, parent, option, index):
        """Open a popup dialog showing full JSON."""
        value = index.data()

        dlg = QDialog(parent)
        dlg.setWindowTitle("Audit Details")

        layout = QVBoxLayout(dlg)

        text = QTextEdit()
        text.setReadOnly(True)
        text.setWordWrapMode(QTextOption.NoWrap)

        try:
            if isinstance(value, dict):
                pretty = json.dumps(value, indent=4)
            else:
                pretty = str(value)
        except Exception:
            pretty = str(value)

        text.setText(pretty)
        layout.addWidget(text)

        dlg.resize(600, 400)
        dlg.exec()

        return None  # No inline editor
