from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLabel,
    QLineEdit, QPushButton, QMessageBox
)
import bcrypt
import sys

from services.mongo_service import MongoService


class LoginApp(QWidget):
    def __init__(self, mongo_service):
        super().__init__()
        self.mongo = mongo_service
        self.setWindowTitle("User Login")

        self.users = self.mongo.db["users"]

        layout = QVBoxLayout()

        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Username")
        layout.addWidget(QLabel("Username:"))
        layout.addWidget(self.username_input)

        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Password")
        self.password_input.setEchoMode(QLineEdit.Password)
        layout.addWidget(QLabel("Password:"))
        layout.addWidget(self.password_input)

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

        user = self.users.find_one({"username": username})
        stored_hash = user.get("password_hash") if user else None

        if stored_hash:
            if isinstance(stored_hash, str):
                stored_hash = stored_hash.encode("utf-8")

            if bcrypt.checkpw(password, stored_hash):
                QMessageBox.information(self, "Success", f"Welcome {username}!")
                self.mongo.audit(
                    event="login.success",
                    performed_by=username,
                    details="User logged in"
                )
                return

        QMessageBox.warning(self, "Login Failed", "Invalid username or password.")
        self.mongo.audit(
            event="login.failure",
            performed_by=username,
            details="Invalid username or password"
        )


if __name__ == "__main__":
    mongo = MongoService()
    app = QApplication(sys.argv)
    window = LoginApp(mongo)
    window.show()
    sys.exit(app.exec())
