from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QLabel,
    QPushButton, QStackedWidget, QMessageBox
)
from PySide6.QtCore import Qt

from admin_page import AdminPage
from logger import logger



class Page(QWidget):
    def __init__(self, title):
        super().__init__()
        self.title = title

        layout = QVBoxLayout()
        label = QLabel(title)
        label.setAlignment(Qt.AlignCenter)
        layout.addWidget(label)
        self.setLayout(layout)

    # Generic read-only handler
    def set_read_only(self, readonly: bool):
        for widget in self.findChildren(QWidget):
            if hasattr(widget, "setReadOnly"):
                widget.setReadOnly(readonly)
            elif hasattr(widget, "setEnabled"):
                widget.setEnabled(not readonly)


class MainApp(QMainWindow):
    def __init__(self, user):
        super().__init__()
        self.setWindowTitle("Main Application")

        # Extract user info
        self.username = user.get("username", "Unknown")
        self.role = user.get("role", "guest")
        self.permissions = user.get("permissions", {})
        logger.info(f"MainApp started for user {self.username} with role {self.role}")

        self.setup_ui()

    def setup_ui(self):

        container = QWidget()
        container_layout = QVBoxLayout()

        header = QLabel(f"Logged in as: {self.username} ({self.role})")
        header.setAlignment(Qt.AlignCenter)
        container_layout.addWidget(header)

        # Create pages
        self.stack = QStackedWidget()
        self.pages = [
            Page("Dashboard"),
            Page("Data Table"),
            Page("Charts"),
            AdminPage()
        ]

        # Add pages to stack
        for p in self.pages:
            self.stack.addWidget(p)

        # Build navigation based on permissions
        self.add_navigation_buttons(container_layout)

        container_layout.addWidget(self.stack)
        container.setLayout(container_layout)
        self.setCentralWidget(container)

    def add_navigation_buttons(self, layout):

        for index, page in enumerate(self.pages):
            title = page.title
            perm = self.permissions.get(title)

            if perm is None:
                continue


            btn = QPushButton(title)
            btn.clicked.connect(lambda _, i=index, p=page, permission=perm:
                                self.switch_page(i, p, permission))
            layout.addWidget(btn)

    def switch_page(self, index, page, permission):
        try:


            # Apply read-only mode
            page.set_read_only(permission == "ro")

            self.stack.setCurrentIndex(index)

        except Exception as e:

            QMessageBox.critical(self, "Error", "Could not switch page")