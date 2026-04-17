from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QLineEdit, QLabel,
    QPushButton, QHBoxLayout, QMessageBox, QComboBox,
    QListWidget, QListWidgetItem
)

from PySide6.QtGui import QPalette, QColor
from PySide6.QtCore import Qt
from datetime import datetime
import re
import bcrypt
import logging
from services.mongo_service import MongoService

logger = logging.getLogger(__name__)

class AddUserDialog(QDialog):
    def __init__(self, mongo, parent=None):
        super().__init__(parent)
        self.mongo = mongo
        self.setWindowTitle("Add User")

        self.setMinimumWidth(400)

        layout = QVBoxLayout(self)

        # ---------------------------------------------------------
        # Username
        # ---------------------------------------------------------
        layout.addWidget(QLabel("Username:"))
        self.username_input = QLineEdit()
        layout.addWidget(self.username_input)

        # ---------------------------------------------------------
        # Password
        # ---------------------------------------------------------
        layout.addWidget(QLabel("Password:"))
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)
        layout.addWidget(self.password_input)

        self.password_input.textChanged.connect(self._update_password_strength)

        # Password strength indicator
        self.password_strength_label = QLabel("")
        self.password_strength_label.setStyleSheet("color: red;")
        layout.addWidget(self.password_strength_label)

        # ---------------------------------------------------------
        # Email
        # ---------------------------------------------------------
        layout.addWidget(QLabel("Email:"))
        self.email_input = QLineEdit()
        layout.addWidget(self.email_input)

        self.email_input.textChanged.connect(self._validate_email)

        # Email validation label
        self.email_validation_label = QLabel("")
        self.email_validation_label.setStyleSheet("color: red;")
        layout.addWidget(self.email_validation_label)

        # ---------------------------------------------------------
        # Role
        # ---------------------------------------------------------
        layout.addWidget(QLabel("Role:"))
        self.role_combo = QComboBox()
        self.role_combo.addItems(["viewer", "user", "admin"])
        layout.addWidget(self.role_combo)

        # ---------------------------------------------------------
        # Status
        # ---------------------------------------------------------
        layout.addWidget(QLabel("Status:"))
        self.status_combo = QComboBox()
        self.status_combo.addItems(["Active", "Disabled"])
        layout.addWidget(self.status_combo)

        # ---------------------------------------------------------
        # Theme
        # ---------------------------------------------------------
        layout.addWidget(QLabel("Theme:"))
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["light", "dark"])
        layout.addWidget(self.theme_combo)

        # ---------------------------------------------------------
        # Permissions (optional override)
        # ---------------------------------------------------------
        layout.addWidget(QLabel("Permissions (optional override):"))

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

        # ---------------------------------------------------------
        # Buttons
        # ---------------------------------------------------------
        btn_row = QHBoxLayout()
        self.create_btn = QPushButton("Create")
        self.create_btn.clicked.connect(self._create_user)
        btn_row.addWidget(self.create_btn)

        self.create_btn.setEnabled(False)

        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        btn_row.addWidget(cancel_btn)

        layout.addLayout(btn_row)

        # Validation triggers
        self.username_input.textChanged.connect(self._update_create_button_state)
        self.password_input.textChanged.connect(self._update_create_button_state)
        self.email_input.textChanged.connect(self._update_create_button_state)

        self.username_input.setFocus()

    # ---------------------------------------------------------
    # Create user
    # ---------------------------------------------------------
    def _create_user(self):
        username = self.username_input.text().strip()
        email = self.email_input.text().strip()
        password = self.password_input.text().strip()

        # Use same validation as registration
        from services.registration_service import RegistrationService
        validator = RegistrationService(self.user_service)

        valid, error = validator.validate(username, email, password, password)
        if not valid:
            QMessageBox.warning(self, "Validation Error", error)
            return

        # Collect admin-selected permissions (optional)
        selected = self.permissions_list.selectedItems()
        permissions = [i.text() for i in selected]

        # Build user document
        user_doc = self.user_service.mongo.build_user_document(
            username=username,
            email=email,
            password=password,
            role=self.role_combo.currentText(),
            status=self.status_combo.currentText()
        )

        # Only override permissions if admin selected some
        if permissions:
            user_doc["permissions"] = permissions

        # Override theme
        user_doc["theme"] = self.theme_combo.currentText()

        # Create user
        try:
            self.user_service.mongo.create_user(user_doc)
            logger.info(f"User '{username}' created successfully.")
            self.accept()
        except Exception as e:
            logger.error(f"Failed to create user: {e}")
            QMessageBox.critical(self, "Error", f"Failed to create user:\n{e}")

    # ---------------------------------------------------------
    # Enter key handling
    # ---------------------------------------------------------
    def keyPressEvent(self, event):
        if event.key() in (Qt.Key_Return, Qt.Key_Enter):
            if self.permissions_list.hasFocus():
                return
            self._create_user()
            return

        super().keyPressEvent(event)

    # ---------------------------------------------------------
    # Password strength
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

    # ---------------------------------------------------------
    # Email validation
    # ---------------------------------------------------------
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

    # ---------------------------------------------------------
    # Enable/disable Create button
    # ---------------------------------------------------------
    def _update_create_button_state(self):
        email_valid = self._validate_email()
        username_ok = len(self.username_input.text().strip()) > 0
        password_ok = len(self.password_input.text().strip()) > 0

        self.create_btn.setEnabled(email_valid and username_ok and password_ok)




