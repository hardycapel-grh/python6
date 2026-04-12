import bcrypt
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem,
    QLabel, QPushButton, QHBoxLayout, QMessageBox
)
from ui.components.logger import logger
from services.mongo_service import MongoService
from ui.dialogs.user_dialogs import (
    AddUserDialog, EditUserDialog,
    DeleteUserDialog, ResetPasswordDialog
)


class UserManagerPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        layout = QVBoxLayout(self)
        self.setLayout(layout)

        # -------------------------
        # Toolbar (Admin actions)
        # -------------------------
        toolbar = QHBoxLayout()

        self.add_btn = QPushButton("Add User")
        self.add_btn.clicked.connect(self.add_user)
        toolbar.addWidget(self.add_btn)

        self.edit_btn = QPushButton("Edit User")
        self.edit_btn.clicked.connect(self.edit_user)
        toolbar.addWidget(self.edit_btn)

        self.delete_btn = QPushButton("Delete User")
        self.delete_btn.clicked.connect(self.delete_user)
        toolbar.addWidget(self.delete_btn)

        self.reset_pw_btn = QPushButton("Reset Password")
        self.reset_pw_btn.clicked.connect(self.reset_password)
        toolbar.addWidget(self.reset_pw_btn)

        self.force_pw_btn = QPushButton("Force Password Change")
        self.force_pw_btn.clicked.connect(self.force_password_change)
        toolbar.addWidget(self.force_pw_btn)

        toolbar.addStretch()

        self.refresh_btn = QPushButton("Refresh")
        self.refresh_btn.clicked.connect(self.load_users)
        toolbar.addWidget(self.refresh_btn)

        layout.addLayout(toolbar)

        # -------------------------
        # User table
        # -------------------------
        self.table = QTableWidget()
        layout.addWidget(self.table)

        logger.info("UserManagerPage loaded")

        self.mongo = MongoService()
        self.load_users()

        self.table.itemDoubleClicked.connect(self.on_row_double_clicked)

    # -------------------------------------------------
    # Load users into table
    # -------------------------------------------------
    def load_users(self):
        users = self.mongo.get_users()

        if not users:
            self.table.setRowCount(0)
            self.table.setColumnCount(1)
            self.table.setHorizontalHeaderLabels(["No users found"])
            return

        # Remove internal/unwanted fields
        for u in users:
            u.pop("_id", None)
            u.pop("password_hash", None)
            u.pop("password", None)
            u.pop("theme", None)
            u.pop("must_change_password", None)

        # Preferred clean column order
        preferred_order = [
            "username",
            "email",
            "role",
            "permissions",
            "phone",
            "last_login"
        ]

        columns = [c for c in preferred_order if c in users[0]]
        for c in users[0].keys():
            if c not in columns:
                columns.append(c)

        self.table.setColumnCount(len(columns))
        self.table.setHorizontalHeaderLabels(columns)
        self.table.setRowCount(len(users))

        for row, user in enumerate(users):
            for col, key in enumerate(columns):
                value = user.get(key, "")

                if key == "permissions" and isinstance(value, dict):
                    value = ", ".join(f"{k}:{v}" for k, v in value.items())

                self.table.setItem(row, col, QTableWidgetItem(str(value)))

        logger.info("User table populated")

    # -------------------------------------------------
    # Toolbar button handlers (Step 3 will implement)
    # -------------------------------------------------
    def get_selected_username(self):
        row = self.table.currentRow()
        if row < 0:
            QMessageBox.warning(self, "No selection", "Please select a user first.")
            return None

        username = self.table.item(row, 0).text()  # username is column 0
        return username

    def add_user(self):
        dlg = AddUserDialog(self.mongo, self)
        if dlg.exec():
            self.load_users()

    def edit_user(self):
        username = self.get_selected_username()
        if not username:
            return

        # Build user_data dict from table row
        row = self.table.currentRow()
        user_data = {}
        for col in range(self.table.columnCount()):
            key = self.table.horizontalHeaderItem(col).text()
            user_data[key] = self.table.item(row, col).text()

        dlg = EditUserDialog(
            user_doc=user_data,
            current_user=self.current_user,   # ← pass it in
            parent=self
        )
        dlg.exec()

    def delete_user(self):
        username = self.get_selected_username()
        if not username:
            return

        dlg = DeleteUserDialog(self.mongo, username, self)
        if dlg.exec():
            self.load_users()

    def reset_password(self):
        username = self.get_selected_username()
        if not username:
            return

        dlg = ResetPasswordDialog(self.mongo, username, self)
        if dlg.exec():
            self.load_users()


    def force_password_change(self):
        username = self.get_selected_username()
        if not username:
            return

        self.mongo.update_user_fields(username, {"must_change_password": True})
        QMessageBox.information(self, "Done", f"{username} must change password on next login.")

    def on_row_double_clicked(self, item):
        row = item.row()
        username = self.table.item(row, 0).text()  # assuming column 0 = username

        # Build user_data dict from the row
        user_data = {}
        for col in range(self.table.columnCount()):
            key = self.table.horizontalHeaderItem(col).text()
            user_data[key] = self.table.item(row, col).text()

        dlg = EditUserDialog(
            user_doc=user_data,
            current_user=self.current_user,   # ← pass it in
            parent=self
        )
        dlg.exec()
