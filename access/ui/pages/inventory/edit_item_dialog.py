from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QComboBox, QPushButton, QMessageBox
)
from PySide6.QtCore import Qt

from ui.components.logger_utils import log_event   # ⭐ Needed for debug logging


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
            uoms = ["EA"]  # fallback

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

        # Load suppliers from DB
        suppliers = list(self.mongo.suppliers.find().sort("name", 1))

        if suppliers:
            for s in suppliers:
                self.supplier.addItem(s["name"])
        else:
            self.supplier.addItem("")

        # Pre-select current supplier
        current_supplier = item.get("supplier", "")
        index = self.supplier.findText(current_supplier)
        if index >= 0:
            self.supplier.setCurrentIndex(index)

        layout.addWidget(self.supplier)


        # Status
        layout.addWidget(QLabel("Status"))
        self.status = QComboBox()
        self.status.addItems(["Active", "Disabled", "Discontinued"])
        self.status.setCurrentText(item.get("status", "Active"))
        layout.addWidget(self.status)

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

    def _save(self):
        # Basic validation
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
            return None


        # New values
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
        }

        # ⭐ FIELD‑LEVEL CHANGE TRACKING
        changes = []
        for key, new_value in self.updated.items():
            old_value = self.item.get(key)
            if old_value != new_value:
                changes.append(f"{key}: '{old_value}' → '{new_value}'")

        # ⭐ AUDIT LOGGING
        if changes:
            self.mongo.log_event(
                "inventory.edit",
                performed_by=self.user.username,
                details=(
                    f"Edited item {self.item.get('part_number')} "
                    f"(Rev {self.item.get('revision', '')} → {self.updated.get('revision', '')}). "
                    f"Changes: {'; '.join(changes)}"
                )
            )

        # ⭐ DEBUG LOGGING
        log_event(
            "info",
            "Inventory item updated",
            user=self.user.username,
            part_number=self.item.get("part_number"),
            old_revision=self.item.get("revision", ""),
            new_revision=self.updated.get("revision", ""),
            changed_fields=changes
        )

        self.accept()

    def get_updated_values(self):
        return self.updated
