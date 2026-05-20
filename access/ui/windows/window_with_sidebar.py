from PySide6.QtWidgets import QMainWindow, QWidget, QHBoxLayout, QListWidget, QStackedWidget
from ui.pages.admin.audit_log_page import AuditLogPage
from ui.components.logger_utils import log_event


class WindowWithSidebar(QMainWindow):
    # print(">>> CLASS OBJECT ID:", id(AuditLogPage))

    def __init__(self, title, parent=None):
        super().__init__(parent)
        self.setWindowTitle(title)

        
        self.resize(1200, 800)
        self.setMinimumSize(1000, 700)


        # Required internal structures
        self.pages = {}
        self._open_pages = {}   # <-- REQUIRED for page reuse

        # Build layout
        container = QWidget()
        layout = QHBoxLayout(container)

        self.sidebar_list = QListWidget()
        self.sidebar_list.itemClicked.connect(self._handle_sidebar_click)

        self.stack = QStackedWidget()   # <-- REQUIRED for page display

        layout.addWidget(self.sidebar_list)
        layout.addWidget(self.stack)

        self.setCentralWidget(container)



    # -----------------------------
    # Add a page to the sidebar
    # -----------------------------
    def add_page(self, label, factory, required_permission=None):

        # Determine active user safely
        user = getattr(self, "current_user", None) or getattr(self, "user", None)
        username = user.username if user else "unknown"

        log_event("debug", "Registering admin page",
                  page=label, required_permission=required_permission)

        # Permission filtering
        if required_permission:
            perms = getattr(user, "permissions", [])
            if required_permission not in perms and "*" not in perms:
                log_event("warn", "Admin page blocked",
                          user=username,
                          page=label,
                          required_permission=required_permission)
                return

        # Store page factory
        self.pages[label] = factory
        log_event("debug", "Admin page stored",
                  page=label, factory=str(factory))

        # Add to sidebar
        self.sidebar_list.addItem(label)
        log_event("info", "Admin page added",
                  user=username, page=label)

    # -----------------------------
    # Handle sidebar click
    # -----------------------------
    def _handle_sidebar_click(self, item):
        # print("SIDEBAR CLICKED:", item.text())

        label = item.text().strip()

        user = getattr(self, "current_user", None) or getattr(self, "user", None)
        username = user.username if user else "unknown"

        log_event("info", "Admin sidebar clicked",
                  user=username, page=label)

        factory = self.pages.get(label)

        if factory is None:
            log_event("error", "No page factory found",
                      user=username, page=label)
            return

        self._open_page(factory)

    # -----------------------------
    # Open or reuse a page
    # -----------------------------
    def _open_page(self, factory):
        # print("OPEN_PAGE CALLED")
        # print(">>> INIT FOUND ON CLASS:", AuditLogPage.__dict__.get("__init__"))

        user = getattr(self, "current_user", None) or getattr(self, "user", None)
        username = user.username if user else "unknown"

        # Reuse existing page
        if factory in self._open_pages:
            log_event("info", "Admin page reused",
                    user=username, page=str(factory))

            page = self._open_pages[factory]
            self.stack.setCurrentWidget(page)

            # print(">>> PAGE MODULE:", page.__class__.__module__)
            # print(">>> PAGE FILE:", page.__class__.__module__.replace('.', '/') + ".py")

            return

        # Create new page
        log_event("info", "Opening admin page",
                user=username, page=str(factory))

        page = factory()
        # print(">>> PAGE INSTANCE TYPE:", type(page))
        # print(">>> PAGE INSTANCE DIR:", dir(page))
        # print(">>> PAGE INIT BOUND:", getattr(page, "__init__", None))


        import inspect
        # print(">>> CLASS DEFINITION LOCATION:", inspect.getsourcefile(page.__class__))
        # print(">>> CLASS DEFINITION LINE:", inspect.getsourcelines(page.__class__)[1])
        # print(">>> RUNTIME CLASS OBJECT ID:", id(page.__class__))

        self._open_pages[factory] = page
        self.stack.addWidget(page)
        self.stack.setCurrentWidget(page)

        # print(">>> ACTUAL PAGE MODULE:", page.__class__.__module__)
        # print(">>> ACTUAL PAGE CLASS:", page.__class__)
        # print(">>> ACTUAL PAGE FILE:", page.__class__.__module__.replace('.', '/') + ".py")

