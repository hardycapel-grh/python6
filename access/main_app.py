from PySide6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QListWidget, QStackedWidget, QMessageBox
from ui.windows.admin_control_window import AdminControlWindow
from ui.windows.log_viewer_window import LogViewerWindow
from ui.components.logger import logger
from page_registry import PAGE_REGISTRY



class MainApp(QMainWindow):
    def __init__(self, user):
        super().__init__()
        self.user = user
        self.log_window = None  # keep reference

        self.setWindowTitle("Main Application")
        self.resize(1200, 800)

        self.admin_window = AdminControlWindow(self.user, parent=self)

        root = QWidget()
        root_layout = QHBoxLayout(root)

        # Sidebar
        self.sidebar = QListWidget()
        self.sidebar.addItem("Log Viewer")  # Always present
        self.sidebar.addItem("Admin Control Panel")

        for page_name in PAGE_REGISTRY.keys():
            self.sidebar.addItem(page_name)

        self.sidebar.itemClicked.connect(self.handle_sidebar_click)

        # Stacked widget for pages
        self.stack = QStackedWidget()

        root_layout.addWidget(self.sidebar, 1)
        root_layout.addWidget(self.stack, 4)

        self.setCentralWidget(root)

        # IMPORTANT: avoid auto-opening Log Viewer on startup
        self.sidebar.setCurrentRow(-1)

        logger.info(f"MainApp started for '{user['username']}'")

    def handle_sidebar_click(self, item):
        name = item.text()

        if name == "Log Viewer":
            self.open_log_viewer()
            return
        
        if name == "Admin Control Panel":
            self.open_admin_panel()
            return

        self.load_page(name)


    def open_log_viewer(self):
        if not hasattr(self, "log_window") or self.log_window is None or not self.log_window.isVisible():
            self.log_window = LogViewerWindow()

        self.log_window.show()
        self.log_window.raise_()
        self.log_window.activateWindow()
        logger.info("Log Viewer opened")

    def open_admin_panel(self):
        perm = self.user["permissions"].get("Admin Control Panel", None)

        if perm in [None, "none"]:
            QMessageBox.warning(self, "Access Denied", "You do not have permission to open the Admin Control Panel.")
            return

        # Create only if needed
        if not hasattr(self, "admin_window") or self.admin_window is None:
            from ui.windows.admin_control_window import AdminControlWindow
            self.admin_window = AdminControlWindow(self.user, parent=self)

        self.admin_window.show()
        self.admin_window.raise_()
        self.admin_window.activateWindow()

    def load_page(self, name):
        info = PAGE_REGISTRY.get(name)
        if not info:
            logger.error(f"Unknown page '{name}'")
            return

        page_class = info["class"]
        page = page_class(self.user)

        self.stack.addWidget(page)
        self.stack.setCurrentWidget(page)