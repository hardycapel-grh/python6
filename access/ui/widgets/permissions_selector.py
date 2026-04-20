# permissions_selector.py
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QListWidget,
    QPushButton, QLineEdit, QListWidgetItem
)


class PermissionsSelectorWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        layout = QVBoxLayout(self)

        self.list = QListWidget()
        layout.addWidget(self.list)

        # Add permission box
        add_layout = QHBoxLayout()
        self.input = QLineEdit()
        self.btn_add = QPushButton("Add")
        add_layout.addWidget(self.input)
        add_layout.addWidget(self.btn_add)
        layout.addLayout(add_layout)

        self.btn_add.clicked.connect(self.add_permission)


    # ---------------------------------------------------------
    def add_permission(self):
        text = self.input.text().strip()
        if text:
            self.list.addItem(text)
            self.input.clear()


    # ---------------------------------------------------------
    def set_permissions(self, permissions):
        self.list.clear()
        for p in permissions:
            self.list.addItem(p)


    # ---------------------------------------------------------
    def get_permissions(self):
        return [self.list.item(i).text() for i in range(self.list.count())]
