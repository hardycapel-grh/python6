from PySide6.QtWidgets import QWidget, QVBoxLayout
from AdminControlPanel import AdminControlPanel


class AdminPage(QWidget):
    def __init__(self):
        super().__init__()
        self.title = "Admin"

        layout = QVBoxLayout()

        # Full-size embedded admin panel
        self.panel = AdminControlPanel()
        self.panel.setMinimumHeight(600)   # ensures full UI is visible
        self.panel.setMinimumWidth(800)

        layout.addWidget(self.panel, stretch=1)

        self.setLayout(layout)

    def set_read_only(self, readonly: bool):
        pass