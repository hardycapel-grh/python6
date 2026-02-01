# main_app.py
from PySide6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QPushButton, QStackedWidget, QMessageBox
from ui.components.logger import logger
from page_registry import PAGE_REGISTRY
from database import get_user


class MainApp(QMainWindow):
    def __init__(self, user):
        super().__init__()

        self.setMinimumHeight(600)
        self.setMaximumHeight(900)
        self.setWindowTitle("Main Application")

        self.user = user
        self.username = user.get("username", "Unknown")
        self.permissions = user.get("permissions", {})

        logger.info(f"MainApp started for '{self.username}'")

        self.setup_ui()

    def setup_ui(self):
        container = QWidget()
        layout = QVBoxLayout(container)

        self.stack = QStackedWidget()
        layout.addWidget(self.stack)

        self.nav_buttons = QVBoxLayout()
        layout.addLayout(self.nav_buttons)

        self.pages = []
        self.build_pages()
        self.build_navigation_buttons()

        self.setCentralWidget(container)

    def build_pages(self):
        """Create page objects and add them to the stack."""
        for title, info in PAGE_REGISTRY.items():
            page_class = info["class"]

            if title == "Profile":
                page = page_class(self.user)
            else:
                page = page_class()

            self.pages.append(page)
            self.stack.addWidget(page)

    def build_navigation_buttons(self):
        """Build sidebar buttons based on current permissions."""
        for index, (title, info) in enumerate(PAGE_REGISTRY.items()):
            permission = self.permissions.get(title)

            if permission not in ("ro", "rw"):
                continue

            btn = QPushButton(title)
            btn.setObjectName("nav")

            # Evaluate permission at click time
            btn.clicked.connect(
                lambda _, i=index, t=title: self.switch_page(i, t)
            )

            self.nav_buttons.addWidget(btn)
        log_btn = QPushButton("Open Log Viewer")
        log_btn.setObjectName("nav")
        log_btn.clicked.connect(self.open_log_viewer)
        self.nav_buttons.addWidget(log_btn)

    def open_log_viewer(self):
        from ui.log_viewer_window import LogViewerWindow
        self.log_window = LogViewerWindow()
        self.log_window.show()

    def refresh_navigation(self):
        """Reload user permissions and rebuild navigation."""
        updated_user = get_user(self.username)
        if updated_user:
            self.user = updated_user
            self.permissions = updated_user.get("permissions", {})

        # Clear old buttons
        while self.nav_buttons.count():
            item = self.nav_buttons.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()

        self.build_navigation_buttons()

    def switch_page(self, index, title):
        """Switch to a page and apply read-only mode."""
        try:
            permission = self.permissions.get(title)
            page = self.pages[index]

            logger.info(f"Switching to '{title}' with permission '{permission}'")

            page.set_read_only(permission == "ro")
            self.stack.setCurrentIndex(index)

        except Exception as e:
            import traceback
            traceback.print_exc()
            logger.error(f"Failed to switch page: {e}")
            QMessageBox.critical(self, "Error", str(e))