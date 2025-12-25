from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton
from PySide6.QtCore import Qt


class AdminPage(QWidget):
    def __init__(self):
        super().__init__()
        self.title = "Admin"
        self.build_ui()

    def build_ui(self):
        layout = QVBoxLayout()

        label = QLabel("Admin Page")
        label.setAlignment(Qt.AlignCenter)
        layout.addWidget(label)

        # Example admin-only button
        self.admin_button = QPushButton("Perform Admin Action")
        layout.addWidget(self.admin_button)

        self.setLayout(layout)

    def set_read_only(self, readonly: bool):
        # Admin page should disable admin actions in read-only mode
        self.admin_button.setEnabled(not readonly)

        for widget in self.findChildren(QWidget):
            if widget is not self.admin_button:
                if hasattr(widget, "setEnabled"):
                    widget.setEnabled(not readonly)