from PySide6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QLabel
from ui.components.logger import logger

class AdminControlWindow(QMainWindow):
    def __init__(self, user):
        super().__init__()
        self.user = user

        self.setWindowTitle("Admin Control Panel")
        self.resize(900, 600)

        central = QWidget()
        layout = QVBoxLayout(central)

        layout.addWidget(QLabel(f"Admin Control Panel — Logged in as: {user['username']}"))

        # TODO: Add admin tools here

        self.setCentralWidget(central)

        logger.info(f"Admin Control Panel opened by '{user['username']}'")