# permission_editor_dialog.py
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QMessageBox
)
from ui.components.logger import logger


class PermissionEditorDialog(QDialog):
    def __init__(self, mongo_service, mode="add", permission_name=None, parent=None):
        super().__init__(parent)
        self.mongo = mongo_service
        self.mode = mode
        self.permission_name = permission_name

        self.setWindowTitle("Add Permission" if mode == "add" else f"Edit Permission: {permission_name}")

        layout = QVBoxLayout(self)

        # --- Name ---
        layout.addWidget(QLabel("Permission Name:"))
        self.name_edit = QLineEdit()
        layout.addWidget(self.name_edit)

        # --- Category ---
        layout.addWidget(QLabel("Category:"))
        self.category_edit = QLineEdit()
        layout.addWidget(self.category_edit)

        # --- Description ---
        layout.addWidget(QLabel("Description:"))
        self.desc_edit = QLineEdit()
        layout.addWidget(self.desc_edit)

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
            self.load_permission()


    # ---------------------------------------------------------
    def load_permission(self):
        perm = self.mongo.get_permission(self.permission_name)
        self.name_edit.setText(perm["name"])
        self.name_edit.setDisabled(True)  # LOCKED

        self.category_edit.setText(perm.get("category", ""))
        self.desc_edit.setText(perm.get("description", ""))


    # ---------------------------------------------------------
    def save(self):
        name = self.name_edit.text().strip()
        category = self.category_edit.text().strip()
        desc = self.desc_edit.text().strip()

        if not name:
            QMessageBox.warning(self, "Missing name", "Permission name cannot be empty.")
            return

        try:
            if self.mode == "add":
                self.mongo.create_permission(name, category, desc, performed_by="admin")
                logger.info(f"Permission '{name}' created.")
            else:
                self.mongo.update_permission(name, category, desc, performed_by="admin")
                logger.info(f"Permission '{name}' updated.")

            self.accept()

        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))
