from PySide6.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout,
    QListWidget, QLabel, QPushButton, QLineEdit, QTextEdit, QComboBox
)
from services.user_service import UserService


class UserManagerPage(QWidget):
    def __init__(self, user):
        super().__init__()
        self.user = user

        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Select a user to view details"))

        title = QLabel("User Manager")
        layout.addWidget(title)

        # Always create UI elements FIRST
        self.user_list = QListWidget()
        self.details_label = QLabel("Select a user to view details")
        self.details_label.setStyleSheet("font-size: 16px;")

        self.add_button = QPushButton("Add User")
        self.edit_button = QPushButton("Edit User")
        self.delete_button = QPushButton("Delete User")

        # Right side layout
        right_layout = QVBoxLayout()
        right_layout.addWidget(self.details_label)
        right_layout.addWidget(self.add_button)
        right_layout.addWidget(self.edit_button)
        right_layout.addWidget(self.delete_button)
        right_layout.addStretch()

        layout.addWidget(self.user_list, 1)
        layout.addLayout(right_layout, 2)

        # Now load users safely
        try:
            self.service = UserService()
            users = self.service.get_all_users()

            # Ensure usernames exist
            usernames = [u.get("username", "<no username>") for u in users]
            self.user_list.addItems(usernames)

        except Exception as e:
            print("Error loading users:", e)
            self.user_list.addItem("Error loading users")

        # Connect after population
        self.user_list.currentItemChanged.connect(self.show_user_details)

    def show_user_details(self, current, previous):
        if not current:
            return

        username = current.text()

        try:
            user = self.service.get_user(username)
        except Exception as e:
            self.details_label.setText(f"Error loading user: {e}")
            return

        if not user:
            self.details_label.setText("User not found")
            return

        details = (
            f"<b>User:</b> {user['username']}<br>"
            f"<b>Role:</b> {user.get('role', 'Unknown')}<br>"
            f"<b>Status:</b> {user.get('status', 'Unknown')}<br>"
        )

        self.details_label.setText(details)

    def apply_permissions(self, perm):
        if perm == "rw":
            return

        # Disable all buttons
        for btn in self.findChildren(QPushButton):
            btn.setEnabled(False)

        # Disable editable widgets
        for t in (QLineEdit, QTextEdit, QComboBox):
            for widget in self.findChildren(t):
                widget.setEnabled(False)

        # Optional banner
        banner = QLabel("Read-Only Mode")
        banner.setStyleSheet("color: orange; font-weight: bold;")
        self.layout().insertWidget(0, banner)