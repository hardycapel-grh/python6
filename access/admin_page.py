from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton
from PySide6.QtCore import Qt

from user_manager_dialog import UserManagerDialog
from logger import logger


class AdminPage(QWidget):
    def __init__(self):
        super().__init__()
        self.title = "Admin"
        self.build_ui()

    def build_ui(self):
        layout = QVBoxLayout()

        label = QLabel("Admin Control Panel")
        label.setAlignment(Qt.AlignCenter)
        layout.addWidget(label)

        # Manage Users button
        self.manage_users_btn = QPushButton("Manage Users")
        self.manage_users_btn.clicked.connect(self.open_user_manager)
        layout.addWidget(self.manage_users_btn)

        self.setLayout(layout)

    def open_user_manager(self):
        logger.info("Admin opened User Manager")
        dlg = UserManagerDialog(self)
        dlg.exec()

    def set_read_only(self, readonly: bool):
        """
        Admin page respects read-only mode.
        If user has 'ro' permission for Admin, disable admin actions.
        """
        self.manage_users_btn.setEnabled(not readonly)
