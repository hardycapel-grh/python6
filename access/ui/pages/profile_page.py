from datetime import datetime

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QGroupBox, QFormLayout, QMessageBox
)
from PySide6.QtCore import Qt

from ui.dialogs.profile_dialogs import ProfileDialog, ChangePasswordDialog
from ui.components.logger_utils import log_event


class ProfilePage(QWidget):
    def __init__(self, app, mongo, parent=None):
        super().__init__(parent)

        self.app = app
        self.mongo = mongo
        self.user = app.user  # lightweight User object

        # Load full MongoDB user document
        self.user_doc = self.mongo.get_user(self.user.username)

        self._build_ui()
        self._load_user_info()
        self._load_permissions()

        # Default window size
        self.setMinimumSize(900, 500)
        self.resize(900, 500)
    # ---------------------------------------------------------
    # Internal audit helper
    # ---------------------------------------------------------
    def _audit(self, event, details=None):
        entry = {
            "event": event,
            "performed_by": self.user.username,
            "target": self.user.username,
            "timestamp": datetime.utcnow()
        }
        if details:
            entry["details"] = details

        self.mongo.audit_log.insert_one(entry)

    # ---------------------------------------------------------
    # UI Construction
    # ---------------------------------------------------------
    def _build_ui(self):
        layout = QVBoxLayout(self)

        # -------------------------
        # Profile Info Section
        # -------------------------
        profile_box = QGroupBox("My Profile")
        profile_layout = QFormLayout()

        self.lbl_username = QLabel()
        self.lbl_email = QLabel()
        self.lbl_role = QLabel()
        self.lbl_status = QLabel()
        self.lbl_created = QLabel()
        self.lbl_last_login = QLabel()
        self.lbl_theme = QLabel()

        profile_layout.addRow("Username:", self.lbl_username)
        profile_layout.addRow("Email:", self.lbl_email)
        profile_layout.addRow("Role:", self.lbl_role)
        profile_layout.addRow("Status:", self.lbl_status)
        profile_layout.addRow("Created At:", self.lbl_created)
        profile_layout.addRow("Last Login:", self.lbl_last_login)
        profile_layout.addRow("Theme:", self.lbl_theme)

        # Buttons
        btn_row = QHBoxLayout()
        self.btn_edit = QPushButton("Edit Details")
        self.btn_password = QPushButton("Change Password")

        self.btn_edit.clicked.connect(self._edit_details)
        self.btn_password.clicked.connect(self._change_password)

        btn_row.addWidget(self.btn_edit)
        btn_row.addWidget(self.btn_password)
        profile_layout.addRow(btn_row)

        profile_box.setLayout(profile_layout)
        layout.addWidget(profile_box)

        # -------------------------
        # Permissions Section
        # -------------------------
        perm_box = QGroupBox("My Permissions")
        perm_layout = QVBoxLayout()

        self.lbl_permissions = QLabel()
        self.lbl_permissions.setTextInteractionFlags(Qt.TextSelectableByMouse)
        perm_layout.addWidget(self.lbl_permissions)

        perm_box.setLayout(perm_layout)
        layout.addWidget(perm_box)

        layout.addStretch()

    # ---------------------------------------------------------
    # Load Data
    # ---------------------------------------------------------
    def _load_user_info(self):
        doc = self.user_doc

        self.lbl_username.setText(doc.get("username", ""))
        self.lbl_email.setText(doc.get("email", ""))
        self.lbl_role.setText(doc.get("role", ""))
        self.lbl_status.setText(doc.get("status", ""))
        self.lbl_created.setText(str(doc.get("created_at", "")))
        self.lbl_last_login.setText(str(doc.get("last_login", "")))
        self.lbl_theme.setText(doc.get("theme", ""))

    def _load_permissions(self):
        perms = self.user.permissions or []
        if not perms:
            self.lbl_permissions.setText("(No permissions)")
        else:
            self.lbl_permissions.setText("\n".join(sorted(perms)))

    # ---------------------------------------------------------
    # Actions
    # ---------------------------------------------------------
    def _edit_details(self):
        old_doc = self.user_doc.copy()

        dlg = ProfileDialog(self.mongo, self.user_doc, self)
        if dlg.exec():
            new_doc = self.mongo.get_user(self.user.username)
            self.user_doc = new_doc

            changes = {}
            for field in ["email", "role", "status", "theme"]:
                if old_doc.get(field) != new_doc.get(field):
                    changes[field] = {
                        "old": old_doc.get(field),
                        "new": new_doc.get(field)
                    }

            if changes:
                self._audit("profile.update", changes)

            log_event("info", "Profile updated", user=self.user.username)
            self._load_user_info()



    def _change_password(self):
        dlg = ChangePasswordDialog(self.mongo, self.user_doc, self)
        if dlg.exec():
            self._audit("profile.password_change")

            log_event("info", "Password changed", user=self.user.username)
            QMessageBox.information(self, "Success", "Password updated successfully.")


