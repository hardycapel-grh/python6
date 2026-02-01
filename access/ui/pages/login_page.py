from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox, QTextEdit, QComboBox
import bcrypt

from ui.components.logger import logger
from database import get_user, update_permissions, update_user_fields
from main_app import MainApp


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
        login_btn.clicked.connect(self.login)

        register_btn = QPushButton("Register")
        register_btn.clicked.connect(self.open_register)

        layout.addWidget(QLabel("Login Page"))
        layout.addWidget(self.username)
        layout.addWidget(self.password)
        layout.addWidget(login_btn)
        layout.addWidget(register_btn)

        self.setLayout(layout)

    def open_register(self):
        from ui.pages.registration_page import RegistrationWindow
        self.reg_window = RegistrationWindow()
        self.reg_window.show()

    def login(self):
        from page_registry import PAGE_REGISTRY  # safe import

        username = self.username.text().strip()
        password = self.password.text().strip()

        if not username or not password:
            QMessageBox.warning(self, "Error", "Please enter both username and password")
            logger.warning("Login failed: missing username or password")
            return

        user = get_user(username)

        if not user:
            QMessageBox.warning(self, "Error", "User not found")
            logger.warning(f"Login failed: user '{username}' not found")
            return

        # Check password
        try:
            if not bcrypt.checkpw(password.encode(), user["password"]):
                QMessageBox.warning(self, "Error", "Incorrect password")
                logger.warning(f"Login failed: incorrect password for '{username}'")
                return
        except Exception as e:
            logger.error(f"Password check failed for '{username}': {e}")
            QMessageBox.critical(self, "Error", "Internal authentication error")
            return

        # Auto-repair missing permissions using PAGE_REGISTRY
        repaired = False
        for page_name, info in PAGE_REGISTRY.items():
            if page_name not in user["permissions"]:
                user["permissions"][page_name] = info["default_permission"]
                repaired = True

        if repaired:
            update_permissions(username, user["permissions"])
            logger.info(f"Permissions auto-repaired for user '{username}'")

        logger.info(f"User '{username}' logged in successfully")

        # Auto-repair missing fields
        updated = False

        # Example: new field "theme"
        if "theme" not in user:
            user["theme"] = "light"
            updated = True

        # Example: new field "last_login"
        if "last_login" not in user:
            user["last_login"] = None
            updated = True

        if "email" not in user:
            user["email"] = ""
            updated = True

        # Save repairs
        if updated:
            update_user_fields(username, user)
            logger.info(f"Auto-repaired missing fields for user '{username}'")

        # Open main app
        self.main_app = MainApp(user)
        self.main_app.show()
        self.close()

    def set_read_only(self, ro: bool):
        """Enable or disable editing for all input widgets."""
        for widget in self.findChildren((QLineEdit, QTextEdit, QComboBox)):
            if isinstance(widget, QLineEdit):
                widget.setReadOnly(ro)
            elif isinstance(widget, QTextEdit):
                widget.setReadOnly(ro)
            elif isinstance(widget, QComboBox):
                widget.setEnabled(not ro)

        # Disable buttons that modify data
        for btn in self.findChildren(QPushButton):
            if btn.objectName() not in ("nav", "close", "back"):
                btn.setEnabled(not ro)