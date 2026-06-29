from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QComboBox, QPushButton, QMessageBox, QWidget
)
from PySide6.QtCore import Qt

from ui.components.logger_utils import log_event


class AddItemDialog(QDialog):
    def __init__(self, mongo, user, parent=None):
        super().__init__(parent)

        self.mongo = mongo
        self.user = user

        self.setWindowTitle("Add Inventory Item")
        self.setMinimumWidth(400)

        self._build_ui()

    # ---------------------------------------------------------
    # Build UI
    # ---------------------------------------------------------
    def _build_ui(self):
        layout = QVBoxLayout(self)

        # Part Number
        row = QHBoxLayout()
        row.addWidget(QLabel("Part Number:"))
        self.part_number = QLineEdit()
        row.addWidget(self.part_number)
        layout.addLayout(row)

        # Description
        row = QHBoxLayout()
        row.addWidget(QLabel("Description:"))
        self.description = QLineEdit()
        row.addWidget(self.description)
        layout.addLayout(row)

        # Revision
        layout.addWidget(QLabel("Revision"))
        self.revision = QLineEdit()
        self.revision.setText("A")
        layout.addWidget(self.revision)

        # Type
        row = QHBoxLayout()
        row.addWidget(QLabel("Type:"))
        self.type_box = QComboBox()
        self.type_box.addItems(["Part", "Assembly", "Tool", "Resource"])
        row.addWidget(self.type_box)
        layout.addLayout(row)

        # UOM
        layout.addWidget(QLabel("Unit of Measure (UOM)"))
        self.uom = QComboBox()
        uoms = [u["uom"] for u in self.mongo.uom_list.find({})]
        if not uoms:
            uoms = ["EA"]  # fallback

        self.uom.addItems(uoms)
        self.uom.setCurrentText("EA")
        layout.addWidget(self.uom)

        # Category
        row = QHBoxLayout()
        row.addWidget(QLabel("Category:"))
        self.category = QLineEdit()
        row.addWidget(self.category)
        layout.addLayout(row)

        # Make/Buy
        row = QHBoxLayout()
        row.addWidget(QLabel("Make/Buy:"))
        self.makebuy = QComboBox()
        self.makebuy.addItems(["Make", "Buy"])
        row.addWidget(self.makebuy)
        layout.addLayout(row)

        # Supplier
        row = QHBoxLayout()
        row.addWidget(QLabel("Supplier:"))

        self.supplier = QComboBox()
        suppliers = list(self.mongo.suppliers.find().sort("name", 1))

        if suppliers:
            for s in suppliers:
                self.supplier.addItem(s["name"])
        else:
            self.supplier.addItem("")

        row.addWidget(self.supplier)
        layout.addLayout(row)

        # Status
        row = QHBoxLayout()
        row.addWidget(QLabel("Status:"))
        self.status_box = QComboBox()
        self.status_box.addItems(["Active", "Disabled", "Discontinued"])
        row.addWidget(self.status_box)
        layout.addLayout(row)

        # Store Type
        row = QHBoxLayout()
        row.addWidget(QLabel("Store Type:"))
        self.store_type = QComboBox()
        self.store_type.addItems(["General", "Customer"])
        self.store_type.currentIndexChanged.connect(self._toggle_customer_field)
        row.addWidget(self.store_type)
        layout.addLayout(row)

        # Store (NEW)
        row = QHBoxLayout()
        row.addWidget(QLabel("Store:"))
        self.store = QComboBox()

        stores = list(self.mongo.stores.find().sort("name", 1))
        if stores:
            for st in stores:
                self.store.addItem(st["name"], st["_id"])
        else:
            self.store.addItem("")

        row.addWidget(self.store)
        layout.addLayout(row)

        # Store Location (NEW)
        row = QHBoxLayout()
        row.addWidget(QLabel("Store Location:"))
        self.store_location = QComboBox()

        locations = list(self.mongo.store_locations.find({"is_active": True}).sort("location_name", 1))
        if locations:
            for loc in locations:
                self.store_location.addItem(loc["location_name"], loc["_id"])
        else:
            self.store_location.addItem("")

        row.addWidget(self.store_location)
        layout.addLayout(row)

        # Customer (only visible when Store Type = Customer)
        self.customer_container = QWidget()
        customer_layout = QHBoxLayout(self.customer_container)

        customer_layout.addWidget(QLabel("Customer:"))
        self.customer = QLineEdit()
        customer_layout.addWidget(self.customer)

        layout.addWidget(self.customer_container)
        self.customer_container.setVisible(False)

        # Ownership
        row = QHBoxLayout()
        row.addWidget(QLabel("Ownership:"))
        self.ownership = QComboBox()
        self.ownership.addItems(["Company", "Customer"])
        row.addWidget(self.ownership)
        layout.addLayout(row)

        # Buttons
        btn_row = QHBoxLayout()
        self.btn_save = QPushButton("Create Item")
        self.btn_cancel = QPushButton("Cancel")

        self.btn_save.clicked.connect(self._save)
        self.btn_cancel.clicked.connect(self.reject)

        btn_row.addStretch()
        btn_row.addWidget(self.btn_save)
        btn_row.addWidget(self.btn_cancel)

        layout.addLayout(btn_row)

    # ---------------------------------------------------------
    # Show/hide customer field
    # ---------------------------------------------------------
    def _toggle_customer_field(self):
        is_customer = self.store_type.currentText() == "Customer"
        self.customer_container.setVisible(is_customer)

    # ---------------------------------------------------------
    # Save item
    # ---------------------------------------------------------
    def _save(self):
        part_number = self.part_number.text().strip()
        description = self.description.text().strip()
        revision = self.revision.text().strip()

        make_or_buy = self.makebuy.currentText().lower()

        if make_or_buy == "make" and not revision:
            QMessageBox.warning(
                self,
                "Revision Required",
                "A revision is required for items that are manufactured (Make)."
            )
            return

        if not part_number:
            QMessageBox.warning(self, "Missing Field", "Part Number is required.")
            return

        if not description:
            QMessageBox.warning(self, "Missing Field", "Description is required.")
            return

        # Required: Store + Store Location
        if self.store.currentIndex() < 0 or self.store.currentText().strip() == "":
            QMessageBox.warning(self, "Missing Field", "Store is required.")
            return

        if self.store_location.currentIndex() < 0 or self.store_location.currentText().strip() == "":
            QMessageBox.warning(self, "Missing Field", "Store Location is required.")
            return

        # Check for duplicate part number
        existing = self.mongo.inventory.find_one({"part_number": part_number})
        if existing:
            QMessageBox.warning(self, "Duplicate", "An item with this Part Number already exists.")
            return

        doc = {
            "part_number": part_number,
            "description": description,
            "revision": revision,
            "type": self.type_box.currentText(),
            "uom": self.uom.currentText(),
            "category": self.category.text().strip(),
            "make_buy": self.makebuy.currentText(),
            "supplier": self.supplier.currentText().strip(),
            "status": self.status_box.currentText(),

            # Store Type (policy)
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

        try:
            self.mongo.inventory.insert_one(doc)

            # Audit log
            self.mongo.log_event(
                "inventory.create",
                performed_by=self.user.username,
                details=f"Created inventory item {part_number} (Rev {revision}, UOM {doc['uom']})"
            )

            # Debug log
            log_event(
                "info",
                "Inventory item created",
                user=self.user.username,
                part_number=part_number,
                revision=revision,
                uom=doc["uom"]
            )

            self.accept()

        except Exception as e:
            log_event("error", "Failed to create inventory item",
                      user=self.user.username, error=str(e))
            QMessageBox.critical(self, "Error", f"Failed to create item:\n{e}")
