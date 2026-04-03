# ui/pages/admin/audit_log_page.py

from PySide6.QtWidgets import QWidget, QLabel, QVBoxLayout


class AuditLogPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Audit Log Page (placeholder)"))