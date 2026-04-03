from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox, QTextEdit, QComboBox
)
from services.registration_service import RegistrationService


class RegistrationPage(QWidget):
    def __init__(self, user_service):
        super().__init__()

        self.service = RegistrationService(user_service)

        layout = QVBoxLayout(self)

        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Username")

        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Password")
        self.password_input.setEchoMode(QLineEdit.Password)

        self.confirm_input = QLineEdit()
        self.confirm_input.setPlaceholderText("Confirm Password")
        self.confirm_input.setEchoMode(QLineEdit.Password)

        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("Email")

        self.register_button = QPushButton("Register")
        self.register_button.clicked.connect(self.handle_register)

        layout.addWidget(self.username_input)
        layout.addWidget(self.password_input)
        layout.addWidget(self.confirm_input)
        layout.addWidget(self.email_input)
        layout.addWidget(self.register_button)

    def handle_register(self):
        username = self.username_input.text().strip()
        email = self.email_input.text().strip()
        password = self.password_input.text()
        confirm = self.confirm_input.text()

        valid, error = self.service.validate(username, email, password, confirm)

        if not valid:
            QMessageBox.warning(self, "Registration Error", error)
            return

        self.service.register_user(username, email, password)

        QMessageBox.information(self, "Success", "Registration successful!")

        # Close registration window and open login
        self.close()
        from ui.pages.login_page import LoginWindow
        self.login_window = LoginWindow()
        self.login_window.show()
