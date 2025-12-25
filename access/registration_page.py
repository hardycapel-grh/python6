from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox
from database import create_user
import bcrypt


class RegistrationWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Register")

        layout = QVBoxLayout()

        self.username = QLineEdit()
        self.username.setPlaceholderText("Choose a username")

        self.password = QLineEdit()
        self.password.setPlaceholderText("Choose a password")
        self.password.setEchoMode(QLineEdit.Password)

        register_btn = QPushButton("Register")
        register_btn.clicked.connect(self.register)

        layout.addWidget(QLabel("Registration Page"))
        layout.addWidget(self.username)
        layout.addWidget(self.password)
        layout.addWidget(register_btn)

        self.setLayout(layout)

        

    def register(self):
        

        username = self.username.text().strip()
        password = self.password.text().strip()

        if not username or not password:
            QMessageBox.warning(self, "Error", "Username and password cannot be empty")
            
            return

        try:
            hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
            default_permissions = {
                "Dashboard": "rw",
                "Data Table": "ro",
                "Charts": "ro",
                "Admin": None
            }

            
        except Exception as e:
            
            QMessageBox.critical(self, "Error", "Internal error hashing password")
            return

        # Default role assigned here
        default_role = "viewer"

        success = create_user(username, hashed, default_role, default_permissions)


        if success:
            QMessageBox.information(self, "Success", "User registered")
            
            self.close()
        else:
            QMessageBox.critical(self, "Error", "Failed to register user")
            