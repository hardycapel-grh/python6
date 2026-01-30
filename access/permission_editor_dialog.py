from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QComboBox, QPushButton, QMessageBox
)

from database import get_user, update_permissions
from ui.logger import logger






class PermissionEditorDialog(QDialog):
    def __init__(self, username, parent=None):
        super().__init__(parent)
        
        from page_registry import PAGE_REGISTRY   # <-- FIX
        self.setWindowTitle(f"Edit Permissions: {username}")
        self.setMinimumWidth(500)
        self.username = username

        layout = QVBoxLayout()

        # Load user from database
        self.user = get_user(username)
        if not self.user:
            QMessageBox.critical(self, "Error", "User not found")
            logger.error(f"Permission editor failed: user '{username}' not found")
            self.close()
            return

        self.perms = self.user.get("permissions", {})
        self.fields = {}

        # Build UI dynamically from PAGE_REGISTRY
        for page_name in PAGE_REGISTRY.keys():
            layout.addWidget(QLabel(page_name))

            combo = QComboBox()
            combo.addItems(["None", "ro", "rw"])

            current = self.perms.get(page_name)

            if current is None:
                combo.setCurrentText("None")
            else:
                combo.setCurrentText(current)

            self.fields[page_name] = combo
            layout.addWidget(combo)

        save_btn = QPushButton("Save")
        save_btn.clicked.connect(self.save)
        layout.addWidget(save_btn)

        self.setLayout(layout)

    def save(self):
        new_perms = {}

        for page_name, combo in self.fields.items():
            val = combo.currentText()
            new_perms[page_name] = None if val == "None" else val

        success = update_permissions(self.username, new_perms)

        if success:
            logger.info(f"Permissions updated for user '{self.username}'")
            QMessageBox.information(self, "Success", "Permissions updated")
            self.accept()
        else:
            logger.error(f"Failed to update permissions for '{self.username}'")
            QMessageBox.critical(self, "Error", "Failed to update permissions")