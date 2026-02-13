from PySide6.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QVBoxLayout,
    QListWidget, QStackedWidget, QLabel, QPushButton,
    QLineEdit, QTextEdit, QComboBox, QMessageBox
)
from ui.components.logger import logger


class AdminControlWindow(QMainWindow):
    def __init__(self, user, parent=None):
        super().__init__(parent)
        self.user = user

        self.setWindowTitle("Admin Control Panel")
        self.resize(1100, 700)

        # --- ROOT WIDGET + LAYOUT ---
        root = QWidget()
        self.root_layout = QHBoxLayout(root)

        # --- SIDEBAR ---
        self.sidebar = QListWidget()
        self.sidebar.addItem("User Manager")
        self.sidebar.addItem("Permissions")
        self.sidebar.addItem("System Info")
        self.sidebar.addItem("Logs")

        self.sidebar.itemClicked.connect(self.handle_sidebar_click)

        # --- HIDE TOOLS THE USER CANNOT ACCESS ---
        for i in range(self.sidebar.count()):
            item = self.sidebar.item(i)
            name = item.text()
            perm = self.user["permissions"].get(name, "none")

            if perm in ["none", None]:
                item.setHidden(True)

        # --- STACKED WIDGET FOR ADMIN TOOLS ---
        self.stack = QStackedWidget()

        from ui.pages.user_manager_page import UserManagerPage
        self.user_manager_page = UserManagerPage(self.user)
        self.permissions_page = QLabel("Permissions Editor goes here")
        self.system_page = QLabel("System Information goes here")
        self.logs_page = QLabel("Log Tools go here")

        self.stack.addWidget(self.user_manager_page)
        self.stack.addWidget(self.permissions_page)
        self.stack.addWidget(self.system_page)
        self.stack.addWidget(self.logs_page)

        # --- LAYOUT ---
        self.root_layout.addWidget(self.sidebar, 1)
        self.root_layout.addWidget(self.stack, 4)

        self.setCentralWidget(root)

        # --- APPLY WINDOW-LEVEL PERMISSIONS ---
        self.permission = user["permissions"].get("Admin Control Panel", "none")
        self.apply_permissions()

        # Track destruction so MainApp knows when to recreate
        self.destroyed.connect(self._on_destroyed)

        logger.info(f"Admin Control Panel opened by '{user['username']}'")

    # ---------------------------------------------------------
    # APPLY READ-ONLY MODE
    # ---------------------------------------------------------
    def apply_permissions(self):
        if self.permission == "rw":
            return  # full access

        for btn in self.findChildren(QPushButton):
            btn.setEnabled(False)

        for t in (QLineEdit, QTextEdit, QComboBox):
            for widget in self.findChildren(t):
                widget.setEnabled(False)

        banner = QLabel("Read-Only Mode — You do not have permission to make changes.")
        banner.setStyleSheet("color: orange; font-weight: bold;")
        self.root_layout.insertWidget(0, banner)

    # ---------------------------------------------------------
    # SIDEBAR NAVIGATION
    # ---------------------------------------------------------
    def handle_sidebar_click(self, item):
        name = item.text()

        perm = self.user["permissions"].get(name, "none")

        if perm in ["none", None]:
            QMessageBox.warning(self, "Access Denied", f"You do not have permission to access '{name}'.")
            return

        if name == "User Manager":
            self.user_manager_page.apply_permissions(perm)
            self.stack.setCurrentWidget(self.user_manager_page)

        elif name == "Permissions":
            self.stack.setCurrentWidget(self.permissions_page)

        elif name == "System Info":
            self.stack.setCurrentWidget(self.system_page)

        elif name == "Logs":
            self.stack.setCurrentWidget(self.logs_page)

    # ---------------------------------------------------------
    # CLEANUP WHEN WINDOW CLOSES
    # ---------------------------------------------------------
    def _on_destroyed(self, *args):
        if self.parent() and hasattr(self.parent(), "admin_window"):
            self.parent().admin_window = None

    def closeEvent(self, event):
        if self.parent() and hasattr(self.parent(), "admin_window"):
            self.parent().admin_window = None
        super().closeEvent(event)