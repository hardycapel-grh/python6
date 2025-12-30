from PySide6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QPushButton, QStackedWidget, QMessageBox
from logger import logger
from page_registry import PAGE_REGISTRY


class MainApp(QMainWindow):
    def __init__(self, user):
        super().__init__()
        self.setWindowTitle("Main Application")

        # Extract user info
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
        """
        Build pages dynamically from PAGE_REGISTRY.
        Only pages with permission != None are shown.
        """
        for index, (title, info) in enumerate(PAGE_REGISTRY.items()):
            page_class = info["class"]
            page = page_class()
            self.pages.append(page)
            self.stack.addWidget(page)

            permission = self.permissions.get(title)

            # Skip pages the user is not allowed to see
            if permission is None:
                continue

            # Create navigation button
            btn = QPushButton(title)
            btn.clicked.connect(
                lambda _, i=index, p=page, perm=permission:
                    self.switch_page(i, p, perm)
            )
            self.nav_buttons.addWidget(btn)

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