# roles_page.py
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QTableWidget, QTableWidgetItem, QMessageBox
)
from ui.dialogs.role_editor_dialog import RoleEditorDialog
from ui.components.logger import logger


class RolesPage(QWidget):
    def __init__(self, mongo_service, parent=None):
        super().__init__(parent)
        self.mongo = mongo_service

        self.layout = QVBoxLayout(self)

        # --- Toolbar ---
        toolbar = QHBoxLayout()
        self.btn_add = QPushButton("Add Role")
        self.btn_edit = QPushButton("Edit Role")
        self.btn_delete = QPushButton("Delete Role")

        toolbar.addWidget(self.btn_add)
        toolbar.addWidget(self.btn_edit)
        toolbar.addWidget(self.btn_delete)
        toolbar.addStretch()

        self.layout.addLayout(toolbar)

        # --- Table ---
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["Role", "Permissions", "Description", "Users"])
        self.layout.addWidget(self.table)

        # --- Signals ---
        self.btn_add.clicked.connect(self.add_role)
        self.btn_edit.clicked.connect(self.edit_role)
        self.btn_delete.clicked.connect(self.delete_role)

        self.refresh()


    # ---------------------------------------------------------
    def refresh(self):
        roles = self.mongo.get_all_roles()
        self.table.setRowCount(len(roles))

        for row, role in enumerate(roles):
            name = role["name"]
            perms = ", ".join(role["permissions"])
            desc = role.get("description", "")
            count = self.mongo.count_users_with_role(name)

            self.table.setItem(row, 0, QTableWidgetItem(name))
            self.table.setItem(row, 1, QTableWidgetItem(perms))
            self.table.setItem(row, 2, QTableWidgetItem(desc))
            self.table.setItem(row, 3, QTableWidgetItem(str(count)))

        self.table.resizeColumnsToContents()


    # ---------------------------------------------------------
    def get_selected_role(self):
        row = self.table.currentRow()
        if row < 0:
            return None
        return self.table.item(row, 0).text()


    # ---------------------------------------------------------
    def add_role(self):
        dialog = RoleEditorDialog(self.mongo, mode="add")
        if dialog.exec():
            self.refresh()


    # ---------------------------------------------------------
    def edit_role(self):
        role_name = self.get_selected_role()
        if not role_name:
            QMessageBox.warning(self, "No selection", "Please select a role to edit.")
            return

        dialog = RoleEditorDialog(self.mongo, mode="edit", role_name=role_name)
        if dialog.exec():
            self.refresh()


    # ---------------------------------------------------------
    def delete_role(self):
        role_name = self.get_selected_role()
        if not role_name:
            QMessageBox.warning(self, "No selection", "Please select a role to delete.")
            return

        count = self.mongo.count_users_with_role(role_name)
        if count > 0:
            QMessageBox.warning(
                self,
                "Cannot delete",
                f"Role '{role_name}' cannot be deleted because {count} users have it."
            )
            return

        confirm = QMessageBox.question(
            self,
            "Confirm Delete",
            f"Delete role '{role_name}'?"
        )

        if confirm == QMessageBox.Yes:
            self.mongo.delete_role(role_name, performed_by="admin")
            logger.info(f"Role '{role_name}' deleted.")
            self.refresh()
