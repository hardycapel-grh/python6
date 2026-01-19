from PySide6.QtWidgets import QVBoxLayout, QLabel, QLineEdit, QPushButton
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