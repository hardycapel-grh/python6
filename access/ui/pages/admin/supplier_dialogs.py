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
        self.setMinimumWidth(400)

        layout = QVBoxLayout(self)

        # Name
        row = QHBoxLayout()
        row.addWidget(QLabel("Supplier Name:"))
        self.name = QLineEdit()
        row.addWidget(self.name)
        layout.addLayout(row)

        # Contact Name
        row = QHBoxLayout()
        row.addWidget(QLabel("Contact Name:"))
        self.contact_name = QLineEdit()
        row.addWidget(self.contact_name)
        layout.addLayout(row)

        # Email
        row = QHBoxLayout()
        row.addWidget(QLabel("Email:"))
        self.email = QLineEdit()
        row.addWidget(self.email)
        layout.addLayout(row)

        # Phone
        row = QHBoxLayout()
        row.addWidget(QLabel("Phone:"))
        self.phone = QLineEdit()
        row.addWidget(self.phone)
        layout.addLayout(row)

        # Address Line 1
        row = QHBoxLayout()
        row.addWidget(QLabel("Address Line 1:"))
        self.address1 = QLineEdit()
        row.addWidget(self.address1)
        layout.addLayout(row)

        # Address Line 2
        row = QHBoxLayout()
        row.addWidget(QLabel("Address Line 2:"))
        self.address2 = QLineEdit()
        row.addWidget(self.address2)
        layout.addLayout(row)

        # City
        row = QHBoxLayout()
        row.addWidget(QLabel("City:"))
        self.city = QLineEdit()
        row.addWidget(self.city)
        layout.addLayout(row)

        # Postcode
        row = QHBoxLayout()
        row.addWidget(QLabel("Postcode:"))
        self.postcode = QLineEdit()
        row.addWidget(self.postcode)
        layout.addLayout(row)

        # Country
        row = QHBoxLayout()
        row.addWidget(QLabel("Country:"))
        self.country = QLineEdit()
        row.addWidget(self.country)
        layout.addLayout(row)

        # Notes
        row = QHBoxLayout()
        row.addWidget(QLabel("Comments:"))
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

        if not name:
            QMessageBox.warning(self, "Missing Field", "Supplier name is required.")
            return

        if self.mongo.suppliers.find_one({"name": name}):
            QMessageBox.warning(self, "Duplicate", f"Supplier '{name}' already exists.")
            return

        doc = {
            "name": name,
            "contact_name": self.contact_name.text().strip(),
            "email": self.email.text().strip(),
            "phone": self.phone.text().strip(),
            "notes": self.notes.text().strip(),
            "address1": self.address1.text().strip(),
            "address2": self.address2.text().strip(),
            "city": self.city.text().strip(),
            "postcode": self.postcode.text().strip(),
            "country": self.country.text().strip()
        }


        self.mongo.suppliers.insert_one(doc)

        self.mongo.log_event(
            "supplier.create",
            performed_by=self.user.username,
            details=f"Created supplier '{name}'"
        )

        log_event("info", "Supplier created", user=self.user.username, supplier=name)

        self.accept()


class EditSupplierDialog(QDialog):
    def __init__(self, mongo, user, name, parent=None):
        super().__init__(parent)

        self.mongo = mongo
        self.user = user
        self.original_name = name

        supplier = self.mongo.suppliers.find_one({"name": name}) or {}

        self.setWindowTitle(f"Edit Supplier: {name}")
        self.setMinimumWidth(400)

        layout = QVBoxLayout(self)

        # Name
        row = QHBoxLayout()
        row.addWidget(QLabel("Supplier Name:"))
        self.name = QLineEdit(supplier.get("name", ""))
        row.addWidget(self.name)
        layout.addLayout(row)

        # Contact Name
        row = QHBoxLayout()
        row.addWidget(QLabel("Contact Name:"))
        self.contact_name = QLineEdit(supplier.get("contact_name", ""))
        row.addWidget(self.contact_name)
        layout.addLayout(row)

        # Email
        row = QHBoxLayout()
        row.addWidget(QLabel("Email:"))
        self.email = QLineEdit(supplier.get("email", ""))
        row.addWidget(self.email)
        layout.addLayout(row)

        # Phone
        row = QHBoxLayout()
        row.addWidget(QLabel("Phone:"))
        self.phone = QLineEdit(supplier.get("phone", ""))
        row.addWidget(self.phone)
        layout.addLayout(row)

        # Notes
        row = QHBoxLayout()
        row.addWidget(QLabel("Comments:"))
        self.notes = QLineEdit(supplier.get("notes", ""))
        row.addWidget(self.notes)
        layout.addLayout(row)

        # Address Line 1
        row = QHBoxLayout()
        row.addWidget(QLabel("Address Line 1:"))
        self.address1 = QLineEdit(supplier.get("address1", ""))
        row.addWidget(self.address1)
        layout.addLayout(row)

        # Address Line 2
        row = QHBoxLayout()
        row.addWidget(QLabel("Address Line 2:"))
        self.address2 = QLineEdit(supplier.get("address2", ""))
        row.addWidget(self.address2)
        layout.addLayout(row)

        # City
        row = QHBoxLayout()
        row.addWidget(QLabel("City:"))
        self.city = QLineEdit(supplier.get("city", ""))
        row.addWidget(self.city)
        layout.addLayout(row)

        # Postcode
        row = QHBoxLayout()
        row.addWidget(QLabel("Postcode:"))
        self.postcode = QLineEdit(supplier.get("postcode", ""))
        row.addWidget(self.postcode)
        layout.addLayout(row)

        # Country
        row = QHBoxLayout()
        row.addWidget(QLabel("Country:"))
        self.country = QLineEdit(supplier.get("country", ""))
        row.addWidget(self.country)
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
                {"$set": {
                    "name": name,
                    "contact_name": self.contact_name.text().strip(),
                    "email": self.email.text().strip(),
                    "phone": self.phone.text().strip(),
                    "notes": self.notes.text().strip(),
                    "address1": self.address1.text().strip(),
                    "address2": self.address2.text().strip(),
                    "city": self.city.text().strip(),
                    "postcode": self.postcode.text().strip(),
                    "country": self.country.text().strip()

                }}
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

class ViewSupplierDialog(QDialog):
    def __init__(self, mongo, name, parent=None):
        super().__init__(parent)

        self.mongo = mongo
        supplier = self.mongo.suppliers.find_one({"name": name}) or {}

        self.setWindowTitle(f"Supplier Details: {name}")
        self.setMinimumWidth(450)

        layout = QVBoxLayout(self)

        def add_row(label, value):
            row = QHBoxLayout()
            row.addWidget(QLabel(f"{label}:"))
            field = QLineEdit(value if value else "")
            field.setReadOnly(True)
            row.addWidget(field)
            layout.addLayout(row)

        add_row("Name", supplier.get("name"))
        add_row("Contact Name", supplier.get("contact_name"))
        add_row("Email", supplier.get("email"))
        add_row("Phone", supplier.get("phone"))
        add_row("Address Line 1", supplier.get("address1"))
        add_row("Address Line 2", supplier.get("address2"))
        add_row("City", supplier.get("city"))
        add_row("Postcode", supplier.get("postcode"))
        add_row("Country", supplier.get("country"))
        add_row("Comments", supplier.get("notes"))

        # Close button
        btn_row = QHBoxLayout()
        btn_close = QPushButton("Close")
        btn_close.clicked.connect(self.accept)
        btn_row.addStretch()
        btn_row.addWidget(btn_close)
        layout.addLayout(btn_row)
