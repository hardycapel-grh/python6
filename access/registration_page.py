from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox
import bcrypt

from logger import logger
from database import create_user
from page_registry import PAGE_REGISTRY

import re

EMAIL_REGEX = re.compile(r"^[^@\s]+@[^@\s]+\.[a-zA-Z0-9]+$")


class RegistrationWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Register")

        layout = QVBoxLayout()

        self.username = QLineEdit()
        self.username.setPlaceholderText("Username")

        self.email = QLineEdit()
        self.email.setPlaceholderText("Email")

        self.password = QLineEdit()
        self.password.setPlaceholderText("Password")
        self.password.setEchoMode(QLineEdit.Password)

        register_btn = QPushButton("Register")
        register_btn.clicked.connect(self.register)

        layout.addWidget(QLabel("Registration Page"))
        layout.addWidget(self.username)
        layout.addWidget(self.email)
        layout.addWidget(self.password)
        layout.addWidget(register_btn)

        self.setLayout(layout)

    def register(self):
        username = self.username.text().strip()
        email = self.email.text().strip()
        password = self.password.text().strip()

        if not username or not email or not password:
            QMessageBox.warning(self, "Error", "All fields are required")
            logger.warning("Registration failed: missing fields")
            return

        # Basic email validation
        # if "@" not in email or "." not in email:
        #     QMessageBox.warning(self, "Error", "Invalid email address")
        #     logger.warning(f"Registration failed: invalid email '{email}'")
        #     return
        
        if not EMAIL_REGEX.match(email):
            QMessageBox.warning(self, "Error", "Invalid email address")
            logger.warning(f"Registration failed: invalid email '{email}'")
            return

        hashed_pw = bcrypt.hashpw(password.encode(), bcrypt.gensalt())

        # Default permissions from registry
        permissions = {
            page: info["default_permission"]
            for page, info in PAGE_REGISTRY.items()
        }

        success = create_user(username, hashed_pw, "user", permissions, email)

        if success:
            QMessageBox.information(self, "Success", "User registered successfully")
            logger.info(f"User '{username}' registered successfully")
            self.close()
        else:
            QMessageBox.critical(self, "Error", "Registration failed")