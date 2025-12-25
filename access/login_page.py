from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox
from main_app import MainApp
from database import get_user
import bcrypt
from logger import logger



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
        logger.info("Login attempt started")

        username = self.username.text().strip()
        password = self.password.text().strip()

        if not username or not password:
            logger.warning("Login failed: missing username or password")
            QMessageBox.warning(self, "Error", "Please enter both username and password")
            
            return

        try:
            user = get_user(username)
        except Exception as e:
            
            QMessageBox.critical(self, "Error", "Database error")
            return

        if not user:
            QMessageBox.warning(self, "Error", "User not found")
            
            return

        # -------------------------------
        # PASSWORD CHECK
        # -------------------------------
        try:
            if not bcrypt.checkpw(password.encode(), user["password"]):
                
                QMessageBox.warning(self, "Error", "Incorrect password")
                return
        except Exception as e:
            
            QMessageBox.critical(self, "Error", "Internal error checking password")
            return

        

        # -------------------------------
        # BUILD USER PERMISSION OBJECT
        # -------------------------------
        role = user.get("role", "standard")

        # Example structure stored in MongoDB:
        # "permissions": {
        #     "Dashboard": "rw",
        #     "Data Table": "ro",
        #     "Charts": None,
        #     "Admin": None
        # }

        permissions = user.get("permissions", {})

        user_object = {
            "username": username,
            "role": role,
            "permissions": permissions
        }

        

        # -------------------------------
        # OPEN MAIN APP WITH USER OBJECT
        # -------------------------------
        self.hide()
        self.main = MainApp(user_object)
        self.main.show()

    def open_registration(self):
        from registration_page import RegistrationWindow
        self.reg = RegistrationWindow()
        self.reg.show()