from PySide6.QtWidgets import QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem, QLabel
from ui.components.logger import logger
from services.mongo_service import MongoService


class UserManagerPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        layout = QVBoxLayout(self)
        self.setLayout(layout)

        self.table = QTableWidget()
        layout.addWidget(self.table)

        logger.info("UserManagerPage loaded")

        self.mongo = MongoService()
        self.load_users()

    def load_users(self):
        users = self.mongo.get_users()

        if not users:
            self.table.setRowCount(0)
            self.table.setColumnCount(1)
            self.table.setHorizontalHeaderLabels(["No users found"])
            return

        # Determine columns from first user document
        columns = list(users[0].keys())
        self.table.setColumnCount(len(columns))
        self.table.setHorizontalHeaderLabels(columns)
        self.table.setRowCount(len(users))

        for row, user in enumerate(users):
            for col, key in enumerate(columns):
                value = str(user.get(key, ""))
                self.table.setItem(row, col, QTableWidgetItem(value))

        logger.info("User table populated")