from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QComboBox, QPushButton, QMessageBox, QWidget
)
from PySide6.QtCore import Qt

from ui.components.logger_utils import log_event


class EditItemDialog(QDialog):
    def __init__(self, mongo, user, item, parent=None):
        super().__init__(parent)
        self.mongo = mongo
        self.user = user
        self.item = item

        self.setWindowTitle(f"Edit Item — {item.get('part_number')}")
        self.setMinimumWidth(400)

        layout = QVBoxLayout(self)

        # Part Number
        layout.addWidget(QLabel("Part Number"))
        self.part_number = QLineEdit(item.get("part_number", ""))
        self.part_number.setReadOnly(True)
        self.part_number.setStyleSheet("background-color: #e0e0e0;")

        layout.addWidget(self.part_number)

        # Description
        layout.addWidget(QLabel("Description"))
        self.description = QLineEdit(item.get("description", ""))
        layout.addWidget(self.description)

        # Revision
        layout.addWidget(QLabel("Revision"))
        self.revision = QLineEdit(item.get("revision", "A"))
        layout.addWidget(self.revision)

        # Type
        layout.addWidget(QLabel("Type"))
        self.type = QComboBox()
        self.type.addItems(["Part", "Assembly", "Tool", "Resource"])
        self.type.setCurrentText(item.get("type", "Part"))
        layout.addWidget(self.type)

        # UOM
        layout.addWidget(QLabel("Unit of Measure (UOM)"))
        self.uom = QComboBox()
        uoms = [u["uom"] for u in self.mongo.uom_list.find({})]
        if not uoms:
            uoms = ["EA"]
        self.uom.addItems(uoms)
        self.uom.setCurrentText(item.get("uom", "EA"))
        layout.addWidget(self.uom)

        # Category
        layout.addWidget(QLabel("Category"))
        self.category = QLineEdit(item.get("category", ""))
        layout.addWidget(self.category)

        # Make/Buy
        layout.addWidget(QLabel("Make or Buy"))
        self.make_buy = QComboBox()
        self.make_buy.addItems(["Make", "Buy"])
        self.make_buy.setCurrentText(item.get("make_buy", "Buy"))
        layout.addWidget(self.make_buy)

        # Supplier
        layout.addWidget(QLabel("Supplier"))
        self.supplier = QComboBox()

        suppliers = list(self.mongo.suppliers.find().sort("name", 1))
        if suppliers:
            for s in suppliers:
                self.supplier.addItem(s["name"])
        else:
            self.supplier.addItem("")

        current_supplier = item.get("supplier", "")
        idx = self.supplier.findText(current_supplier)
        if idx >= 0:
            self.supplier.setCurrentIndex(idx)

        layout.addWidget(self.supplier)

        # Status
        layout.addWidget(QLabel("Status"))
        self.status = QComboBox()
        self.status.addItems(["Active", "Disabled", "Discontinued"])
        self.status.setCurrentText(item.get("status", "Active"))
        layout.addWidget(self.status)

        # Store Type
        layout.addWidget(QLabel("Store Type"))
        self.store_type = QComboBox()
        self.store_type.addItems(["General", "Customer"])
        self.store_type.setCurrentText(item.get("store_type", "General"))
        self.store_type.currentIndexChanged.connect(self._toggle_customer_field)
        layout.addWidget(self.store_type)

        # Store (NEW)
        layout.addWidget(QLabel("Store"))
        self.store = QComboBox()

        stores = list(self.mongo.stores.find().sort("name", 1))
        if stores:
            for st in stores:
                self.store.addItem(st["name"], st["_id"])
        else:
            self.store.addItem("")

        # Pre-select store
        current_store = item.get("store_name", "")
        idx = self.store.findText(current_store)
        if idx >= 0:
            self.store.setCurrentIndex(idx)

        layout.addWidget(self.store)

        # Store Location (NEW)
        layout.addWidget(QLabel("Store Location"))
        self.store_location = QComboBox()

        locations = list(self.mongo.store_locations.find({"is_active": True}).sort("location_name", 1))
        if locations:
            for loc in locations:
                self.store_location.addItem(loc["location_name"], loc["_id"])
        else:
            self.store_location.addItem("")

        # Pre-select store location
        current_loc = item.get("store_location_name", "")
        idx = self.store_location.findText(current_loc)
        if idx >= 0:
            self.store_location.setCurrentIndex(idx)

        layout.addWidget(self.store_location)

        # Customer (conditional)
        self.customer_container = QWidget()
        customer_layout = QHBoxLayout(self.customer_container)
        customer_layout.addWidget(QLabel("Customer:"))
        self.customer = QLineEdit(item.get("customer", ""))
        customer_layout.addWidget(self.customer)
        layout.addWidget(self.customer_container)

        # Show/hide based on store type
        self.customer_container.setVisible(self.store_type.currentText() == "Customer")

        # Ownership
        layout.addWidget(QLabel("Ownership"))
        self.ownership = QComboBox()
        self.ownership.addItems(["Company", "Customer"])
        self.ownership.setCurrentText(item.get("ownership", "Company"))
        layout.addWidget(self.ownership)

        # Buttons
        btn_row = QHBoxLayout()
        btn_cancel = QPushButton("Cancel")
        btn_save = QPushButton("Save")
        btn_save.setStyleSheet("background-color: #0275d8; color: white;")

        btn_cancel.clicked.connect(self.reject)
        btn_save.clicked.connect(self._save)

        btn_row.addStretch()
        btn_row.addWidget(btn_cancel)
        btn_row.addWidget(btn_save)
        layout.addLayout(btn_row)

    # Toggle customer field visibility
    def _toggle_customer_field(self):
        is_customer = self.store_type.currentText() == "Customer"
        self.customer_container.setVisible(is_customer)

    def _save(self):
        if not self.part_number.text().strip():
            QMessageBox.warning(self, "Invalid Input", "Part number cannot be empty.")
            return

        make_or_buy = self.make_buy.currentText().lower()
        revision = self.revision.text().strip()

        if make_or_buy == "make" and not revision:
            QMessageBox.warning(
                self,
                "Revision Required",
                "A revision is required for items that are manufactured (Make)."
            )
            return

        # Required: Store + Store Location
        if self.store.currentIndex() < 0 or self.store.currentText().strip() == "":
            QMessageBox.warning(self, "Missing Field", "Store is required.")
            return

        if self.store_location.currentIndex() < 0 or self.store_location.currentText().strip() == "":
            QMessageBox.warning(self, "Missing Field", "Store Location is required.")
            return

        # Build updated document
        self.updated = {
            "part_number": self.part_number.text().strip(),
            "description": self.description.text().strip(),
            "revision": self.revision.text().strip(),
            "type": self.type.currentText(),
            "uom": self.uom.currentText(),
            "category": self.category.text().strip(),
            "make_buy": self.make_buy.currentText(),
            "supplier": self.supplier.currentText().strip(),
            "status": self.status.currentText(),

            # Store Type
            "store_type": self.store_type.currentText(),

            # Store (virtual)
            "store_id": self.store.currentData(),
            "store_name": self.store.currentText(),

            # Store Location (physical)
            "store_location_id": self.store_location.currentData(),
            "store_location_name": self.store_location.currentText(),

            # Customer (conditional)
            "customer": self.customer.text().strip() if self.store_type.currentText() == "Customer" else "",

            # Ownership
            "ownership": self.ownership.currentText()
        }

        # Change tracking
        changes = []
        for key, new_value in self.updated.items():
            old_value = self.item.get(key)
            if old_value != new_value:
                changes.append(f"{key}: '{old_value}' → '{new_value}'")

        # Audit log
        if changes:
            self.mongo.log_event(
                "inventory.edit",
                performed_by=self.user.username,
                details=f"Edited item {self.item.get('part_number')} — Changes: {'; '.join(changes)}"
            )

        log_event(
            "info",
            "Inventory item updated",
            user=self.user.username,
            part_number=self.item.get("part_number"),
            changed_fields=changes
        )

        self.accept()

    def get_updated_values(self):
        return self.updated
