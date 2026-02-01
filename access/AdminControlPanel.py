from PySide6.QtWidgets import (
    QVBoxLayout, QLabel, QPushButton, QTableWidget, QTableWidgetItem,
    QHBoxLayout, QMessageBox, QComboBox, QLineEdit, QWidget, QToolButton, QMenu
)
from PySide6.QtCore import Qt

import bcrypt

from ui.components.logger import logger
from database import (
    get_all_users, update_permissions, delete_user,
    update_password, update_user_fields
)

from base_page import BasePage


class AdminControlPanel(BasePage):
    title = "Admin Control Panel"

    def __init__(self):
        super().__init__()

        layout = QVBoxLayout()
        self.setLayout(layout)

        title = QLabel("Admin Control Panel", self)
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        # User table
        self.table = QTableWidget(self)
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["Username", "Email", "Role", "Actions"])
        layout.addWidget(self.table)

        # Refresh button (safe)
        self.refresh_btn = QPushButton("Refresh Users", self)
        self.refresh_btn.setObjectName("safe")  # stays enabled in RO mode
        self.refresh_btn.clicked.connect(self.load_users)
        layout.addWidget(self.refresh_btn)

        # Load users
        self.load_users()

    # ---------------------------------------------------------
    # LOAD USERS
    # ---------------------------------------------------------
    def load_users(self):
        users = get_all_users()
        self.table.setRowCount(len(users))

        for row, user in enumerate(users):
            username = user.get("username", "")
            email = user.get("email", "")
            role = user.get("role", "")

            # Username
            self.table.setItem(row, 0, QTableWidgetItem(username))

            # Email
            self.table.setItem(row, 1, QTableWidgetItem(email))

            # Role
            self.table.setItem(row, 2, QTableWidgetItem(role))

            # Actions menu
            btn_actions = QToolButton(self)
            btn_actions.setText("Actions")
            btn_actions.setPopupMode(QToolButton.InstantPopup)
            btn_actions.setMinimumWidth(120)
            btn_actions.setMinimumHeight(32)

            menu = QMenu(btn_actions)

            # Menu items
            action_perm = menu.addAction("Edit Permissions")
            action_perm.triggered.connect(lambda _, u=user: self.edit_permissions(u))

            action_reset = menu.addAction("Reset Password")
            action_reset.triggered.connect(lambda _, u=user: self.reset_password(u))

            action_edit = menu.addAction("Edit User")
            action_edit.triggered.connect(lambda _, u=user: self.edit_user_fields(u))

            action_delete = menu.addAction("Delete User")
            action_delete.triggered.connect(lambda _, u=user: self.delete_user(u))

            btn_actions.setMenu(menu)

            # Store references so BasePage can disable them
            btn_actions._menu_actions = {
                "perm": action_perm,
                "reset": action_reset,
                "edit": action_edit,
                "delete": action_delete
            }

            container = QWidget(self)
            c_layout = QVBoxLayout(container)
            c_layout.addWidget(btn_actions)
            c_layout.setAlignment(Qt.AlignCenter)

            self.table.setCellWidget(row, 3, container)
            self.table.setRowHeight(row, 40)
            self.table.horizontalHeader().setStretchLastSection(True)

    # ---------------------------------------------------------
    # PERMISSIONS EDITOR
    # ---------------------------------------------------------
    def edit_permissions(self, user):
        if self._is_read_only():
            QMessageBox.warning(self, "Permission Denied", "Read-only mode")
            return

        from page_registry import PAGE_REGISTRY
        username = user["username"]
        permissions = user.get("permissions", {})

        dlg = QWidget()
        dlg.setWindowTitle(f"Edit Permissions: {username}")
        dlg.setLayout(QVBoxLayout())

        combo_boxes = {}

        for page, info in PAGE_REGISTRY.items():
            row = QHBoxLayout()
            row.addWidget(QLabel(page))

            combo = QComboBox()
            combo.addItems(["none", "ro", "rw"])
            combo.setCurrentText(permissions.get(page, "none"))
            combo_boxes[page] = combo

            row.addWidget(combo)
            dlg.layout().addLayout(row)

        save_btn = QPushButton("Save")
        dlg.layout().addWidget(save_btn)

        def save():
            new_perms = {page: combo.currentText() for page, combo in combo_boxes.items()}
            if update_permissions(username, new_perms):
                QMessageBox.information(self, "Success", "Permissions updated")
                logger.info(f"Admin updated permissions for '{username}'")
                dlg.close()
                self.load_users()

                # Refresh navigation bar
                main = self.window()
                if hasattr(main, "refresh_navigation"):
                    main.refresh_navigation()
            else:
                QMessageBox.critical(self, "Error", "Failed to update permissions")

        save_btn.clicked.connect(save)
        dlg.show()

    # ---------------------------------------------------------
    # RESET PASSWORD
    # ---------------------------------------------------------
    def reset_password(self, user):
        if self._is_read_only():
            QMessageBox.warning(self, "Permission Denied", "Read-only mode")
            return

        username = user["username"]
        temp_pw = "Temp123!"
        hashed = bcrypt.hashpw(temp_pw.encode(), bcrypt.gensalt())

        if update_password(username, hashed):
            QMessageBox.information(
                self,
                "Password Reset",
                f"Temporary password for {username}:\n\n{temp_pw}"
            )
            logger.info(f"Admin reset password for '{username}'")
        else:
            QMessageBox.critical(self, "Error", "Failed to reset password")

    # ---------------------------------------------------------
    # EDIT USER FIELDS
    # ---------------------------------------------------------
    def edit_user_fields(self, user):
        if self._is_read_only():
            QMessageBox.warning(self, "Permission Denied", "Read-only mode")
            return

        username = user["username"]

        dlg = QWidget()
        dlg.setWindowTitle(f"Edit User: {username}")
        dlg.setLayout(QVBoxLayout())

        email = QLineEdit(user.get("email", ""))
        phone = QLineEdit(user.get("phone", ""))
        theme = QLineEdit(user.get("theme", ""))

        dlg.layout().addWidget(QLabel("Email"))
        dlg.layout().addWidget(email)

        dlg.layout().addWidget(QLabel("Phone"))
        dlg.layout().addWidget(phone)

        dlg.layout().addWidget(QLabel("Theme"))
        dlg.layout().addWidget(theme)

        save_btn = QPushButton("Save")
        dlg.layout().addWidget(save_btn)

        def save():
            fields = {
                "email": email.text().strip(),
                "phone": phone.text().strip(),
                "theme": theme.text().strip()
            }

            if update_user_fields(username, fields):
                QMessageBox.information(self, "Success", "User updated")
                logger.info(f"Admin updated fields for '{username}'")
                dlg.close()
                self.load_users()
            else:
                QMessageBox.critical(self, "Error", "Failed to update user")

        save_btn.clicked.connect(save)
        dlg.show()

    # ---------------------------------------------------------
    # DELETE USER
    # ---------------------------------------------------------
    def delete_user(self, user):
        if self._is_read_only():
            QMessageBox.warning(self, "Permission Denied", "Read-only mode")
            return

        username = user["username"]

        confirm = QMessageBox.question(
            self,
            "Confirm Delete",
            f"Are you sure you want to delete '{username}'?"
        )

        if confirm != QMessageBox.Yes:
            return

        if delete_user(username):
            QMessageBox.information(self, "Deleted", f"User '{username}' deleted")
            logger.info(f"Admin deleted user '{username}'")
            self.load_users()
        else:
            QMessageBox.critical(self, "Error", "Failed to delete user")

    # ---------------------------------------------------------
    # INTERNAL: Check if page is in read-only mode
    # ---------------------------------------------------------
    def _is_read_only(self):
        # BasePage sets this attribute automatically
        return getattr(self, "_BasePage__read_only", False)