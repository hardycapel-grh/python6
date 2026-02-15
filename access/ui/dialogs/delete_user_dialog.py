from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QPushButton, QHBoxLayout
)
from services.user_service import UserService
from PySide6.QtCore import Qt


class DeleteUserDialog(QDialog):
    def __init__(self, username, parent=None):
        super().__init__(parent)

        self.setWindowTitle("Delete User")
        self.resize(350, 150)

        self.username = username
        self.service = UserService()

        layout = QVBoxLayout(self)

        # Warning message
        warning = QLabel(
            f"Are you sure you want to delete the user:\n\n"
            f"<b>{username}</b>\n\n"
            f"This action cannot be undone."
        )
        warning.setTextFormat(Qt.RichText)
        warning.setWordWrap(True)
        layout.addWidget(warning)

        # Buttons
        btn_layout = QHBoxLayout()
        self.delete_btn = QPushButton("Delete")
        self.cancel_btn = QPushButton("Cancel")

        btn_layout.addWidget(self.delete_btn)
        btn_layout.addWidget(self.cancel_btn)
        layout.addLayout(btn_layout)

        self.delete_btn.clicked.connect(self.delete_user)
        self.cancel_btn.clicked.connect(self.reject)

    # ---------------------------------------------------------
    # Delete user from MongoDB
    # ---------------------------------------------------------
    def delete_user(self):
        try:
            self.service.delete_user(self.username)
        except Exception as e:
            from PySide6.QtWidgets import QMessageBox
            QMessageBox.critical(self, "Error", f"Failed to delete user:\n{e}")
            return

        self.accept()