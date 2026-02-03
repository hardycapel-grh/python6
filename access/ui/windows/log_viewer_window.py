from PySide6.QtWidgets import QMainWindow, QDockWidget, QListWidget
from PySide6.QtCore import Qt
from ui.log_viewer_page import LogViewerPage

class LogViewerWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Log Viewer")

        # Create the main viewer
        self.viewer = LogViewerPage()
        self.setCentralWidget(self.viewer)

        # Create the dockable tools panel
        self.create_dock_panel()

        # Create the search results dock
        self.create_search_results_dock()

        # Now that everything exists, size the window naturally
        self.adjustSize()

        # Minimum size so it never collapses too small
        self.setMinimumSize(800, 500)

    def create_dock_panel(self):
        dock = QDockWidget("Advanced Tools", self)
        dock.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)

        # Use the viewer's existing advanced_frame as the dock widget
        dock.setWidget(self.viewer.advanced_frame)

        self.addDockWidget(Qt.LeftDockWidgetArea, dock)

        dock.setFeatures(
            QDockWidget.DockWidgetMovable |
            QDockWidget.DockWidgetFloatable
        )

        dock.setMinimumWidth(150)
        dock.setMaximumWidth(300)

    def create_search_results_dock(self):
        dock = QDockWidget("Search Results", self)
        dock.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)

        # Create the list widget that will hold results
        self.viewer.search_results_list = QListWidget()
        dock.setWidget(self.viewer.search_results_list)

        self.addDockWidget(Qt.RightDockWidgetArea, dock)

        dock.setFeatures(
            QDockWidget.DockWidgetMovable |
            QDockWidget.DockWidgetFloatable
        )

        dock.setMinimumWidth(250)
        dock.setMaximumWidth(400)