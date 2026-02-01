from PySide6.QtWidgets import (
    QVBoxLayout, QLabel, QLineEdit, QPushButton,
    QMessageBox, QFormLayout, QTextEdit, QComboBox
)
from PySide6.QtCore import Qt
import bcrypt

from ui.components.logger import logger
from database import update_user_fields, update_password
from base_page import BasePage


class ProfilePage(BasePage):
    title = "Profile"

    def __init__(self, user):
        super().__init__()
        self.user = user

        self.build_ui()
        self.load_user_data()

    def build_ui(self):
        layout = QVBoxLayout()
        self.setLayout(layout)

        title = QLabel("Your Profile")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        form = QFormLayout()

        # Username (always read-only)
        self.username_field = QLineEdit(self)
        self.username_field.setReadOnly(True)
        form.addRow("Username:", self.username_field)

        # Role (always read-only)
        self.role_field = QLineEdit(self)
        self.role_field.setReadOnly(True)
        form.addRow("Role:", self.role_field)

        # Editable fields
        self.email_field = QLineEdit(self)
        form.addRow("Email:", self.email_field)

        self.phone_field = QLineEdit(self)
        form.addRow("Phone:", self.phone_field)

        self.theme_field = QLineEdit(self)
        form.addRow("Theme:", self.theme_field)

        layout.addLayout(form)

        # -----------------------------
        # Change Password Section
        # -----------------------------
        pw_title = QLabel("Change Password")
        pw_title.setAlignment(Qt.AlignCenter)
        layout.addWidget(pw_title)

        pw_form = QFormLayout()

        self.current_pw = QLineEdit(self)
        self.current_pw.setEchoMode(QLineEdit.Password)
        pw_form.addRow("Current Password:", self.current_pw)

        self.new_pw = QLineEdit(self)
        self.new_pw.setEchoMode(QLineEdit.Password)
        pw_form.addRow("New Password:", self.new_pw)

        self.confirm_pw = QLineEdit(self)
        self.confirm_pw.setEchoMode(QLineEdit.Password)
        pw_form.addRow("Confirm New Password:", self.confirm_pw)

        layout.addLayout(pw_form)

        # Buttons
        self.change_pw_btn = QPushButton("Change Password", self)
        self.change_pw_btn.clicked.connect(self.change_password)
        layout.addWidget(self.change_pw_btn)

        self.save_btn = QPushButton("Save Profile Changes", self)
        self.save_btn.clicked.connect(self.save_profile)
        layout.addWidget(self.save_btn)

    def load_user_data(self):
        self.username_field.setText(self.user.get("username", ""))
        self.role_field.setText(self.user.get("role", ""))

        self.email_field.setText(self.user.get("email", ""))
        self.phone_field.setText(self.user.get("phone", ""))
        self.theme_field.setText(self.user.get("theme", ""))

        logger.info(f"ProfilePage: Loaded profile for '{self.user.get('username')}'")

    def save_profile(self):
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
        username = self.user["username"]

        current = self.current_pw.text().encode()
        new = self.new_pw.text().encode()
        confirm = self.confirm_pw.text().encode()

        if not bcrypt.checkpw(current, self.user["password"]):
            QMessageBox.warning(self, "Error", "Current password is incorrect")
            return

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

        if new != confirm:
            QMessageBox.warning(self, "Error", "New passwords do not match")
            return

        hashed = bcrypt.hashpw(new, bcrypt.gensalt())

        if update_password(username, hashed):
            QMessageBox.information(self, "Success", "Password changed successfully")
            logger.info(f"ProfilePage: Password changed for '{username}'")

            self.user["password"] = hashed

            self.current_pw.clear()
            self.new_pw.clear()
            self.confirm_pw.clear()
        else:
            QMessageBox.critical(self, "Error", "Failed to change password")
            logger.error(f"ProfilePage: Failed to change password for '{username}'")