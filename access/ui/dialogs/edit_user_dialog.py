from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QComboBox, QMessageBox
)
from services.user_service import UserService


class EditUserDialog(QDialog):
    def __init__(self, username, parent=None):
        super().__init__(parent)

        self.setWindowTitle(f"Edit User: {username}")
        self.resize(400, 250)

        self.service = UserService()
        self.username = username

        # Load user data
        self.user = self.service.get_user(username)
        if not self.user:
            QMessageBox.critical(self, "Error", "User not found")
            self.close()
            return

        layout = QVBoxLayout(self)

        # Username (read-only)
        layout.addWidget(QLabel("Username:"))
        self.username_input = QLineEdit(username)
        self.username_input.setReadOnly(True)
        layout.addWidget(self.username_input)

        # Role
        layout.addWidget(QLabel("Role:"))
        self.role_dropdown = QComboBox()
        self.role_dropdown.addItems(["User", "Support", "Manager", "Admin"])
        self.role_dropdown.setCurrentText(self.user.get("role", "User"))
        layout.addWidget(self.role_dropdown)

        # Status
        layout.addWidget(QLabel("Status:"))
        self.status_dropdown = QComboBox()
        self.status_dropdown.addItems(["Active", "Disabled"])
        self.status_dropdown.setCurrentText(self.user.get("status", "Active"))
        layout.addWidget(self.status_dropdown)

        # Buttons
        btn_layout = QHBoxLayout()
        self.save_btn = QPushButton("Save Changes")
        self.cancel_btn = QPushButton("Cancel")
        btn_layout.addWidget(self.save_btn)
        btn_layout.addWidget(self.cancel_btn)
        layout.addLayout(btn_layout)

        self.save_btn.clicked.connect(self.save_changes)
        self.cancel_btn.clicked.connect(self.reject)

    # ---------------------------------------------------------
    # Save changes to MongoDB
    # ---------------------------------------------------------
    def save_changes(self):
        new_role = self.role_dropdown.currentText()
        new_status = self.status_dropdown.currentText()

        updates = {
            "role": new_role,
            "status": new_status,
            "permissions": self.service.get_role_permissions(new_role)
        }

        try:
            self.service.update_user(self.username, updates)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to update user:\n{e}")
            return

        QMessageBox.information(self, "Success", "User updated successfully.")
        self.accept()