from PySide6.QtWidgets import QMainWindow, QWidget, QHBoxLayout, QListWidget
from ui.components.logger import logger
from ui.windows.log_viewer_window import LogViewerWindow
from ui.windows.admin_control_window import AdminControlWindow   # placeholder for later


class MainApp(QMainWindow):
    def __init__(self, user):
        super().__init__()
        self.user = user
        self._open_windows = {}

        self.setWindowTitle("Main Application")
        self.resize(1200, 800)

        logger.info(f"MainApp initialised for user '{user['username']}'")

        # Root layout
        root = QWidget()
        root_layout = QHBoxLayout(root)
        self.setCentralWidget(root)

        # Sidebar (main navigation)
        self.sidebar = QListWidget()
        self.sidebar.addItem("Log Viewer")
        self.sidebar.addItem("Admin Control Panel")   # will work once we add it
        self.sidebar.itemClicked.connect(self._handle_sidebar_click)

        root_layout.addWidget(self.sidebar, 1)

    def _handle_sidebar_click(self, item):
        name = item.text()
        logger.info(f"Main sidebar clicked: {name}")

        if name == "Log Viewer":
            self._open_window(LogViewerWindow)

        elif name == "Admin Control Panel":
            self._open_window(AdminControlWindow)

    def _open_window(self, window_class):
        """Ensures only one instance of each tool window exists."""
        if window_class not in self._open_windows:
            self._open_windows[window_class] = window_class()

        win = self._open_windows[window_class]
        win.show()
        win.raise_()
        win.activateWindow()

        logger.info(f"Opened window: {window_class.__name__}")