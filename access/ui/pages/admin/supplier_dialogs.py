from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QMessageBox
)

from ui.components.logger_utils import log_event


class AddSupplierDialog(QDialog):
    def __init__(self, mongo, user, parent=None):
        super().__init__(parent)

        self.mongo = mongo
        self.user = user

        self.setWindowTitle("Add Supplier")
        self.setMinimumWidth(350)

        layout = QVBoxLayout(self)

        # Name
        row = QHBoxLayout()
        row.addWidget(QLabel("Name:"))
        self.name = QLineEdit()
        row.addWidget(self.name)
        layout.addLayout(row)

        # Notes
        row = QHBoxLayout()
        row.addWidget(QLabel("Notes:"))
        self.notes = QLineEdit()
        row.addWidget(self.notes)
        layout.addLayout(row)

        # Buttons
        btn_row = QHBoxLayout()
        btn_save = QPushButton("Add")
        btn_cancel = QPushButton("Cancel")

        btn_save.clicked.connect(self._save)
        btn_cancel.clicked.connect(self.reject)

        btn_row.addStretch()
        btn_row.addWidget(btn_save)
        btn_row.addWidget(btn_cancel)

        layout.addLayout(btn_row)

    def _save(self):
        name = self.name.text().strip()
        notes = self.notes.text().strip()

        if not name:
            QMessageBox.warning(self, "Missing Field", "Supplier name is required.")
            return

        existing = self.mongo.suppliers.find_one({"name": name})
        if existing:
            QMessageBox.warning(self, "Duplicate", f"Supplier '{name}' already exists.")
            return

        try:
            self.mongo.suppliers.insert_one({"name": name, "notes": notes})

            self.mongo.log_event(
                "supplier.create",
                performed_by=self.user.username,
                details=f"Created supplier '{name}'"
            )

            log_event("info", "Supplier created", user=self.user.username, supplier=name)

            self.accept()

        except Exception as e:
            log_event("error", "Failed to create supplier",
                      user=self.user.username, supplier=name, error=str(e))
            QMessageBox.critical(self, "Error", f"Failed to create supplier:\n{e}")


class EditSupplierDialog(QDialog):
    def __init__(self, mongo, user, name, parent=None):
        super().__init__(parent)

        self.mongo = mongo
        self.user = user
        self.original_name = name

        self.setWindowTitle(f"Edit Supplier: {name}")
        self.setMinimumWidth(350)

        supplier = self.mongo.suppliers.find_one({"name": name})

        layout = QVBoxLayout(self)

        # Name
        row = QHBoxLayout()
        row.addWidget(QLabel("Name:"))
        self.name = QLineEdit(supplier.get("name", ""))
        row.addWidget(self.name)
        layout.addLayout(row)

        # Notes
        row = QHBoxLayout()
        row.addWidget(QLabel("Notes:"))
        self.notes = QLineEdit(supplier.get("notes", ""))
        row.addWidget(self.notes)
        layout.addLayout(row)

        # Buttons
        btn_row = QHBoxLayout()
        btn_save = QPushButton("Save")
        btn_cancel = QPushButton("Cancel")

        btn_save.clicked.connect(self._save)
        btn_cancel.clicked.connect(self.reject)

        btn_row.addStretch()
        btn_row.addWidget(btn_save)
        btn_row.addWidget(btn_cancel)

        layout.addLayout(btn_row)

    def _save(self):
        name = self.name.text().strip()
        notes = self.notes.text().strip()

        if not name:
            QMessageBox.warning(self, "Missing Field", "Supplier name is required.")
            return

        # Prevent renaming to an existing supplier
        if name != self.original_name:
            existing = self.mongo.suppliers.find_one({"name": name})
            if existing:
                QMessageBox.warning(self, "Duplicate", f"Supplier '{name}' already exists.")
                return

        try:
            self.mongo.suppliers.update_one(
                {"name": self.original_name},
                {"$set": {"name": name, "notes": notes}}
            )

            self.mongo.log_event(
                "supplier.update",
                performed_by=self.user.username,
                details=f"Updated supplier '{self.original_name}' → '{name}'"
            )

            log_event("info", "Supplier updated",
                      user=self.user.username,
                      old=self.original_name,
                      new=name)

            self.accept()

        except Exception as e:
            log_event("error", "Failed to update supplier",
                      user=self.user.username, supplier=name, error=str(e))
            QMessageBox.critical(self, "Error", f"Failed to update supplier:\n{e}")
