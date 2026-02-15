from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QPushButton, QLineEdit,
    QHBoxLayout, QMessageBox
)
from services.user_service import UserService
import secrets
import string


class ResetPasswordDialog(QDialog):
    def __init__(self, username, parent=None):
        super().__init__(parent)

        self.setWindowTitle("Reset Password")
        self.resize(400, 200)

        self.username = username
        self.service = UserService()

        layout = QVBoxLayout(self)

        # Username label
        layout.addWidget(QLabel(f"Reset password for user: <b>{username}</b>"))

        # Temporary password field
        layout.addWidget(QLabel("New Temporary Password:"))
        self.password_input = QLineEdit()
        self.password_input.setReadOnly(True)
        layout.addWidget(self.password_input)

        # Generate button
        self.generate_btn = QPushButton("Generate Password")
        layout.addWidget(self.generate_btn)

        # Buttons
        btn_layout = QHBoxLayout()
        self.save_btn = QPushButton("Apply Reset")
        self.cancel_btn = QPushButton("Cancel")
        btn_layout.addWidget(self.save_btn)
        btn_layout.addWidget(self.cancel_btn)
        layout.addLayout(btn_layout)

        # Signals
        self.generate_btn.clicked.connect(self.generate_password)
        self.save_btn.clicked.connect(self.apply_reset)
        self.cancel_btn.clicked.connect(self.reject)

        # Enable HTML formatting
        from PySide6.QtCore import Qt
        for widget in layout.children():
            if isinstance(widget, QLabel):
                widget.setTextFormat(Qt.RichText)

    # ---------------------------------------------------------
    # Generate a secure temporary password
    # ---------------------------------------------------------
    def generate_password(self):
        alphabet = string.ascii_letters + string.digits + "!@#$%^&*"
        temp_password = ''.join(secrets.choice(alphabet) for _ in range(10))
        self.password_input.setText(temp_password)

    # ---------------------------------------------------------
    # Apply password reset
    # ---------------------------------------------------------
    def apply_reset(self):
        new_password = self.password_input.text().strip()

        if not new_password:
            QMessageBox.warning(self, "Missing Password", "Generate a password first.")
            return

        try:
            hashed = self.service.hash_password(new_password)

            updates = {
                "password_hash": hashed,
                "must_change_password": True
            }

            self.service.update_user(self.username, updates)

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to reset password:\n{e}")
            return

        QMessageBox.information(
            self,
            "Password Reset",
            f"Password reset successfully.\n\n"
            f"New temporary password:\n\n{new_password}\n\n"
            "Give this password to the user."
        )

        self.accept()