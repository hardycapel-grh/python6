from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QLineEdit,
    QPushButton, QMessageBox
)
from services.user_service import UserService
import bcrypt


class ForcePasswordChangeWindow(QDialog):
    def __init__(self, username, parent=None):
        super().__init__(parent)

        self.setWindowTitle("Change Your Password")
        self.resize(400, 260)

        self.username = username
        self.service = UserService()

        layout = QVBoxLayout(self)

        # Header
        header = QLabel(
            f"<b>{username}</b>, you must change your password before continuing."
        )
        header.setWordWrap(True)
        layout.addWidget(header)

        # Old password
        layout.addWidget(QLabel("Current Password:"))
        self.old_input = QLineEdit()
        self.old_input.setEchoMode(QLineEdit.Password)
        layout.addWidget(self.old_input)

        # New password
        layout.addWidget(QLabel("New Password:"))
        self.new_input = QLineEdit()
        self.new_input.setEchoMode(QLineEdit.Password)
        layout.addWidget(self.new_input)

        # Confirm new password
        layout.addWidget(QLabel("Confirm New Password:"))
        self.confirm_input = QLineEdit()
        self.confirm_input.setEchoMode(QLineEdit.Password)
        layout.addWidget(self.confirm_input)

        # Save button
        self.save_btn = QPushButton("Update Password")
        layout.addWidget(self.save_btn)

        self.save_btn.clicked.connect(self.update_password)

    # ---------------------------------------------------------
    # Validate and update password
    # ---------------------------------------------------------
    def update_password(self):
        old = self.old_input.text().strip()
        new = self.new_input.text().strip()
        confirm = self.confirm_input.text().strip()

        if not old or not new or not confirm:
            QMessageBox.warning(self, "Missing Fields", "All fields are required.")
            return

        if new != confirm:
            QMessageBox.warning(self, "Mismatch", "New passwords do not match.")
            return

        user = self.service.get_user(self.username)
        stored_hash = user.get("password_hash")

        # Verify old password
        if not bcrypt.checkpw(old.encode(), stored_hash.encode()):
            QMessageBox.warning(self, "Incorrect Password", "Current password is wrong.")
            return

        # Hash new password
        new_hash = self.service.hash_password(new)

        updates = {
            "password_hash": new_hash,
            "must_change_password": False
        }

        self.service.update_user(self.username, updates)

        QMessageBox.information(self, "Success", "Password updated successfully.")
        self.accept()