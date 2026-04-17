from cProfile import label

from PySide6.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout,
    QListWidget, QStackedWidget
)
from ui.components.logger import logger
from ui.windows.log_viewer_window import LogViewerWindow
from ui.windows.admin_control_window import AdminControlWindow
from ui.components.logger_utils import log_event
from ui.dialogs.profile_dialogs import ProfileDialog, ChangePasswordDialog




class MainApp(QMainWindow):
    def __init__(self, user, mongo):
        super().__init__()
        self.setMinimumSize(1200, 800)
        self.resize(1400, 900)

        self.user = user
        self.mongo = mongo

        # Storage for sidebar factories
        self.sidebar_items = {}

        # Sidebar widget
        self.sidebar_list = QListWidget()
        self.sidebar_list.setFixedWidth(200)
        self.sidebar_list.itemClicked.connect(self._handle_sidebar_click)

        # Track open windows
        self._open_windows = {}

        # Main content area
        self.main_pane = QStackedWidget()

        # Layout
        container = QWidget()
        layout = QHBoxLayout(container)
        layout.addWidget(self.sidebar_list)
        layout.addWidget(self.main_pane)
        self.setCentralWidget(container)

        # Build sidebar AFTER UI is ready
        self._build_sidebar()

        # Log initial UI tree
        log_event("info", "MainApp started", user=self.user.username)


    # ---------------------------------------------------------
    # Sidebar construction
    # ---------------------------------------------------------
    def _build_sidebar(self):
        log_event("info", "Building sidebar", user=self.user.username)

        self._add_sidebar_item(
            "Log Viewer",
            LogViewerWindow,
            lambda: LogViewerWindow(self.user),   # <-- MUST pass user
            required_permission="logs.read"
)
        self._add_sidebar_item(
            "Admin Control Panel",
            AdminControlWindow,
            lambda: AdminControlWindow(self.user, self.mongo),
            required_permission="admin.access"
        )

            # --- New: self-service items (no special permission) ---
        self._add_sidebar_item(
            "My Profile",
            ProfileDialog,
            lambda: ProfileDialog(self.mongo, self.user, self)
        )

        self._add_sidebar_item(
            "Change Password",
            ChangePasswordDialog,
            lambda: ChangePasswordDialog(self.mongo, self.user, self)
        )

    # ---------------------------------------------------------
    # Add sidebar item with permission filtering
    # ---------------------------------------------------------
    def _add_sidebar_item(self, label, window_class, factory, required_permission=None):
    
        log_event("debug", "Registering sidebar item",
                label=label, required_permission=required_permission)

        # Permission filtering
        if required_permission:
            perms = getattr(self.user, "permissions", [])
            if required_permission not in perms and "*" not in perms:
                log_event("warn", "Sidebar item blocked",
                        user=self.user.username,
                        label=label,
                        required_permission=required_permission)
                return

        # Store factory
        self.sidebar_items[label] = factory
        log_event("debug", "Sidebar item stored",
                label=label, factory=str(factory))

        # Add label to sidebar
        self.sidebar_list.addItem(label)
        log_event("info", "Sidebar item added",
                label=label, user=self.user.username)


    # ---------------------------------------------------------
    # Sidebar click handler
    # ---------------------------------------------------------
    def _handle_sidebar_click(self, item):
        label = item.text().strip()

        log_event("info", "Sidebar clicked",
                user=self.user.username, label=label)

        window_factory = self.sidebar_items.get(label)

        if window_factory is None:
            log_event("error", "No window factory found",
                    user=self.user.username, label=label)
            return

        self._open_window(window_factory)


    # ---------------------------------------------------------
    # Permission-aware window opening
    # ---------------------------------------------------------
    def _open_window(self, window_factory):
        # Reuse existing window
        if window_factory in self._open_windows:
            log_event("info", "Window reused",
                    user=self.user.username,
                    window=str(window_factory))

            window = self._open_windows[window_factory]
            window.show()
            window.raise_()
            window.activateWindow()
            return

        # Create new window
        log_event("info", "Opening new window",
                user=self.user.username,
                window=str(window_factory))

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
