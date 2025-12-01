# page1.py
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QHBoxLayout
from PySide6.QtCore import Qt

class Page3(QWidget):
    def __init__(self, switch_function):
        super().__init__()
        layout = QVBoxLayout()

        label = QLabel("Welcome to Page 3 - the information page")
        label.setAlignment(Qt.AlignCenter)
        layout.addWidget(label)
        layout.addStretch()

        button_layout = QHBoxLayout()
        for i in range(4):
            btn = QPushButton(f"Go to Page {i + 1}")
            btn.clicked.connect(lambda _, target=i: switch_function(target))
            button_layout.addWidget(btn)

        layout.addLayout(button_layout)
        layout.addStretch()
        self.setLayout(layout)