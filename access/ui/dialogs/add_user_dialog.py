from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QComboBox, QListWidget, QListWidgetItem,
    QMessageBox
)
from PySide6.QtCore import Qt
from ui.components.logger import logger
import re


class AddUserDialog(QDialog):
    def __init__(self, user_service, parent=None):
        super().__init__(parent)

        self.user_service = user_service
        self.mongo = user_service.mongo

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
