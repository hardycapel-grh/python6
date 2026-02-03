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

        # Log the attempt
        logger.info(f"Registration attempt: username='{username}', email='{email}'")

        # -----------------------------
        # Required fields
        # -----------------------------
        if not username or not email or not password:
            QMessageBox.warning(self, "Error", "All fields are required")
            logger.warning("Registration failed: missing required fields")
            return

        # -----------------------------
        # Username validation
        # -----------------------------
        if " " in username:
            QMessageBox.warning(self, "Error", "Username cannot contain spaces")
            logger.warning(f"Registration failed: username '{username}' contains spaces")
            return

        if len(username) < 3:
            QMessageBox.warning(self, "Error", "Username must be at least 3 characters long")
            logger.warning(f"Registration failed: username '{username}' too short")
            return

        # -----------------------------
        # Email validation
        # -----------------------------
        if not EMAIL_REGEX.match(email):
            QMessageBox.warning(self, "Error", "Invalid email address")
            logger.warning(f"Registration failed: invalid email '{email}'")
            return

        # -----------------------------
        # Password validation
        # -----------------------------
        if len(password) < 8:
            QMessageBox.warning(self, "Error", "Password must be at least 8 characters long")
            logger.warning(f"Registration failed for '{username}': password too short")
            return

        if not any(c.islower() for c in password):
            QMessageBox.warning(self, "Error", "Password must contain a lowercase letter")
            logger.warning(f"Registration failed for '{username}': missing lowercase letter")
            return

        if not any(c.isupper() for c in password):
            QMessageBox.warning(self, "Error", "Password must contain an uppercase letter")
            logger.warning(f"Registration failed for '{username}': missing uppercase letter")
            return

        if not any(c.isdigit() for c in password):
            QMessageBox.warning(self, "Error", "Password must contain a number")
            logger.warning(f"Registration failed for '{username}': missing number")
            return

        if not any(c in "!@#$%^&*()-_=+[]{};:,.<>?/\\|" for c in password):
            QMessageBox.warning(self, "Error", "Password must contain a special character")
            logger.warning(f"Registration failed for '{username}': missing special character")
            return

        # -----------------------------
        # Hash password
        # -----------------------------
        try:
            hashed_pw = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
        except Exception as e:
            logger.error(f"Registration failed for '{username}': password hashing error: {e}")
            QMessageBox.critical(self, "Error", "Internal error while processing password")
            return

        # -----------------------------
        # Default permissions
        # -----------------------------
        permissions = {
            page: info["default_permission"]
            for page, info in PAGE_REGISTRY.items()
        }
        logger.info(f"Default permissions assigned for '{username}'")

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
            logger.error(f"Registration failed for '{username}': username may already exist")

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