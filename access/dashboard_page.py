from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel
from PySide6.QtCore import Qt
from logger import logger


class DashboardPage(QWidget):
    def __init__(self):
        super().__init__()
        self.title = "Dashboard"
        self.build_ui()

    def build_ui(self):
        layout = QVBoxLayout()

        label = QLabel("Welcome to the Dashboard")
        label.setAlignment(Qt.AlignCenter)
        layout.addWidget(label)

        # Placeholder for future dashboard widgets
        # e.g., stats, charts, summaries, quick actions

        self.setLayout(layout)

    def set_read_only(self, readonly: bool):
        """
        Dashboard currently has no editable widgets,
        but this method is required for permission control.
        """
        if readonly:
            logger.info("Dashboard set to read-only mode")
        else:
            logger.info("Dashboard set to read-write mode")