from PySide6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QPushButton, QStackedWidget, QMessageBox
from logger import logger
from page_registry import PAGE_REGISTRY
from functools import partial
from database import get_user




class MainApp(QMainWindow):
    def __init__(self, user):
        super().__init__()
        # Limit height
        self.setMinimumHeight(600)
        self.setMaximumHeight(900)


        self.setWindowTitle("Main Application")

        self.user = user  # <-- CRITICAL FIX

        self.username = user.get("username", "Unknown")
        self.role = user.get("role", "guest")
        self.permissions = user.get("permissions", {})

        logger.info(f"MainApp started for user '{self.username}' with role '{self.role}'")

        self.setup_ui()

    def setup_ui(self):
        container = QWidget()
        layout = QVBoxLayout(container)

        # Stacked widget for pages
        self.stack = QStackedWidget()
        layout.addWidget(self.stack)

        # Navigation buttons
        self.nav_buttons = QVBoxLayout()
        layout.addLayout(self.nav_buttons)

        self.pages = []
        self.build_pages()

        self.setCentralWidget(container)

    def build_pages(self):
        for index, (title, info) in enumerate(PAGE_REGISTRY.items()):
            page_class = info["class"]

            if title == "Profile":
                page = page_class(self.user)
            else:
                page = page_class()

            self.pages.append(page)
            self.stack.addWidget(page)

        # Build navigation after pages exist
        self.build_navigation_buttons()

    def build_navigation_buttons(self):
        for index, (title, info) in enumerate(PAGE_REGISTRY.items()):
            permission = self.permissions.get(title)

            if permission not in ("ro", "rw"):
                continue

            btn = QPushButton(title)
            page = self.pages[index]

            btn.clicked.connect(
                partial(self.switch_page, index, page, permission)
            )

            self.nav_buttons.addWidget(btn)

    def refresh_navigation(self):
        # Reload user from DB
        from database import get_user
        updated_user = get_user(self.username)
        if updated_user:
            self.user = updated_user
            self.permissions = updated_user.get("permissions", {})

        # Clear existing buttons
        while self.nav_buttons.count():
            item = self.nav_buttons.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()

        # Rebuild navigation
        self.build_navigation_buttons()


    def switch_page(self, index, page, permission):
        """
        Switch to a page and apply read-only mode if needed.
        """
        try:
            logger.info(
                f"User '{self.username}' switched to page '{page.title}' "
                f"(permission: {permission})"
            )

            # Apply read-only mode
            page.set_read_only(permission == "ro")

            # Switch page
            self.stack.setCurrentIndex(index)

        except Exception as e:
            logger.error(f"Failed to switch page: {e}")
            QMessageBox.critical(self, "Error", "Could not switch page")