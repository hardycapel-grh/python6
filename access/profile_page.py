from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton,
    QMessageBox, QFormLayout
)
from PySide6.QtCore import Qt
import bcrypt

from logger import logger
from database import update_user_fields, update_password


class ProfilePage(QWidget):
    def __init__(self, user):
        super().__init__()
        self.title = "Profile"
        self.read_only = False
        self.user = user

        self.build_ui()
        self.load_user_data()

    def build_ui(self):
        layout = QVBoxLayout()

        title = QLabel("Your Profile")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        form = QFormLayout()

        # Username (read-only)
        self.username_field = QLineEdit()
        self.username_field.setReadOnly(True)
        form.addRow("Username:", self.username_field)

        # Role (read-only)
        self.role_field = QLineEdit()
        self.role_field.setReadOnly(True)
        form.addRow("Role:", self.role_field)

        # Email
        self.email_field = QLineEdit()
        form.addRow("Email:", self.email_field)

        # Phone (optional)
        self.phone_field = QLineEdit()
        form.addRow("Phone:", self.phone_field)

        # Theme (optional)
        self.theme_field = QLineEdit()
        form.addRow("Theme:", self.theme_field)

        layout.addLayout(form)

        # -----------------------------
        # Change Password Section
        # -----------------------------
        pw_title = QLabel("Change Password")
        pw_title.setAlignment(Qt.AlignCenter)
        layout.addWidget(pw_title)

        pw_form = QFormLayout()

        self.current_pw = QLineEdit()
        self.current_pw.setEchoMode(QLineEdit.Password)
        pw_form.addRow("Current Password:", self.current_pw)

        self.new_pw = QLineEdit()
        self.new_pw.setEchoMode(QLineEdit.Password)
        pw_form.addRow("New Password:", self.new_pw)

        self.confirm_pw = QLineEdit()
        self.confirm_pw.setEchoMode(QLineEdit.Password)
        pw_form.addRow("Confirm New Password:", self.confirm_pw)

        layout.addLayout(pw_form)

        change_pw_btn = QPushButton("Change Password")
        change_pw_btn.clicked.connect(self.change_password)
        layout.addWidget(change_pw_btn)

        # Save profile button
        save_btn = QPushButton("Save Profile Changes")
        save_btn.clicked.connect(self.save_profile)
        layout.addWidget(save_btn)

        self.setLayout(layout)

    def load_user_data(self):
        """Load user data into the fields, tolerating missing fields."""
        self.username_field.setText(self.user.get("username", ""))
        self.role_field.setText(self.user.get("role", ""))

        self.email_field.setText(self.user.get("email", ""))
        self.phone_field.setText(self.user.get("phone", ""))
        self.theme_field.setText(self.user.get("theme", ""))

        logger.info(f"ProfilePage: Loaded profile for '{self.user.get('username')}'")

    def save_profile(self):
        """Save updated fields back to MongoDB."""
        username = self.user["username"]

        updated_fields = {
            "email": self.email_field.text().strip(),
            "phone": self.phone_field.text().strip(),
            "theme": self.theme_field.text().strip(),
        }

        success = update_user_fields(username, updated_fields)

        if success:
            QMessageBox.information(self, "Success", "Profile updated successfully")
            logger.info(f"ProfilePage: Updated profile for '{username}'")
            self.user.update(updated_fields)
        else:
            QMessageBox.critical(self, "Error", "Failed to update profile")
            logger.error(f"ProfilePage: Failed to update profile for '{username}'")

    def change_password(self):
        # """Validate and update the user's password."""
        print("DEBUG: change_password() called")

        username = self.user["username"]

        current = self.current_pw.text().encode()
        new = self.new_pw.text().encode()
        confirm = self.confirm_pw.text().encode()

        # Check current password
        if not bcrypt.checkpw(current, self.user["password"]):
            QMessageBox.warning(self, "Error", "Current password is incorrect")
            return

        # Check new password validity
        new_pw_text = self.new_pw.text()

        if len(new_pw_text) < 8:
            QMessageBox.warning(self, "Error", "Password must be at least 8 characters long")
            return

        if not any(c.islower() for c in new_pw_text):
            QMessageBox.warning(self, "Error", "Password must contain a lowercase letter")
            return

        if not any(c.isupper() for c in new_pw_text):
            QMessageBox.warning(self, "Error", "Password must contain an uppercase letter")
            return

        if not any(c.isdigit() for c in new_pw_text):
            QMessageBox.warning(self, "Error", "Password must contain a number")
            return

        if not any(c in "!@#$%^&*()-_=+[]{};:,.<>?/\\|" for c in new_pw_text):
            QMessageBox.warning(self, "Error", "Password must contain a special character")
            return

        # Check new passwords match
        if new != confirm:
            QMessageBox.warning(self, "Error", "New passwords do not match")
            return

        # -----------------------------
        # Missing part: actually update password
        # -----------------------------
        hashed = bcrypt.hashpw(new, bcrypt.gensalt())

        if update_password(username, hashed):
            QMessageBox.information(self, "Success", "Password changed successfully")
            logger.info(f"ProfilePage: Password changed for '{username}'")

            # Update local user object
            self.user["password"] = hashed

            # Clear fields
            self.current_pw.clear()
            self.new_pw.clear()
            self.confirm_pw.clear()
        else:
            QMessageBox.critical(self, "Error", "Failed to change password")
            logger.error(f"ProfilePage: Failed to change password for '{username}'")

    def set_read_only(self, readonly: bool):
        """Profile page is always editable except for fixed fields."""
        self.read_only = readonly