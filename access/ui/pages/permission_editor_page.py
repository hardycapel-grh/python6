from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QComboBox,
    QCheckBox, QPushButton, QMessageBox, QGroupBox
)
from services.mongo_service import MongoService
from models.user import User


PERMISSION_REGISTRY = {
    "logs": ["logs.read", "logs.write"],
    "users": ["users.read", "users.write"],
    "permissions": ["permissions.read", "permissions.write"],
    "system": ["system.read", "system.write"],
}

class PermissionEditorPage(QWidget):
    REQUIRED_PERMISSION = "permissions.read"

    def __init__(self, current_user, parent=None):
        super().__init__(parent)
        self.current_user = current_user

        self.mongo = MongoService()
        self.user_cache = {}   # username → User object
        self.checkboxes = {}   # feature → {read: QCheckBox, write: QCheckBox}

        layout = QVBoxLayout(self)

        # User selector
        user_row = QHBoxLayout()
        user_row.addWidget(QLabel("Select User:"))

        self.user_dropdown = QComboBox()
        self.user_dropdown.currentTextChanged.connect(self.load_user_permissions)
        user_row.addWidget(self.user_dropdown)

        layout.addLayout(user_row)

        # Permission groups
        for feature, perms in PERMISSION_REGISTRY.items():
            group = QGroupBox(feature.capitalize())
            group_layout = QHBoxLayout()

            read_perm, write_perm = perms

            read_cb = QCheckBox("Read")
            write_cb = QCheckBox("Write")

            group_layout.addWidget(read_cb)
            group_layout.addWidget(write_cb)
            group.setLayout(group_layout)

            layout.addWidget(group)

            self.checkboxes[feature] = {
                "read": read_cb,
                "write": write_cb
            }

        # Save button
        self.save_btn = QPushButton("Save Permissions")
        self.save_btn.clicked.connect(self.save_permissions)
        layout.addWidget(self.save_btn)

        # Load users
        self.load_users()

        # Enforce read-only if no write permission
        if not self.current_user.has_permission("permissions.write"):
            self._set_read_only()

    def _set_read_only(self):
        for feature, boxes in self.checkboxes.items():
            boxes["read"].setEnabled(False)
            boxes["write"].setEnabled(False)

        self.save_btn.setEnabled(False)

        banner = QLabel("Read-Only Mode")
        banner.setStyleSheet("color: orange; font-weight: bold;")
        self.layout().insertWidget(0, banner)

    def load_users(self):
        users = self.mongo.db.users.find({}, {"_id": 0})
        for u in users:
            user_obj = User(
                username=u["username"],
                role=u["role"],
                permissions=u.get("permissions", [])
            )
            self.user_cache[u["username"]] = user_obj
            self.user_dropdown.addItem(u["username"])

    def load_user_permissions(self, username):
        if not username:
            return

        user = self.user_cache[username]

        for feature, boxes in self.checkboxes.items():
            boxes["read"].setChecked(False)
            boxes["write"].setChecked(False)

        for feature, perms in PERMISSION_REGISTRY.items():
            read_perm, write_perm = perms

            if read_perm in user.permissions:
                self.checkboxes[feature]["read"].setChecked(True)

            if write_perm in user.permissions:
                self.checkboxes[feature]["write"].setChecked(True)

    def save_permissions(self):
        if not self.current_user.has_permission("permissions.write"):
            QMessageBox.warning(self, "Permission Denied",
                                "You do not have permission to modify permissions.")
            return

        username = self.user_dropdown.currentText()
        user = self.user_cache[username]

        new_permissions = []

        for feature, perms in PERMISSION_REGISTRY.items():
            read_perm, write_perm = perms

            if self.checkboxes[feature]["read"].isChecked():
                new_permissions.append(read_perm)

            if self.checkboxes[feature]["write"].isChecked():
                new_permissions.append(write_perm)

        self.mongo.db.users.update_one(
            {"username": username},
            {"$set": {"permissions": new_permissions}}
        )

        user.permissions = new_permissions

        QMessageBox.information(self, "Success", "Permissions updated successfully.")