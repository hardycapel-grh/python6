from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QListWidget, QPushButton, QMessageBox,
    QComboBox, QLabel, QLineEdit
)

from database import get_all_users, delete_user
from permission_editor_dialog import PermissionEditorDialog
from logger import logger


class UserManagerDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("User Manager")

        layout = QVBoxLayout()

        # Search bar
        self.search_bar = QLineEdit()
        self.search_bar.setPlaceholderText("Search by username or email...")
        self.search_bar.textChanged.connect(self.load_users)
        layout.addWidget(self.search_bar)

        # Sort dropdown
        sort_label = QLabel("Sort By:")
        self.sort_box = QComboBox()
        self.sort_box.addItems(["Username", "Email"])
        self.sort_box.currentIndexChanged.connect(self.load_users)

        layout.addWidget(sort_label)
        layout.addWidget(self.sort_box)

        # User list
        self.user_list = QListWidget()
        self.user_list.itemDoubleClicked.connect(self.edit_user)
        layout.addWidget(self.user_list)

        # Buttons
        self.edit_btn = QPushButton("Edit Permissions")
        self.edit_btn.clicked.connect(self.edit_user)
        layout.addWidget(self.edit_btn)

        self.delete_btn = QPushButton("Delete User")
        self.delete_btn.clicked.connect(self.delete_user_action)
        layout.addWidget(self.delete_btn)

        self.setLayout(layout)

        # Load users into the list
        self.load_users()

    def load_users(self):
        """Load and filter users from the database into the list widget."""
        self.user_list.clear()
        users = get_all_users()

        # Extract username + email
        user_entries = []
        for u in users:
            username = u.get("username", "unknown")
            email = u.get("email", "(no email)")
            user_entries.append((username, email))

        # Apply search filter
        query = self.search_bar.text().strip().lower()
        if query:
            user_entries = [
                (u, e) for (u, e) in user_entries
                if query in u.lower() or query in e.lower()
            ]

        # Sort based on dropdown
        sort_mode = self.sort_box.currentText()

        if sort_mode == "Username":
            user_entries.sort(key=lambda x: x[0].lower())
        elif sort_mode == "Email":
            user_entries.sort(key=lambda x: x[1].lower())

        # Add to list
        for username, email in user_entries:
            display = f"{username}  —  {email}"
            self.user_list.addItem(display)

        logger.info(f"User Manager loaded user list (sorted by {sort_mode}, search='{query}')")

    def get_selected_username(self):
        """Return the selected username (strip email part)."""
        selected = self.user_list.currentItem()
        if not selected:
            QMessageBox.warning(self, "Error", "Please select a user")
            return None

        text = selected.text()
        username = text.split("—")[0].strip()
        return username

    def edit_user(self):
        """Open the Permission Editor for the selected user."""
        username = self.get_selected_username()
        if not username:
            return

        logger.info(f"Admin opened Permission Editor for '{username}'")

        dlg = PermissionEditorDialog(username, self)
        dlg.exec()

        # Refresh list after editing
        self.load_users()

    def delete_user_action(self):
        """Delete the selected user after confirmation."""
        username = self.get_selected_username()
        if not username:
            return

        if username == "admin":
            QMessageBox.warning(self, "Error", "You cannot delete the main admin account")
            logger.warning("Attempted to delete protected admin account")
            return

        confirm = QMessageBox.question(
            self,
            "Confirm Delete",
            f"Are you sure you want to delete '{username}'?"
        )

        if confirm != QMessageBox.Yes:
            return

        if delete_user(username):
            QMessageBox.information(self, "Success", f"User '{username}' deleted")
            logger.info(f"User '{username}' deleted by admin")
            self.load_users()
        else:
            QMessageBox.critical(self, "Error", "Failed to delete user")
            logger.error(f"Failed to delete user '{username}'")