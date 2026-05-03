# ui/pages/admin/permissions_page.py

# permissions_page.py
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QTableWidget, QTableWidgetItem, QMessageBox
)
from ui.dialogs.permission_editor_dialog import PermissionEditorDialog
from ui.components.logger import logger


class PermissionsPage(QWidget):
    def __init__(self, mongo_service, parent=None):
        super().__init__(parent)
        self.mongo = mongo_service
        self.app = parent

        layout = QVBoxLayout(self)

        # --- Toolbar ---
        toolbar = QHBoxLayout()
        self.btn_add = QPushButton("Add Permission")
        self.btn_edit = QPushButton("Edit Permission")
        self.btn_delete = QPushButton("Delete Permission")

        toolbar.addWidget(self.btn_add)
        toolbar.addWidget(self.btn_edit)
        toolbar.addWidget(self.btn_delete)
        toolbar.addStretch()
        layout.addLayout(toolbar)

        self.btn_add.setEnabled(self.app.has_permission("permissions.create"))
        self.btn_edit.setEnabled(self.app.has_permission("permissions.edit"))
        self.btn_delete.setEnabled(self.app.has_permission("permissions.delete"))


        # --- Table ---
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["Permission", "Category", "Description", "Used By"])
        layout.addWidget(self.table)

        # --- Signals ---
        self.btn_add.clicked.connect(self.add_permission)
        self.btn_edit.clicked.connect(self.edit_permission)
        self.btn_delete.clicked.connect(self.delete_permission)

        self.refresh()


    # ---------------------------------------------------------
    def refresh(self):
        perms = self.mongo.get_all_permissions()
        self.table.setRowCount(len(perms))

        for row, perm in enumerate(perms):
            name = perm["name"]
            category = perm.get("category", "")
            desc = perm.get("description", "")
            used_by = self.mongo.count_total_usage_of_permission(name)


            self.table.setItem(row, 0, QTableWidgetItem(name))
            self.table.setItem(row, 1, QTableWidgetItem(category))
            self.table.setItem(row, 2, QTableWidgetItem(desc))
            self.table.setItem(row, 3, QTableWidgetItem(str(used_by)))

        self.table.resizeColumnsToContents()


    # ---------------------------------------------------------
    def get_selected_permission(self):
        row = self.table.currentRow()
        if row < 0:
            return None
        return self.table.item(row, 0).text()


    # ---------------------------------------------------------
    def add_permission(self):
        if not self.app.has_permission("permissions.create"):
            self.app.show_permission_denied()
            return
        dialog = PermissionEditorDialog(self.mongo, mode="add")
        if dialog.exec():
            self.refresh()


    # ---------------------------------------------------------
    def edit_permission(self):
        # --- Permission enforcement ---
        if not self.app.has_permission("permissions.edit"):
            self.app.show_permission_denied()
            return

        name = self.get_selected_permission()
        if not name:
            QMessageBox.warning(self, "No selection", "Please select a permission to edit.")
            return

        dialog = PermissionEditorDialog(self.mongo, mode="edit", permission_name=name)
        if dialog.exec():
            self.refresh()



    # ---------------------------------------------------------
    def delete_permission(self):
    # --- Permission enforcement ---
        if not self.app.has_permission("permissions.delete"):
            self.app.show_permission_denied()
            return

        name = self.get_selected_permission()
        if not name:
            QMessageBox.warning(self, "No selection", "Please select a permission to delete.")
            return

        used_by = self.mongo.count_roles_using_permission(name)
        if used_by > 0:
            QMessageBox.warning(
                self,
                "Cannot delete",
                f"Permission '{name}' cannot be deleted because {used_by} roles use it."
            )
            return

        confirm = QMessageBox.question(
            self,
            "Confirm Delete",
            f"Delete permission '{name}'?"
        )

        if confirm == QMessageBox.Yes:
            self.mongo.delete_permission(name, performed_by="admin")
            logger.info(f"Permission '{name}' deleted.")
            self.refresh()

