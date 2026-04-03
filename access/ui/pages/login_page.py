from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton,
    QMessageBox, QTextEdit, QComboBox
)
import bcrypt

from ui.components.logger import logger
from services.mongo_service import MongoService


class LoginWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Login")

        from services.user_service import UserService
        self.user_service = UserService()

        self.mongo = MongoService()

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




    # ---------------------------------------------------------
    # Registration window
    # ---------------------------------------------------------
    def open_register(self):
        from ui.pages.registration_page import RegistrationPage
        self.reg_window = RegistrationPage(self.user_service)
        self.reg_window.show()

    # ---------------------------------------------------------
    # Login logic
    # ---------------------------------------------------------
    def login(self):
        from page_registry import PAGE_REGISTRY  # safe import

        username = self.username.text().strip()
        password = self.password.text().strip()

        logger.info(f"Login attempt: {username}")

        if not username or not password:
            QMessageBox.warning(self, "Error", "Please enter both username and password")
            logger.warning("Login failed: missing username or password")
            return

        # -------------------------------------------------
        # Authenticate via MongoDB
        # -------------------------------------------------
        db_user = self.mongo.authenticate(username, password)

        if not db_user:
            QMessageBox.warning(self, "Error", "Invalid username or password")
            logger.warning(f"Login failed for '{username}'")
            return

        # -------------------------------------------------
        # Force password change
        # -------------------------------------------------
        if db_user.get("must_change_password"):
            logger.info(f"User '{username}' must change password before continuing")
            self.open_force_password_change_window(username)
            return

        # -------------------------------------------------
        # Auto-repair missing fields
        # -------------------------------------------------
        updated = False

        if "theme" not in db_user:
            db_user["theme"] = "light"
            updated = True

        if "last_login" not in db_user:
            db_user["last_login"] = None
            updated = True

        if "email" not in db_user:
            db_user["email"] = ""
            updated = True

        if updated:
            self.mongo.update_permissions(username, db_user["permissions"])
            logger.info(f"Auto-repaired missing fields for user '{username}'")

        # -------------------------------------------------
        # Convert dict → User object
        # -------------------------------------------------
        from models.user import User
        user = User(
            username=db_user["username"],
            role=db_user["role"],
            permissions=db_user["permissions"]
        )

        # -------------------------------------------------
        # Open MainApp
        # -------------------------------------------------
        from main_app import MainApp
        self.main_app = MainApp(user)
        self.main_app.show()
        self.close()

    # ---------------------------------------------------------
    # Read-only mode helpers (unchanged)
    # ---------------------------------------------------------
    def set_read_only(self, ro: bool):
        for widget in self.findChildren((QLineEdit, QTextEdit, QComboBox)):
            if isinstance(widget, QLineEdit):
                widget.setReadOnly(ro)
            elif isinstance(widget, QTextEdit):
                widget.setReadOnly(ro)
            elif isinstance(widget, QComboBox):
                widget.setEnabled(not ro)

        for btn in self.findChildren(QPushButton):
            if btn.objectName() not in ("nav", "close", "back"):
                btn.setEnabled(not ro)

    def apply_permissions(self, perm):
        if perm == "rw":
            return

        for btn in self.findChildren(QPushButton):
            btn.setEnabled(False)

        for t in (QLineEdit, QTextEdit, QComboBox):
            for widget in self.findChildren(t):
                widget.setEnabled(False)

        banner = QLabel("Read-Only Mode")
        banner.setStyleSheet("color: orange; font-weight: bold;")
        self.layout().insertWidget(0, banner)

    # ---------------------------------------------------------
    # Force password change flow
    # ---------------------------------------------------------
    def open_force_password_change_window(self, username):
        from ui.windows.force_password_change_window import ForcePasswordChangeWindow
        dialog = ForcePasswordChangeWindow(username, self)

        if dialog.exec():
            updated_user = self.mongo.db.users.find_one({"username": username}, {"_id": 0})

            # Convert dict → User object
            from models.user import User
            user = User(
                username=updated_user["username"],
                role=updated_user["role"],
                permissions=updated_user["permissions"]
            )

            from main_app import MainApp
            self.main_app = MainApp(user)
            self.main_app.show()
            self.close()