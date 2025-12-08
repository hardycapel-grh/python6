from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLabel,
    QLineEdit, QPushButton, QMessageBox
)
from pymongo import MongoClient
import bcrypt
import sys

class RegistrationApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("User Registration")

        # MongoDB connection
        self.client = MongoClient("mongodb://localhost:27017/")
        self.db = self.client["test"]
        self.users = self.db["users"]

        layout = QVBoxLayout()

        # Username
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Username")
        layout.addWidget(QLabel("Username:"))
        layout.addWidget(self.username_input)

        # Email
        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("Email")
        layout.addWidget(QLabel("Email:"))
        layout.addWidget(self.email_input)

        # Password
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Password")
        self.password_input.setEchoMode(QLineEdit.Password)
        layout.addWidget(QLabel("Password:"))
        layout.addWidget(self.password_input)

        # Confirm Password
        self.confirm_input = QLineEdit()
        self.confirm_input.setPlaceholderText("Confirm Password")
        self.confirm_input.setEchoMode(QLineEdit.Password)
        layout.addWidget(QLabel("Confirm Password:"))
        layout.addWidget(self.confirm_input)

        # Register button
        register_btn = QPushButton("Register")
        register_btn.clicked.connect(self.register_user)
        layout.addWidget(register_btn)

        self.setLayout(layout)

    def register_user(self):
        username = self.username_input.text().strip()
        email = self.email_input.text().strip()
        password = self.password_input.text().encode("utf-8")
        confirm = self.confirm_input.text().encode("utf-8")

        if not username or not email or not password:
            QMessageBox.warning(self, "Input Error", "All fields are required.")
            return

        if password != confirm:
            QMessageBox.warning(self, "Password Error", "Passwords do not match.")
            return

        # Check if user already exists
        if self.users.find_one({"username": username}):
            QMessageBox.warning(self, "Duplicate User", "Username already exists.")
            return

        # Hash password
        hashed = bcrypt.hashpw(password, bcrypt.gensalt())

        # Insert into MongoDB
        self.users.insert_one({
            "username": username,
            "email": email,
            "password_hash": hashed
        })

        QMessageBox.information(self, "Success", f"User '{username}' registered successfully!")

        # Clear fields
        self.username_input.clear()
        self.email_input.clear()
        self.password_input.clear()
        self.confirm_input.clear()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = RegistrationApp()
    window.show()
    sys.exit(app.exec())