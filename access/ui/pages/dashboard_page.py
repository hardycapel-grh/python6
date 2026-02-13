from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QLineEdit, QTextEdit, QComboBox
from PySide6.QtCore import Qt
from ui.components.logger import logger



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

    def set_read_only(self, ro: bool):
        """Enable or disable editing for all input widgets."""
        for widget in self.findChildren((QLineEdit, QTextEdit, QComboBox)):
            if isinstance(widget, QLineEdit):
                widget.setReadOnly(ro)
            elif isinstance(widget, QTextEdit):
                widget.setReadOnly(ro)
            elif isinstance(widget, QComboBox):
                widget.setEnabled(not ro)

        # Disable buttons that modify data
        for btn in self.findChildren(QPushButton):
            if btn.objectName() not in ("nav", "close", "back"):
                btn.setEnabled(not ro)

    def apply_permissions(self, perm):
        if perm == "rw":
            return

        # Disable all buttons
        for btn in self.findChildren(QPushButton):
            btn.setEnabled(False)

        # Disable editable widgets
        for t in (QLineEdit, QTextEdit, QComboBox):
            for widget in self.findChildren(t):
                widget.setEnabled(False)

        # Optional banner
        banner = QLabel("Read-Only Mode")
        banner.setStyleSheet("color: orange; font-weight: bold;")
        self.layout().insertWidget(0, banner)