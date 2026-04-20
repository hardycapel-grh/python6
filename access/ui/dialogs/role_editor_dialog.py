# role_editor_dialog.py
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QMessageBox
)
from ui.widgets.permissions_selector import PermissionsSelectorWidget
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
        self.perm_widget = PermissionsSelectorWidget()
        layout.addWidget(self.perm_widget)

        # --- Buttons ---
        btns = QHBoxLayout()
        self.btn_save = QPushButton("Save")
        self.btn_cancel = QPushButton("Cancel")
        btns.addWidget(self.btn_save)
        btns.addWidget(self.btn_cancel)
        layout.addLayout(btns)

        self.btn_save.clicked.connect(self.save)
        self.btn_cancel.clicked.connect(self.reject)

        if mode == "edit":
            self.load_role()


    # ---------------------------------------------------------
    def load_role(self):
        role = self.mongo.get_role(self.role_name)
        self.name_edit.setText(role["name"])
        self.name_edit.setDisabled(True)  # LOCKED

        self.desc_edit.setText(role.get("description", ""))
        self.perm_widget.set_permissions(role["permissions"])


    # ---------------------------------------------------------
    def save(self):
        name = self.name_edit.text().strip()
        desc = self.desc_edit.text().strip()
        perms = self.perm_widget.get_permissions()

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
