from PySide6.QtWidgets import QWidget, QVBoxLayout, QLineEdit, QTextEdit, QComboBox, QPushButton
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