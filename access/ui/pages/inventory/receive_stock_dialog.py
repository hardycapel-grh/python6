from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QComboBox, QPushButton, QDateEdit, QMessageBox, QWidget
)
from PySide6.QtCore import Qt, QDate

from ui.components.logger_utils import log_event


class ReceiveStockDialog(QDialog):
    def __init__(self, mongo, user, item, parent=None):
        """
        item = the inventory_item document
        """
        from PySide6.QtWidgets import QComboBox

        super().__init__(parent)

        self.mongo = mongo
        self.user = user
        self.item = item

        self.setWindowTitle(f"Receive Stock — {item['part_number']}")
        self.setMinimumWidth(450)

        self._build_ui()

    # ---------------------------------------------------------
    # Build UI
    # ---------------------------------------------------------
    def _build_ui(self):
        layout = QVBoxLayout(self)

        # GRN Number
        row = QHBoxLayout()
        row.addWidget(QLabel("GRN Number:"))
        self.grn = QLineEdit()
        row.addWidget(self.grn)
        layout.addLayout(row)

        # Batch / Lot Number
        row = QHBoxLayout()
        row.addWidget(QLabel("Batch / Lot Number:"))
        self.batch = QLineEdit()
        row.addWidget(self.batch)
        layout.addLayout(row)

        # Quantity
        row = QHBoxLayout()
        row.addWidget(QLabel("Quantity:"))
        self.quantity = QLineEdit()
        row.addWidget(self.quantity)
        layout.addLayout(row)

        # Unit Cost
        row = QHBoxLayout()
        row.addWidget(QLabel("Unit Cost:"))
        self.unit_cost = QLineEdit()
        row.addWidget(self.unit_cost)
        layout.addLayout(row)

        # Expiry Date
        row = QHBoxLayout()
        row.addWidget(QLabel("Expiry Date:"))
        self.expiry = QDateEdit()
        self.expiry.setCalendarPopup(True)
        self.expiry.setDate(QDate.currentDate())
        row.addWidget(self.expiry)
        layout.addLayout(row)

        # Store
        row = QHBoxLayout()
        row.addWidget(QLabel("Store:"))
        self.store_combo = QComboBox()
        row.addWidget(self.store_combo)
        layout.addLayout(row)

        self._load_stores()



        # Buttons
        btn_row = QHBoxLayout()
        self.btn_save = QPushButton("Receive Stock")
        self.btn_cancel = QPushButton("Cancel")

        self.btn_save.clicked.connect(self._save)
        self.btn_cancel.clicked.connect(self.reject)

        btn_row.addStretch()
        btn_row.addWidget(self.btn_save)
        btn_row.addWidget(self.btn_cancel)

        layout.addLayout(btn_row)

        


    # ---------------------------------------------------------
    # Save batch
    # ---------------------------------------------------------
    def _save(self):
        grn = self.grn.text().strip()
        batch = self.batch.text().strip()
        qty = self.quantity.text().strip()
        cost = self.unit_cost.text().strip()

        if not grn:
            QMessageBox.warning(self, "Missing Field", "GRN Number is required.")
            return

        if not batch:
            QMessageBox.warning(self, "Missing Field", "Batch/Lot Number is required.")
            return

        if not qty.isdigit():
            QMessageBox.warning(self, "Invalid Quantity", "Quantity must be a number.")
            return

        try:
            qty = float(qty)
        except:
            QMessageBox.warning(self, "Invalid Quantity", "Quantity must be numeric.")
            return

        try:
            cost = float(cost)
        except:
            QMessageBox.warning(self, "Invalid Cost", "Unit cost must be numeric.")
            return

        doc = {
            "item_id": self.item["_id"],
            "part_number": self.item["part_number"],
            "description": self.item["description"],

            "grn_number": grn,
            "batch_number": batch,
            "quantity": qty,
            "unit_cost": cost,
            "received_date": QDate.currentDate().toString("yyyy-MM-dd"),
            "expiry_date": self.expiry.date().toString("yyyy-MM-dd"),

            "store_id": self.store_combo.currentData(),
            "owner_customer_id": None
        }


        try:
            self.mongo.inventory_batches.insert_one(doc)

            # Audit log
            self.mongo.log_event(
                "inventory.receive_stock",
                performed_by=self.user.username,
                details=f"Received {qty} units of {self.item['part_number']} (Batch {batch})"
            )

            log_event("info", "Stock received",
                      user=self.user.username,
                      part_number=self.item["part_number"],
                      batch=batch)

            self.accept()

        except Exception as e:
            log_event("error", "Failed to receive stock",
                      user=self.user.username, error=str(e))
            QMessageBox.critical(self, "Error", f"Failed to receive stock:\n{e}")

    def _load_stores(self):
        stores = list(self.mongo.stores.find({"status": "Active"}).sort("name", 1))
        self.stores = stores

        self.store_combo.clear()
        for store in stores:
            self.store_combo.addItem(store["name"], store["_id"])
