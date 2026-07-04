from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QComboBox, QPushButton, QMessageBox
)
from PySide6.QtCore import QDate

from ui.components.logger_utils import log_event


class StockMovementDialog(QDialog):
    def __init__(self, mongo, user, item, parent=None):
        super().__init__(parent)

        self.mongo = mongo
        self.user = user
        self.item = item

        self.setWindowTitle(f"Move Stock — {item['part_number']}")
        self.setMinimumWidth(450)

        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)

        # Quantity
        row = QHBoxLayout()
        row.addWidget(QLabel("Quantity:"))
        self.qty = QLineEdit()
        row.addWidget(self.qty)
        layout.addLayout(row)

        # FROM Store
        row = QHBoxLayout()
        row.addWidget(QLabel("From Store:"))
        self.from_store = QComboBox()
        for st in self.mongo.stores.find().sort("name", 1):
            self.from_store.addItem(st["name"], st["_id"])
        row.addWidget(self.from_store)
        layout.addLayout(row)

        # FROM Location
        row = QHBoxLayout()
        row.addWidget(QLabel("From Location:"))
        self.from_location = QComboBox()
        for loc in self.mongo.store_locations.find({"is_active": True}).sort("location_name", 1):
            self.from_location.addItem(loc["location_name"], loc["_id"])
        row.addWidget(self.from_location)
        layout.addLayout(row)

        # TO Store
        row = QHBoxLayout()
        row.addWidget(QLabel("To Store:"))
        self.to_store = QComboBox()
        for st in self.mongo.stores.find().sort("name", 1):
            self.to_store.addItem(st["name"], st["_id"])
        row.addWidget(self.to_store)
        layout.addLayout(row)

        # TO Location
        row = QHBoxLayout()
        row.addWidget(QLabel("To Location:"))
        self.to_location = QComboBox()
        for loc in self.mongo.store_locations.find({"is_active": True}).sort("location_name", 1):
            self.to_location.addItem(loc["location_name"], loc["_id"])
        row.addWidget(self.to_location)
        layout.addLayout(row)

        # Buttons
        btn_row = QHBoxLayout()
        self.btn_save = QPushButton("Move Stock")
        self.btn_cancel = QPushButton("Cancel")

        self.btn_save.clicked.connect(self._save)
        self.btn_cancel.clicked.connect(self.reject)

        btn_row.addStretch()
        btn_row.addWidget(self.btn_save)
        btn_row.addWidget(self.btn_cancel)

        layout.addLayout(btn_row)

    def _save(self):
        qty_text = self.qty.text().strip()

        # -----------------------------
        # VALIDATION
        # -----------------------------
        if not qty_text.isdigit():
            QMessageBox.warning(self, "Invalid Quantity", "Quantity must be numeric.")
            return

        qty_to_move = float(qty_text)

        if qty_to_move <= 0:
            QMessageBox.warning(self, "Invalid Quantity", "Quantity must be greater than zero.")
            return

        # -----------------------------
        # FIND BATCHES IN FROM STORE/LOCATION (FIFO)
        # -----------------------------
        from_store_id = self.from_store.currentData()
        from_location_id = self.from_location.currentData()

        batches = list(self.mongo.inventory_batches.find({
            "item_id": self.item["_id"],
            "store_id": from_store_id,
            "store_location_id": from_location_id
        }).sort("received_date", 1))  # FIFO

        if not batches:
            QMessageBox.warning(
                self,
                "No Stock",
                f"No stock found in {self.from_store.currentText()} / {self.from_location.currentText()}."
            )
            return

        # -----------------------------
        # DECREASE QUANTITY FROM SOURCE (FIFO)
        # Track how much is taken from each batch
        # -----------------------------
        remaining = qty_to_move

        for batch in batches:
            if remaining <= 0:
                break

            available = batch.get("quantity", 0)

            if available <= 0:
                batch["_used_qty"] = 0
                continue

            if available > remaining:
                # Reduce batch quantity
                self.mongo.inventory_batches.update_one(
                    {"_id": batch["_id"]},
                    {"$set": {"quantity": available - remaining}}
                )
                batch["_used_qty"] = remaining
                remaining = 0
            else:
                # Empty this batch
                self.mongo.inventory_batches.update_one(
                    {"_id": batch["_id"]},
                    {"$set": {"quantity": 0}}
                )
                batch["_used_qty"] = available
                remaining -= available

        # If still remaining, not enough stock
        if remaining > 0:
            QMessageBox.warning(
                self,
                "Insufficient Stock",
                f"Not enough stock in {self.from_store.currentText()} / {self.from_location.currentText()}."
            )
            return

        # -----------------------------
        # ADD QUANTITY TO DESTINATION
        # Create one MOVE batch per source batch used
        # Copy expiry + cost
        # -----------------------------
        to_store_id = self.to_store.currentData()
        to_location_id = self.to_location.currentData()

        for batch in batches:
            used_qty = batch.get("_used_qty", 0)
            if used_qty <= 0:
                continue

            new_batch = {
                "item_id": self.item["_id"],
                "part_number": self.item["part_number"],
                "description": self.item["description"],

                "grn_number": f"MOVE-{batch.get('grn_number', '')}",
                "batch_number": f"MOVE-{batch.get('batch_number', '')}",  # traceable
                "quantity": used_qty,

                # ⭐ Copy cost + expiry from source batch
                "unit_cost": batch.get("unit_cost", 0),
                "expiry_date": batch.get("expiry_date", ""),

                "received_date": QDate.currentDate().toString("yyyy-MM-dd"),

                "store_id": to_store_id,
                "store_name": self.to_store.currentText(),

                "store_location_id": to_location_id,
                "store_location_name": self.to_location.currentText(),

                # Traceability
                "source_batch_id": batch["_id"],
                "owner_customer_id": None
            }

            self.mongo.inventory_batches.insert_one(new_batch)

        # -----------------------------
        # MOVEMENT HISTORY
        # -----------------------------
        movement_doc = {
            "item_id": self.item["_id"],
            "part_number": self.item["part_number"],
            "description": self.item["description"],

            "quantity": qty_to_move,
            "movement_date": QDate.currentDate().toString("yyyy-MM-dd"),

            "from_store_id": from_store_id,
            "from_store_name": self.from_store.currentText(),
            "from_location_id": from_location_id,
            "from_location_name": self.from_location.currentText(),

            "to_store_id": to_store_id,
            "to_store_name": self.to_store.currentText(),
            "to_location_id": to_location_id,
            "to_location_name": self.to_location.currentText(),

            "performed_by": self.user.username
        }

        self.mongo.stock_movements.insert_one(movement_doc)

        # -----------------------------
        # AUDIT LOG
        # -----------------------------
        self.mongo.log_event(
            "inventory.move",
            performed_by=self.user.username,
            details=f"Moved {qty_to_move} of {self.item['part_number']} "
                    f"from {self.from_store.currentText()} / {self.from_location.currentText()} "
                    f"to {self.to_store.currentText()} / {self.to_location.currentText()}"
        )

        log_event(
            "info",
            "Stock moved",
            user=self.user.username,
            part_number=self.item["part_number"],
            qty=qty_to_move
        )

        self.accept()


