from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLabel,
    QLineEdit, QPushButton, QMessageBox
)
from pymongo import MongoClient
import bcrypt
import sys

class LoginApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("User Login")

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

        # Password
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Password")
        self.password_input.setEchoMode(QLineEdit.Password)
        layout.addWidget(QLabel("Password:"))
        layout.addWidget(self.password_input)

        # Login button
        login_btn = QPushButton("Login")
        login_btn.clicked.connect(self.login_user)
        layout.addWidget(login_btn)

        self.setLayout(layout)

    def login_user(self):
        username = self.username_input.text().strip()
        password = self.password_input.text().encode("utf-8")

        if not username or not password:
            QMessageBox.warning(self, "Input Error", "Both fields are required.")
            return

        # Find user in MongoDB
        user = self.users.find_one({"username": username})
        if user:
            stored_hash = user.get("password_hash")
            if stored_hash and bcrypt.checkpw(password, stored_hash):
                QMessageBox.information(self, "Success", f"Welcome {username}!")
            else:
                QMessageBox.warning(self, "Login Failed", "Incorrect password.")
        else:
            QMessageBox.warning(self, "Login Failed", "User not found.")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = LoginApp()
    window.show()
    sys.exit(app.exec())