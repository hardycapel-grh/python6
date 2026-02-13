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
        from ui.pages.registration_page import RegistrationPage
        self.reg_window = RegistrationPage()
        self.reg_window.show()

    def login(self):
        from page_registry import PAGE_REGISTRY  # safe import

        username = self.username.text().strip()
        password = self.password.text().strip()

        logger.info(f"Login attempt: {username}")

        if not username or not password:
            QMessageBox.warning(self, "Error", "Please enter both username and password")
            logger.warning("Login failed: missing username or password")
            return

        user = get_user(username)

        if not user:
            QMessageBox.warning(self, "Error", "User not found")
            logger.warning(f"Login failed: user '{username}' not found")
            return

        # -------------------------
        # FIXED: bcrypt password check
        # -------------------------
        try:
            stored_hash = user.get("password_hash")
            if not stored_hash:
                logger.error(f"User '{username}' has no password_hash field")
                QMessageBox.critical(self, "Error", "Account is corrupted")
                return

            if not bcrypt.checkpw(password.encode(), stored_hash.encode()):
                QMessageBox.warning(self, "Error", "Incorrect password")
                logger.warning(f"Login failed: incorrect password for '{username}'")
                return

        except Exception as e:
            logger.error(f"Password check failed for '{username}': {e}")
            QMessageBox.critical(self, "Error", "Internal authentication error")
            return

        # -------------------------
        # Permissions auto-repair
        # -------------------------
        repaired = False
        for page_name, info in PAGE_REGISTRY.items():
            if page_name not in user["permissions"]:
                user["permissions"][page_name] = info["default_permission"]
                repaired = True

        if repaired:
            update_permissions(username, user["permissions"])
            logger.info(f"Permissions auto-repaired for user '{username}'")

        logger.info(f"User '{username}' logged in successfully")

        # -------------------------
        # Auto-repair missing fields
        # -------------------------
        updated = False

        if "theme" not in user:
            user["theme"] = "light"
            updated = True

        if "last_login" not in user:
            user["last_login"] = None
            updated = True

        if "email" not in user:
            user["email"] = ""
            updated = True

        if updated:
            update_user_fields(username, user)
            logger.info(f"Auto-repaired missing fields for user '{username}'")

        # -------------------------
        # Open main app
        # -------------------------
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

    def apply_permissions(self, perm):
        if perm == "rw":
            return

        # Disable all buttons
        for btn in self.findChildren(QPushButton):
            btn.setEnabled(False)

        # Disable editable widgets
        for t in (QLineEdit, QTextEdit, QComboBox):
            for widget in self.findChildren(t):
                widget.setEnabled(False)

        # Optional banner
        banner = QLabel("Read-Only Mode")
        banner.setStyleSheet("color: orange; font-weight: bold;")
        self.layout().insertWidget(0, banner)