from PySide6.QtWidgets import QMainWindow, QWidget, QHBoxLayout, QListWidget, QListWidgetItem
from ui.components.logger import logger
from ui.windows.log_viewer_window import LogViewerWindow
from ui.windows.admin_control_window import AdminControlWindow


class MainApp(QMainWindow):
    def __init__(self, user):
        super().__init__()

        # Convert dict → User object (we'll define this next)
        self.user = user
        self._open_windows = {}

        self.setWindowTitle("Main Application")
        self.resize(1200, 800)

        logger.info(f"MainApp initialised for user '{self.user.username}'")

        # Root layout
        root = QWidget()
        root_layout = QHBoxLayout(root)
        self.setCentralWidget(root)

        # Sidebar
        self.sidebar = QListWidget()
        root_layout.addWidget(self.sidebar, 1)

        # Build sidebar with permission-aware items
        self._build_sidebar()

        # Connect click handler
        self.sidebar.itemClicked.connect(self._handle_sidebar_click)


    # ---------------------------------------------------------
    # Sidebar construction
    # ---------------------------------------------------------
    def _build_sidebar(self):
        self._add_sidebar_item("Log Viewer",
                            LogViewerWindow,
                            lambda: LogViewerWindow())

        self._add_sidebar_item("Admin Control Panel",
                            AdminControlWindow,
                            lambda: AdminControlWindow(self.user))

    def _add_sidebar_item(self, label: str, window_class, window_factory):
        required = getattr(window_class, "REQUIRED_PERMISSION", None)

        if required and not self.user.has_permission(required):
            logger.info(f"Hiding '{label}' (missing permission: {required})")
            return

        item = QListWidgetItem(label)
        item.setData(1000, window_factory)  # store FACTORY, not class
        self.sidebar.addItem(item)

    # ---------------------------------------------------------
    # Sidebar click handler
    # ---------------------------------------------------------
    def _handle_sidebar_click(self, item):
        window_factory = item.data(1000)
        label = item.text()

        logger.info(f"Main sidebar clicked: {label}")
        self._open_window(window_factory)

    # ---------------------------------------------------------
    # Permission-aware window opening
    # ---------------------------------------------------------
    
    def _open_window(self, window_factory):
        # If already open, bring it to front
        if window_factory in self._open_windows:
            window = self._open_windows[window_factory]
            window.show()
            window.raise_()
            window.activateWindow()
            return

        # Create window lazily
        window = window_factory()
        self._open_windows[window_factory] = window
        
        window.show()

    # ---------------------------------------------------------
    # Permission denied popup
    # ---------------------------------------------------------
    def _show_permission_denied(self):
        from PySide6.QtWidgets import QMessageBox

        QMessageBox.warning(
            self,
            "Permission Denied",
            "You do not have permission to access this feature.",
        )