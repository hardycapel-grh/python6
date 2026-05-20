# ui/pages/audit_log_page.py
print(">>> USING CORRECT AUDIT LOG PAGE FILE")

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QTableWidget, QTableWidgetItem
)
from PySide6.QtCore import Qt
from datetime import datetime

from services.mongo_service import MongoService
from PySide6.QtWidgets import QDialog, QVBoxLayout, QTextEdit, QPushButton


class AuditLogPage(QWidget):
    def __init__(self, mongo: MongoService, parent=None):
        # print(">>> __init__ START")
        super().__init__(parent)
        self.mongo = mongo
        # print("AuditLogPage created with mongo:", mongo)


        self.setWindowTitle("Audit Log")

        layout = QVBoxLayout(self)

        # -------------------------
        # Filters
        # -------------------------
        filter_layout = QHBoxLayout()

        self.event_filter = QLineEdit()
        self.event_filter.setPlaceholderText("Event (e.g. user.create, login.success)")
        filter_layout.addWidget(QLabel("Event:"))
        filter_layout.addWidget(self.event_filter)

        self.user_filter = QLineEdit()
        self.user_filter.setPlaceholderText("Performed by (username)")
        filter_layout.addWidget(QLabel("User:"))
        filter_layout.addWidget(self.user_filter)

        self.target_filter = QLineEdit()
        self.target_filter.setPlaceholderText("Target (username / id)")
        filter_layout.addWidget(QLabel("Target:"))
        filter_layout.addWidget(self.target_filter)

        self.refresh_btn = QPushButton("Refresh")
        self.refresh_btn.clicked.connect(self.load_data)
        filter_layout.addWidget(self.refresh_btn)

        layout.addLayout(filter_layout)

        # -------------------------
        # Table
        # -------------------------
        self.table = QTableWidget()
        # print(">>> TABLE OBJECT:", self.table)
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(
            ["Timestamp", "Event", "Performed By", "Target", "Details"]
        )
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.cellDoubleClicked.connect(self.on_row_double_clicked)
        layout.addWidget(self.table)

        self.load_data()

    def build_query(self):
        query = {}

        event = self.event_filter.text().strip()
        if event:
            query["event"] = event

        performed_by = self.user_filter.text().strip()
        if performed_by:
            query["performed_by"] = performed_by

        target = self.target_filter.text().strip()
        if target:
            query["target"] = target

        return query

    def load_data(self):
        query = self.build_query()

        cursor = self.mongo.audit_log.find(query).sort("timestamp", -1).limit(500)

        rows = list(cursor)
        self.table.setRowCount(len(rows))

        for row_idx, doc in enumerate(rows):
            ts = doc.get("timestamp")
            if isinstance(ts, datetime):
                ts_str = ts.strftime("%Y-%m-%d %H:%M:%S")
            else:
                ts_str = str(ts)

            event = doc.get("event", "")
            performed_by = doc.get("performed_by", "")
            target = doc.get("target", "")
            details = doc.get("details", "")

            self.table.setItem(row_idx, 0, QTableWidgetItem(ts_str))
            self.table.setItem(row_idx, 1, QTableWidgetItem(event))
            self.table.setItem(row_idx, 2, QTableWidgetItem(performed_by))
            self.table.setItem(row_idx, 3, QTableWidgetItem(str(target)))
            self.table.setItem(row_idx, 4, QTableWidgetItem(str(details)))



    def on_row_double_clicked(self, row, col):
        doc = {
            "timestamp": self.table.item(row, 0).text(),
            "event": self.table.item(row, 1).text(),
            "performed_by": self.table.item(row, 2).text(),
            "target": self.table.item(row, 3).text(),
            "details": self.table.item(row, 4).text(),
        }

        dlg = QDialog(self)
        dlg.setWindowTitle("Audit Log Entry Details")

        layout = QVBoxLayout(dlg)

        text = QTextEdit()
        text.setReadOnly(True)

        # Pretty formatting
        formatted = (
            f"Timestamp: {doc['timestamp']}\n"
            f"Event: {doc['event']}\n"
            f"Performed By: {doc['performed_by']}\n"
            f"Target: {doc['target']}\n"
            f"Details:\n{doc['details']}"
        )

        text.setText(formatted)
        layout.addWidget(text)

        close_btn = QPushButton("Close")
        close_btn.clicked.connect(dlg.accept)
        layout.addWidget(close_btn)

        dlg.exec()


