from PySide6.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QListWidget, QStackedWidget
)
from ui.components.logger import logger


class WindowWithSidebar(QMainWindow):
    def __init__(self, title="Tool Window"):
        super().__init__()
        self.setWindowTitle(title)
        self.resize(1200, 800)

        logger.info(f"{title} initialised")

        # Root container
        root = QWidget()
        root_layout = QHBoxLayout(root)
        self.setCentralWidget(root)

        # Sidebar (left navigation)
        self.sidebar = QListWidget()
        self.sidebar.setFixedWidth(200)
        self.sidebar.itemClicked.connect(self._handle_sidebar_click)
        root_layout.addWidget(self.sidebar)

        # Main content area (stacked pages)
        self.main_pane = QStackedWidget()
        root_layout.addWidget(self.main_pane, 1)

        # Internal registry of pages
        self._pages = {}

    def add_page(self, name: str, widget: QWidget):
        """Register a page and add it to the stacked widget."""
        self._pages[name] = widget
        self.main_pane.addWidget(widget)
        self.sidebar.addItem(name)
        logger.info(f"Page registered: {name}")

    def _handle_sidebar_click(self, item):
        name = item.text()
        logger.info(f"Sidebar clicked: {name}")

        if name in self._pages:
            widget = self._pages[name]
            self.main_pane.setCurrentWidget(widget)
            logger.info(f"Switched to page: {name}")