class EditUserDialog(QDialog):
    def __init__(self, user_doc, current_user, parent=None):
        super().__init__(parent)

        self.user_doc = user_doc
        self.current_user = current_user   # ← ADD THIS
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
            # self.mongo.update_user(self.user_doc["_id"], update_doc)
            self.mongo.update_user(
                self.user_doc["_id"],
                update_doc,
                performed_by=self.current_user.username
            )
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



class DeleteUserDialog(QDialog):
    def __init__(self, mongo, user_data, parent=None):
        super().__init__(parent)
        self.mongo = mongo
        self.user_data = user_data
        self.setWindowTitle("Delete User")

        layout = QVBoxLayout(self)
        layout.addWidget(QLabel(f"Are you sure you want to delete '{user_data['username']}'?"))

        btns = QHBoxLayout()
        yes = QPushButton("Delete")
        no = QPushButton("Cancel")
        yes.clicked.connect(self.delete_user)
        no.clicked.connect(self.reject)
        btns.addWidget(yes)
        btns.addWidget(no)
        layout.addLayout(btns)

    def delete_user(self):
        try:
            self.mongo.delete_user(
                self.user_data["_id"],
                performed_by=self.parent().current_user.username
            )
            self.accept()

        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))


class ResetPasswordDialog(QDialog):
    def __init__(self, mongo, username, parent=None):
        super().__init__(parent)
        self.mongo = mongo
        self.username = username
        self.setWindowTitle(f"Reset Password: {username}")

        layout = QVBoxLayout(self)

        self.new_pw = QLineEdit()
        self.new_pw.setEchoMode(QLineEdit.Password)

        self.pw_strength = QLabel("")
        self.pw_strength.setStyleSheet("font-weight: bold;")

        layout.addWidget(QLabel("New Password"))
        layout.addWidget(self.new_pw)
        layout.addWidget(self.pw_strength)

        btns = QHBoxLayout()
        save = QPushButton("Reset")
        cancel = QPushButton("Cancel")

        save.clicked.connect(self.reset_pw)      # ← important
        cancel.clicked.connect(self.reject)

        btns.addWidget(save)
        btns.addWidget(cancel)
        layout.addLayout(btns)

        self.new_pw.setFocus()
        self.new_pw.textChanged.connect(self.update_pw_strength)
        self.new_pw.returnPressed.connect(self.reset_pw)

    def update_pw_strength(self):
        pw = self.new_pw.text()
        if len(pw) < 6:
            self.pw_strength.setText("Weak")
            self.pw_strength.setStyleSheet("color: red; font-weight: bold;")
            return

        score = 0
        if any(c.islower() for c in pw): score += 1
        if any(c.isupper() for c in pw): score += 1
        if any(c.isdigit() for c in pw): score += 1
        if any(not c.isalnum() for c in pw): score += 1

        if score <= 1:
            self.pw_strength.setText("Weak")
            self.pw_strength.setStyleSheet("color: red; font-weight: bold;")
        elif score == 2:
            self.pw_strength.setText("Medium")
            self.pw_strength.setStyleSheet("color: orange; font-weight: bold;")
        else:
            self.pw_strength.setText("Strong")
            self.pw_strength.setStyleSheet("color: green; font-weight: bold;")

    def validate_inputs(self):
        pw = self.new_pw.text().strip()
        if not pw:
            return False, "Password is required."
        if len(pw) < 6:
            return False, "Password must be at least 6 characters."
        return True, None

    def reset_pw(self):
        valid, err = self.validate_inputs()
        if not valid:
            QMessageBox.warning(self, "Invalid Input", err)
            return

        try:
            self.mongo.reset_password(
                self.user_data["_id"],
                self.new_pw.text(),
                performed_by=self.parent().current_user.username
            )
            self.accept()

            from ui.components.toast import Toast
            Toast(self.parent(), "Password reset successfully")

        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

