# ui/pages/admin/permissions_page.py

from PySide6.QtWidgets import QWidget, QLabel, QVBoxLayout


class PermissionsPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Permissions Page (placeholder)"))