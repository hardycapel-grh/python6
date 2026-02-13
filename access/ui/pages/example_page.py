from PySide6.QtWidgets import QVBoxLayout, QLabel, QLineEdit, QPushButton, QTextEdit, QComboBox
from base_page import BasePage

class ExamplePage(BasePage):
    title = "Example Page"

    def __init__(self):
        super().__init__()

        layout = QVBoxLayout()
        self.setLayout(layout)

        layout.addWidget(QLabel("Editable field:", self))

        self.field = QLineEdit(self)
        layout.addWidget(self.field)

        save_btn = QPushButton("Save", self)
        layout.addWidget(save_btn)

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