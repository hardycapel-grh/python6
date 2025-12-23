from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox
from main_app import MainApp
from database import get_user
import bcrypt


class LoginWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Login")

        layout = QVBoxLayout()

        self.username = QLineEdit()
        self.username.setPlaceholderText("Username")

        self.password = QLineEdit()
        self.password.setPlaceholderText("Password")
        self.password.setEchoMode(QLineEdit.Password)

        login_btn = QPushButton("Login")
        register_btn = QPushButton("Register")

        login_btn.clicked.connect(self.login)
        register_btn.clicked.connect(self.open_registration)

        layout.addWidget(QLabel("Login Page"))
        layout.addWidget(self.username)
        layout.addWidget(self.password)
        layout.addWidget(login_btn)
        layout.addWidget(register_btn)

        self.setLayout(layout)

    def login(self):
        print("[DEBUG] Login button clicked")

        username = self.username.text().strip()
        password = self.password.text().strip()

        if not username or not password:
            QMessageBox.warning(self, "Error", "Please enter both username and password")
            print("[ERROR] Missing username or password")
            return

        try:
            user = get_user(username)
        except Exception as e:
            print("[ERROR] Database error:", e)
            QMessageBox.critical(self, "Error", "Database error")
            return

        if not user:
            QMessageBox.warning(self, "Error", "User not found")
            print("[ERROR] User not found")
            return

        try:
            if bcrypt.checkpw(password.encode(), user["password"]):
                print("[DEBUG] Password correct")
                self.hide()
                self.main = MainApp(user)
                self.main.show()
            else:
                print("[ERROR] Incorrect password")
                QMessageBox.warning(self, "Error", "Incorrect password")
        except Exception as e:
            print("[ERROR] Password check failed:", e)
            QMessageBox.critical(self, "Error", "Internal error checking password")

    def open_registration(self):
        from registration_page import RegistrationWindow
        self.reg = RegistrationWindow()
        self.reg.show()