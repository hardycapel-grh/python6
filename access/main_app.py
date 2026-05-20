from cProfile import label

from PySide6.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout,
    QListWidget, QStackedWidget, QMessageBox
)
from ui.components.logger import logger
from ui.windows.log_viewer_window import LogViewerPage, LogViewerWindow
from ui.windows.admin_control_window import AdminControlWindow
from ui.components.logger_utils import log_event
from ui.dialogs.profile_dialogs import ProfileDialog, ChangePasswordDialog
from ui.pages.admin.audit_log_page import AuditLogPage
from ui.pages.profile_page import ProfilePage





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

    def has_permission(self, perm_name: str) -> bool:
        perms = getattr(self.user, "permissions", [])
        return perm_name in perms or "*" in perms



    # ---------------------------------------------------------
    # Sidebar construction
    # ---------------------------------------------------------
    def _build_sidebar(self):
        log_event("info", "Building sidebar", user=self.user.username)

        self._add_sidebar_item(
            "My Profile",
            ProfilePage,
            lambda: ProfilePage(self, self.mongo, None)
        )

        self._add_sidebar_item(
            "Log Viewer",
            LogViewerPage,
            lambda: LogViewerPage(None),
            required_permission="logs.read"
        )

        self._add_sidebar_item(
            "Admin",
            AdminControlWindow,
            lambda: AdminControlWindow(self.user, self.mongo, self),
            required_permission="admin.access"
        )



    # ---------------------------------------------------------
    # Add sidebar item with permission filtering
    # ---------------------------------------------------------
    def _add_sidebar_item(self, label, window_class, factory, required_permission=None):
        log_event("debug", "Registering sidebar item",
                label=label, required_permission=required_permission)

        if required_permission:
            perms = getattr(self.user, "permissions", [])
            if required_permission not in perms and "*" not in perms:
                log_event("warn", "Sidebar item blocked",
                        user=self.user.username,
                        label=label,
                        required_permission=required_permission)
                return

        # Store BOTH class and factory
        self.sidebar_items[label] = (window_class, factory)

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

        entry = self.sidebar_items.get(label)

        if entry is None:
            log_event("error", "No window entry found",
                    user=self.user.username, label=label)
            return

        window_class, factory = entry
        self._open_window(window_class, factory)





    # ---------------------------------------------------------
    # Permission-aware window opening
    # ---------------------------------------------------------
    def _open_window(self, window_class, factory):
        key = window_class.__name__

        if key in self._open_windows:
            window = self._open_windows[key]
            window.show()
            window.raise_()
            window.activateWindow()
            return

        try:
            window = factory()
        except Exception as e:
            log_event("error", f"Factory for {key} failed: {e}")
            raise

        self._open_windows[key] = window

        window.show()
        window.raise_()
        window.activateWindow()









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

    def show_permission_denied(self):
        QMessageBox.warning(
            self,
            "Permission Denied",
            "You do not have permission to perform this action."
        )

    def _wrap_admin_window(self):
        win = AdminControlWindow(self.user, self.mongo, parent=self)
        win.setParent(self)   # ⭐ REQUIRED because WindowWithSidebar ignores parent
        return win
