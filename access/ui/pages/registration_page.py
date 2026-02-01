from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox, QTextEdit, QComboBox
import bcrypt
import re

from ui.components.logger import logger
from database import create_user
from page_registry import PAGE_REGISTRY

EMAIL_REGEX = re.compile(r"^[^@\s]+@[^@\s]+\.[a-zA-Z0-9]+$")


class RegistrationWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Register")

        layout = QVBoxLayout()

        # Username
        self.username = QLineEdit()
        self.username.setPlaceholderText("Username")

        # Password
        self.password = QLineEdit()
        self.password.setPlaceholderText("Password")
        self.password.setEchoMode(QLineEdit.Password)

        # Email
        self.email = QLineEdit()
        self.email.setPlaceholderText("Email")

        # Register button
        register_btn = QPushButton("Register")
        register_btn.clicked.connect(self.register)

        layout.addWidget(QLabel("Registration Page"))
        layout.addWidget(self.username)
        layout.addWidget(self.password)
        layout.addWidget(self.email)
        layout.addWidget(register_btn)

        self.setLayout(layout)

    def register(self):
        username = self.username.text().strip()
        email = self.email.text().strip()
        password = self.password.text().strip()

        # -----------------------------
        # Required fields
        # -----------------------------
        if not username or not email or not password:
            QMessageBox.warning(self, "Error", "All fields are required")
            logger.warning("Registration failed: missing fields")
            return

        # -----------------------------
        # Username validation
        # -----------------------------
        if " " in username:
            QMessageBox.warning(self, "Error", "Username cannot contain spaces")
            return

        if len(username) < 3:
            QMessageBox.warning(self, "Error", "Username must be at least 3 characters long")
            return

        # -----------------------------
        # Email validation
        # -----------------------------
        if not EMAIL_REGEX.match(email):
            QMessageBox.warning(self, "Error", "Invalid email address")
            logger.warning(f"Registration failed: invalid email '{email}'")
            return

        # -----------------------------
        # Password validation (same rules as change password)
        # -----------------------------
        if len(password) < 8:
            QMessageBox.warning(self, "Error", "Password must be at least 8 characters long")
            return

        if not any(c.islower() for c in password):
            QMessageBox.warning(self, "Error", "Password must contain a lowercase letter")
            return

        if not any(c.isupper() for c in password):
            QMessageBox.warning(self, "Error", "Password must contain an uppercase letter")
            return

        if not any(c.isdigit() for c in password):
            QMessageBox.warning(self, "Error", "Password must contain a number")
            return

        if not any(c in "!@#$%^&*()-_=+[]{};:,.<>?/\\|" for c in password):
            QMessageBox.warning(self, "Error", "Password must contain a special character")
            return

        # -----------------------------
        # Hash password (raw bytes)
        # -----------------------------
        hashed_pw = bcrypt.hashpw(password.encode(), bcrypt.gensalt())

        # -----------------------------
        # Default permissions
        # -----------------------------
        permissions = {
            page: info["default_permission"]
            for page, info in PAGE_REGISTRY.items()
        }

        # -----------------------------
        # Create user in DB
        # -----------------------------
        success = create_user(username, hashed_pw, "user", permissions, email)

        if success:
            QMessageBox.information(self, "Success", "User registered successfully")
            logger.info(f"User '{username}' registered successfully")
            self.close()
        else:
            QMessageBox.critical(self, "Error", "Registration failed")
            logger.error(f"Registration failed for '{username}'")

    def set_read_only(self, ro: bool):
        """Enable or disable editing for all input widgets."""
        for widget in self.findChildren((QLineEdit, QTextEdit, QComboBox)):
            if isinstance(widget, QLineEdit):
                widget.setReadOnly(ro)
            elif isinstance(widget, QTextEdit):
                widget.setReadOnly(ro)
            elif isinstance(widget, QComboBox):
                widget.setEnabled(not ro)

        # Disable buttons that modify data
        for btn in self.findChildren(QPushButton):
            if btn.objectName() not in ("nav", "close", "back"):
                btn.setEnabled(not ro)