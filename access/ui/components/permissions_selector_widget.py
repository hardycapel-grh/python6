from PySide6.QtWidgets import QWidget, QVBoxLayout, QCheckBox, QLabel, QScrollArea
from PySide6.QtCore import Qt

class PermissionsSelectorWidget(QWidget):
    def __init__(self, mongo, selected=None, parent=None):
        super().__init__(parent)

        self.mongo = mongo
        self.selected = set(selected or [])

        layout = QVBoxLayout(self)

        title = QLabel("User Permissions (Overrides)")
        title.setStyleSheet("font-weight: bold; margin-bottom: 6px;")
        layout.addWidget(title)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        layout.addWidget(scroll)

        container = QWidget()
        self.inner_layout = QVBoxLayout(container)

        # Load all permissions from DB
        all_perms = self.mongo.get_all_permissions()
        self.checkboxes = {}

        for perm in all_perms:
            name = perm["name"]
            cb = QCheckBox(name)
            cb.setChecked(name in self.selected)
            self.checkboxes[name] = cb
            self.inner_layout.addWidget(cb)

        self.inner_layout.addStretch()
        scroll.setWidget(container)

    def get_selected_permissions(self):
        return [
            name for name, cb in self.checkboxes.items()
            if cb.isChecked()
        ]
