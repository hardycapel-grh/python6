from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QMessageBox
)
from ui.components.permissions_selector_widget import PermissionsSelectorWidget

from ui.components.logger import logger


class RoleEditorDialog(QDialog):
    def __init__(self, mongo_service, mode="add", role_name=None, parent=None):
        super().__init__(parent)
        self.mongo = mongo_service
        self.mode = mode
        self.role_name = role_name

        self.setWindowTitle("Add Role" if mode == "add" else f"Edit Role: {role_name}")

        layout = QVBoxLayout(self)

        # --- Role Name ---
        layout.addWidget(QLabel("Role Name:"))
        self.name_edit = QLineEdit()
        layout.addWidget(self.name_edit)

        # --- Description ---
        layout.addWidget(QLabel("Description:"))
        self.desc_edit = QLineEdit()
        layout.addWidget(self.desc_edit)

        # --- Permissions ---
        layout.addWidget(QLabel("Permissions:"))

        # NEW: instantiate selector with mongo + selected list
        selected = []
        if mode == "edit":
            role = self.mongo.get_role(role_name)
            selected = role.get("permissions", [])

        self.perm_widget = PermissionsSelectorWidget(
            mongo=self.mongo,
            selected=selected
        )

        
        layout.addWidget(self.perm_widget)

        # Autofocus
        if mode == "add":
            self.name_edit.setFocus()
        else:
            self.desc_edit.setFocus()

        # --- Buttons ---
        btns = QHBoxLayout()
        self.btn_save = QPushButton("Save")
        self.btn_cancel = QPushButton("Cancel")
        btns.addWidget(self.btn_save)
        btns.addWidget(self.btn_cancel)
        layout.addLayout(btns)

        self.btn_save.clicked.connect(self.save)
        self.btn_cancel.clicked.connect(self.reject)

        self.name_edit.returnPressed.connect(self.save)
        self.desc_edit.returnPressed.connect(self.save)

        if mode == "edit":
            self.load_role()


    # ---------------------------------------------------------
    def load_role(self):
        role = self.mongo.get_role(self.role_name)

        self.name_edit.setText(role["name"])
        self.name_edit.setDisabled(True)

        self.desc_edit.setText(role.get("description", ""))
        self.desc_edit.selectAll()


    # ---------------------------------------------------------
    def save(self):
        name = self.name_edit.text().strip()
        desc = self.desc_edit.text().strip()

        # NEW: correct API for the new widget
        perms = self.perm_widget.get_selected_permissions()


        if not name:
            QMessageBox.warning(self, "Missing name", "Role name cannot be empty.")
            return

        try:
            if self.mode == "add":
                self.mongo.create_role(name, perms, desc, performed_by="admin")
                logger.info(f"Role '{name}' created.")
            else:
                self.mongo.update_role(name, perms, desc, performed_by="admin")
                logger.info(f"Role '{name}' updated.")

            self.accept()

        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))
