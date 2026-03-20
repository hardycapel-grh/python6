from PySide6.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QListWidget, QStackedWidget
)
from ui.components.logger import logger


class WindowWithSidebar(QMainWindow):
    def __init__(self, title: str):
        super().__init__()
        self.setWindowTitle(title)

        # Storage for factories and instances
        self.pages = {}           # name → factory
        self.page_instances = {}  # name → QWidget

        # -----------------------------
        # Build UI FIRST
        # -----------------------------
        self.resize(1000, 600)
        self.sidebar = QListWidget()
        self.sidebar.setFixedWidth(200)
        self.sidebar.itemClicked.connect(self._handle_sidebar_click)

        self.main_pane = QStackedWidget()

        container = QWidget()
        layout = QHBoxLayout(container)
        layout.addWidget(self.sidebar)
        layout.addWidget(self.main_pane)
        self.setCentralWidget(container)

        # -----------------------------
        # Now that UI is ready,
        # allow subclass to register pages
        # -----------------------------
        self._setup_pages()

    def _setup_pages(self):
        """Override in subclasses to register pages via add_page()."""
        pass

    def add_page(self, name, page_factory):
        logger.info(f"Registering page '{name}'")
        self.pages[name] = page_factory
        self.sidebar.addItem(name)

    def _handle_sidebar_click(self, item):
        name = item.text()
        logger.info(f"Sidebar clicked: {name}")

        if name not in self.pages:
            logger.error(f"Page '{name}' not registered in pages dict")
            return

        # Lazy creation
        if name not in self.page_instances:
            page = self.pages[name]()  # call factory
            self.page_instances[name] = page
            self.main_pane.addWidget(page)

        self.main_pane.setCurrentWidget(self.page_instances[name])