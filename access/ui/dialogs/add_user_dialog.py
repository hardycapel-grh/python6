from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QComboBox, QMessageBox
)
import secrets
import string
from services.user_service import UserService


class AddUserDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowTitle("Add New User")
        self.resize(400, 250)

        layout = QVBoxLayout(self)

        # Username
        layout.addWidget(QLabel("Username:"))
        self.username_input = QLineEdit()
        layout.addWidget(self.username_input)

        # Role
        layout.addWidget(QLabel("Role:"))
        self.role_dropdown = QComboBox()
        self.role_dropdown.addItems(["User", "Support", "Manager", "Admin"])
        layout.addWidget(self.role_dropdown)

        # Status
        layout.addWidget(QLabel("Status:"))
        self.status_dropdown = QComboBox()
        self.status_dropdown.addItems(["Active", "Disabled"])
        layout.addWidget(self.status_dropdown)

        # Buttons
        btn_layout = QHBoxLayout()
        self.create_btn = QPushButton("Create User")
        self.cancel_btn = QPushButton("Cancel")
        btn_layout.addWidget(self.create_btn)
        btn_layout.addWidget(self.cancel_btn)
        layout.addLayout(btn_layout)

        self.create_btn.clicked.connect(self.create_user)
        self.cancel_btn.clicked.connect(self.reject)

        self.service = UserService()

    # ---------------------------------------------------------
    # Generate a secure temporary password
    # ---------------------------------------------------------
    def generate_temp_password(self, length=10):
        alphabet = string.ascii_letters + string.digits + "!@#$%^&*"
        return ''.join(secrets.choice(alphabet) for _ in range(length))

    # ---------------------------------------------------------
    # Create user in database
    # ---------------------------------------------------------
    def create_user(self):
        username = self.username_input.text().strip()
        role = self.role_dropdown.currentText()
        status = self.status_dropdown.currentText()

        if not username:
            QMessageBox.warning(self, "Missing Info", "Username cannot be empty.")
            return

        # Check if user already exists
        if self.service.get_user(username):
            QMessageBox.warning(self, "Duplicate User", "A user with that username already exists.")
            return

        temp_password = self.generate_temp_password()

        try:
            self.service.create_user(
                username=username,
                password=temp_password,
                role=role,
                status=status
            )
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to create user:\n{e}")
            return

        QMessageBox.information(
            self,
            "User Created",
            f"User '{username}' created successfully.\n\n"
            f"Temporary password:\n\n{temp_password}\n\n"
            "Make sure to give this password to the user."
        )

        self.accept()