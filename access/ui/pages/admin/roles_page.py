# ui/pages/admin/roles_page.py

from PySide6.QtWidgets import QWidget, QLabel, QVBoxLayout


class RolesPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Roles Page (placeholder)"))