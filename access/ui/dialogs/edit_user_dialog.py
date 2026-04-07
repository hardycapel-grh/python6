from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QComboBox, QListWidget, QListWidgetItem,
    QMessageBox
)
from PySide6.QtCore import Qt
from services.mongo_service import MongoService
from ui.components.logger import logger
import bcrypt
import re


class EditUserDialog(QDialog):

    def __init__(self, user_doc, parent=None):
        super().__init__(parent)

        self.user_doc = user_doc
        self.mongo = MongoService()

        self.setWindowTitle(f"Edit User: {user_doc['username']}")
        self.setMinimumWidth(400)

        layout = QVBoxLayout(self)

        # ---------------------------------------------------------
        # Username
        # ---------------------------------------------------------
        layout.addWidget(QLabel("Username:"))
        self.username_input = QLineEdit(user_doc["username"])
        layout.addWidget(self.username_input)

        # ---------------------------------------------------------
        # Password (blank = unchanged)
        # ---------------------------------------------------------
        layout.addWidget(QLabel("New Password (leave blank to keep existing):"))
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)
        layout.addWidget(self.password_input)

        self.password_input.textChanged.connect(self._update_password_strength)

        self.password_strength_label = QLabel("")
        self.password_strength_label.setStyleSheet("color: red;")
        layout.addWidget(self.password_strength_label)

        # ---------------------------------------------------------
        # Email
        # ---------------------------------------------------------
        layout.addWidget(QLabel("Email:"))
        self.email_input = QLineEdit(user_doc["email"])
        layout.addWidget(self.email_input)

        self.email_input.textChanged.connect(self._validate_email)

        self.email_validation_label = QLabel("")
        self.email_validation_label.setStyleSheet("color: red;")
        layout.addWidget(self.email_validation_label)

        # ---------------------------------------------------------
        # Role
        # ---------------------------------------------------------
        layout.addWidget(QLabel("Role:"))
        self.role_combo = QComboBox()
        self.role_combo.addItems(["viewer", "user", "admin"])
        self.role_combo.setCurrentText(user_doc["role"])
        layout.addWidget(self.role_combo)


        # ---------------------------------------------------------
        # Status
        # ---------------------------------------------------------
        layout.addWidget(QLabel("Status:"))
        self.status_combo = QComboBox()
        self.status_combo.addItems(["Active", "Disabled"])
        self.status_combo.setCurrentText(user_doc["status"])
        layout.addWidget(self.status_combo)

        # ---------------------------------------------------------
        # Theme
        # ---------------------------------------------------------
        layout.addWidget(QLabel("Theme:"))
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["light", "dark"])
        self.theme_combo.setCurrentText(user_doc.get("theme", "light"))
        layout.addWidget(self.theme_combo)

        # ---------------------------------------------------------
        # Permissions
        # ---------------------------------------------------------
        layout.addWidget(QLabel("Permissions:"))

        self.permissions_list = QListWidget()
        self.permissions_list.setSelectionMode(QListWidget.MultiSelection)

        all_permissions = [
            "logs.read", "logs.write",
            "users.read", "users.write",
            "permissions.read", "permissions.write",
            "system.read", "system.write",
            "admin.access"
        ]

        for perm in all_permissions:
            item = QListWidgetItem(perm)
            self.permissions_list.addItem(item)

        layout.addWidget(self.permissions_list)

        # Pre-select existing permissions
        for i in range(self.permissions_list.count()):
            item = self.permissions_list.item(i)
            if item.text() in user_doc["permissions"]:
                item.setSelected(True)

        # ---------------------------------------------------------
        # Buttons
        # ---------------------------------------------------------
        btn_row = QHBoxLayout()
        self.save_btn = QPushButton("Save")
        self.save_btn.clicked.connect(self._save_user)
        btn_row.addWidget(self.save_btn)

        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        btn_row.addWidget(cancel_btn)

        layout.addLayout(btn_row)

        # Validation connections
        self.username_input.textChanged.connect(self._update_save_button_state)
        self.password_input.textChanged.connect(self._update_save_button_state)
        self.email_input.textChanged.connect(self._update_save_button_state)

        self.email_input.textChanged.connect(self._validate_email)

        self._validate_email()
        self._update_save_button_state()

    # ---------------------------------------------------------
    # Save user
    # ---------------------------------------------------------
    def _save_user(self):
        username = self.username_input.text().strip()
        email = self.email_input.text().strip()
        new_password = self.password_input.text().strip()

        if not username or not email:
            QMessageBox.warning(self, "Missing Fields", "Username and email are required.")
            return

        # Collect permissions
        selected = self.permissions_list.selectedItems()
        permissions = [i.text() for i in selected]

        update_doc = {
            "username": username,
            "email": email,
            "role": self.role_combo.currentText(),
            "permissions": permissions,
            "status": self.status_combo.currentText(),
            "theme": self.theme_combo.currentText()
        }

        # Only update password if provided
        if new_password:
            update_doc["password_hash"] = bcrypt.hashpw(new_password.encode(), bcrypt.gensalt()).decode()

        try:
            self.mongo.update_user(self.user_doc["_id"], update_doc)
            logger.info(f"User '{username}' updated successfully.")
            self.accept()
        except Exception as e:
            logger.error(f"Failed to update user: {e}")
            QMessageBox.critical(self, "Error", f"Failed to update user:\n{e}")

    # ---------------------------------------------------------
    # Shared validation + presets
    # ---------------------------------------------------------
    def _update_password_strength(self):
        pwd = self.password_input.text()

        score = 0
        if len(pwd) >= 8: score += 1
        if len(pwd) >= 12: score += 1
        if any(c.islower() for c in pwd): score += 1
        if any(c.isupper() for c in pwd): score += 1
        if any(c.isdigit() for c in pwd): score += 1
        if any(c in "!@#$%^&*()-_=+[]{};:,.<>?/\\|" for c in pwd): score += 1

        if score <= 2:
            text, color = "Weak", "red"
        elif score <= 4:
            text, color = "Fair", "orange"
        elif score <= 6:
            text, color = "Good", "goldenrod"
        else:
            text, color = "Strong", "green"

        self.password_strength_label.setText(f"Strength: {text}")
        self.password_strength_label.setStyleSheet(f"color: {color}; font-weight: bold;")

    def _validate_email(self):
        email = self.email_input.text().strip()
        pattern = r"^[\w\.-]+@[\w\.-]+\.\w+$"

        if re.match(pattern, email):
            self.email_validation_label.setText("Valid email")
            self.email_validation_label.setStyleSheet("color: green; font-weight: bold;")
            return True
        else:
            self.email_validation_label.setText("Invalid email format")
            self.email_validation_label.setStyleSheet("color: red; font-weight: bold;")
            return False

    def _update_save_button_state(self):
        email_valid = self._validate_email()
        username_ok = len(self.username_input.text().strip()) > 0

        self.save_btn.setEnabled(email_valid and username_ok)

    def _apply_role_preset(self):
        role = self.role_combo.currentText()
        preset = self.ROLE_PRESETS.get(role, [])

        # Clear all selections
        for i in range(self.permissions_list.count()):
            item = self.permissions_list.item(i)
            item.setSelected(False)

        # Apply preset
        for i in range(self.permissions_list.count()):
            item = self.permissions_list.item(i)
            if item.text() in preset:
                item.setSelected(True)
