"""
Dialog for editing an existing Sales Order.

This dialog mirrors AddItemDialog but loads an existing SO,
allows editing of fields, editing/removing items, and logs changes.
"""

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QFormLayout, QLineEdit, QComboBox,
    QDialogButtonBox, QListWidget, QListWidgetItem, QPushButton,
    QHBoxLayout, QLabel, QDateEdit, QInputDialog
)
from PySide6.QtCore import Qt, QDate, QTimer
from PySide6.QtWidgets import QDoubleSpinBox, QCheckBox

from ui.components.logger_utils import log_event
from ui.pages.sales.add_item_dialog import AddItemDialog

from ui.pages.sales.add_item_dialog import AddItemDialog



ALLOWED_TRANSITIONS = {
    "new":        {"new","released", "held", "cancelled"},
    "released":   {"released", "in-work", "held", "cancelled"},
    "in-work":    {"in-work","finished", "held", "cancelled"},
    # "held":       {"new", "released", "in-work", "cancelled"},
    "finished":   set(),
    "cancelled":  set()
}


class EditSalesOrderDialog(QDialog):
    def __init__(self, mongo, user, sales_order, parent=None):
        """
        sales_order: dict from MongoDB representing the SO to edit
        """
        super().__init__(parent)

        self.mongo = mongo
        self.user = user
        self.sales_order = sales_order

        self.setWindowTitle(f"Edit Sales Order {sales_order['so_number']}")
        self.setMinimumWidth(450)

        # -------------------------
        # Main layout
        # -------------------------
        main_layout = QVBoxLayout(self)

        form = QFormLayout()

        # SO Number (read-only)
        self.so_number_edit = QLineEdit()
        self.so_number_edit.setText(str(sales_order["so_number"]))
        self.so_number_edit.setReadOnly(True)
        self.so_number_edit.setEnabled(False)
        form.addRow("SO Number:", self.so_number_edit)

        # Customer dropdown
        customers = [doc.get("name", "") for doc in self.mongo.suppliers.find({})]
        self.customer_combo = QComboBox()
        self.customer_combo.addItems(customers)
        self.customer_combo.setCurrentText(sales_order["customer"])
        self.customer_combo.setEnabled(False)
        form.addRow("Customer:", self.customer_combo)

        # Req Date
        self.req_date_edit = QDateEdit()
        self.req_date_edit.setCalendarPopup(True)
        self.req_date_edit.setDate(QDate.fromString(sales_order["req_date"], "yyyy-MM-dd"))
        form.addRow("Req Date:", self.req_date_edit)

        # Status dropdown
        self.status_combo = QComboBox()
        self.status_combo.addItems(["new", "released", "in-work", "finished", "cancelled"])
        self.status_combo.setCurrentText(sales_order["status"])
        form.addRow("Status:", self.status_combo)

        # Type dropdown
        self.type_combo = QComboBox()
        self.type_combo.addItems(["enquiry", "firm"])
        self.type_combo.setCurrentText(sales_order["type"])
        form.addRow("Type:", self.type_combo)

        

        self.held_checkbox = QCheckBox("Held")
        self.held_checkbox.setChecked(self.sales_order.get("held", False))
        form.addRow("Held:", self.held_checkbox)


        main_layout.addLayout(form)

        # -------------------------
        # Items list
        # -------------------------
        items_layout = QVBoxLayout()

        items_layout.addWidget(QLabel("Order Items:"))
        self.items_list = QListWidget()
        items_layout.addWidget(self.items_list)

        # Load existing items
        for item in sales_order["items"]:
            if isinstance(item, str):
                # Convert legacy format: "PN123" → {"part_number": "PN123", ...}
                item = {
                    "part_number": item,
                    "description": "",
                    "qty": 1,
                    "uom": "ea"
                }

            display = (
                f"{item.get('part_number', '')} - "
                f"{item.get('description', '')} "
                f"(qty: {item.get('qty', '')} {item.get('uom', '')})"
            )

            list_item = QListWidgetItem(display)
            list_item.setData(Qt.UserRole, item)
            self.items_list.addItem(list_item)



        # Buttons for item editing
        btn_layout = QHBoxLayout()
        self.add_item_btn = QPushButton("Add Item")
        self.edit_qty_btn = QPushButton("Edit Qty")
        self.remove_item_btn = QPushButton("Remove Item")

        btn_layout.addWidget(self.add_item_btn)
        btn_layout.addWidget(self.edit_qty_btn)
        btn_layout.addWidget(self.remove_item_btn)

        items_layout.addLayout(btn_layout)
        main_layout.addLayout(items_layout)

        # -------------------------
        # Dialog buttons
        # -------------------------
        buttons = QDialogButtonBox(
            QDialogButtonBox.Save | QDialogButtonBox.Cancel,
            Qt.Horizontal,
            self
        )
        main_layout.addWidget(buttons)

        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.close)

        if sales_order.get("held", False):
            self._set_read_only_mode()


        # -------------------------
        # Connections
        # -------------------------
        self.edit_qty_btn.clicked.connect(self._edit_item_qty)
        self.remove_item_btn.clicked.connect(self._remove_item)
        self.add_item_btn.clicked.connect(self._add_item)

    # ---------------------------------------------------------
    # Item quantity editing
    # ---------------------------------------------------------
    def _add_item(self):
    # Open the same inventory picker used in AddItemDialog

        dlg = AddItemDialog(self.mongo, self.user, self)
        if dlg.exec():
            new_item_data = dlg.get_data()["items"]

            if not new_item_data:
                return

            # Add each item returned by the AddItemDialog
            for item in new_item_data:
                display = (
                    f"{item['part_number']} - {item['description']} "
                    f"(qty: {item['qty']} {item['uom']})"
                )

                list_item = QListWidgetItem(display)
                list_item.setData(Qt.UserRole, item)
                self.items_list.addItem(list_item)

                # Audit log
                self.mongo.log_event(
                    "sales_order.item_add",
                    performed_by=getattr(self.user, "username", None),
                    details=(
                        f"Added item {item['part_number']} qty {item['qty']} {item['uom']} "
                        f"to Sales Order {self.so_number_edit.text()}"
                    )
                )

                # Debug log
                log_event(
                    "info",
                    "Sales order item added",
                    user=getattr(self.user, "username", None),
                    so_number=self.so_number_edit.text(),
                    part_number=item["part_number"],
                    qty=item["qty"],
                    uom=item["uom"]
                )

    def _edit_item_qty(self):
        item = self.items_list.currentItem()
        if not item:
            return

        data = item.data(Qt.UserRole)
        old_qty = data["qty"]

        dlg = QInputDialog(self)
        dlg.setInputMode(QInputDialog.DoubleInput)
        dlg.setDoubleDecimals(3)
        dlg.setDoubleMinimum(0.0)
        dlg.setDoubleMaximum(999999.0)
        dlg.setDoubleValue(float(old_qty))
        dlg.setLabelText(f"Edit quantity for {data['part_number']}")

        if dlg.exec():
            new_qty = dlg.doubleValue()

            # Audit log
            self.mongo.log_event(
                "sales_order.item_qty_update",
                performed_by=getattr(self.user, "username", None),
                details=(
                    f"Updated qty for {data['part_number']} "
                    f"from {old_qty} to {new_qty} "
                    f"in Sales Order {self.so_number_edit.text()}"
                )
            )

           # Debug log
            log_event(
                "info",
                "Sales order item qty updated",
                user=getattr(self.user, "username", None),
                so_number=self.so_number_edit.text(),
                part_number=data["part_number"],
                old_qty=old_qty,
                new_qty=new_qty
            )

            # Update UI + stored data
            data["qty"] = new_qty
            item.setData(Qt.UserRole, data)
            item.setText(
                f"{data['part_number']} - {data['description']} "
                f"(qty: {new_qty} {data['uom']})"
            )

    # ---------------------------------------------------------
    # Remove item
    # ---------------------------------------------------------
    def _remove_item(self):
        item = self.items_list.currentItem()
        if not item:
            return

        data = item.data(Qt.UserRole)

        # Audit log
        self.mongo.log_event(
            "sales_order.item_remove",
            performed_by=getattr(self.user, "username", None),
            details=(
                f"Removed item {data['part_number']} qty {data['qty']} {data['uom']} "
                f"from Sales Order {self.so_number_edit.text()}"
            )
        )

        # Debug log
        log_event(
            "info",
            "Sales order item removed",
            user=getattr(self.user, "username", None),
            so_number=self.so_number_edit.text(),
            part_number=data["part_number"],
            qty=data["qty"],
            uom=data["uom"]
        )

        self.items_list.takeItem(self.items_list.row(item))

    def _set_read_only_mode(self):
        # Disable all editable widgets
        self.req_date_edit.setEnabled(False)
        self.status_combo.setEnabled(False)
        self.type_combo.setEnabled(False)
        self.items_list.setEnabled(False)
        self.add_item_btn.setEnabled(False)
        self.edit_qty_btn.setEnabled(False)
        self.remove_item_btn.setEnabled(False)

        # Optional: visually indicate read-only mode
        self.setWindowTitle(f"Sales Order {self.sales_order['so_number']} (Held - Read Only)")


    # ---------------------------------------------------------
    # Gather updated data
    # ---------------------------------------------------------
    def get_data(self):
        return {
            "so_number": self.so_number_edit.text().strip(),
            "customer": self.customer_combo.currentText(),
            "req_date": self.req_date_edit.date().toString("yyyy-MM-dd"),
            "status": self.status_combo.currentText(),
            "type": self.type_combo.currentText(),
            "held": self.held_checkbox.isChecked(),
            "items": [
                self.items_list.item(i).data(Qt.UserRole)
                for i in range(self.items_list.count())
            ],
            "updated_by": getattr(self.user, "username", None)
        }

    def accept(self):

    # Prevent saving if held
        if self.sales_order.get("held", False):
            from PySide6.QtWidgets import QMessageBox
            QMessageBox.warning(
                self,
                "Held Sales Order",
                "This Sales Order is held and cannot be edited until un‑held."
            )
            return

        updated_data = self.get_data()

        old_status = self.sales_order.get("status", "").lower()
        new_status = updated_data.get("status", "").lower()

        # ⭐ Workflow rule enforcement
        if new_status not in ALLOWED_TRANSITIONS.get(old_status, set()):
            from PySide6.QtWidgets import QMessageBox
            QMessageBox.warning(
                self,
                "Invalid Status Change",
                f"You cannot change status from '{old_status}' to '{new_status}'."
            )
            return  # stop the save

        # ⭐ If valid, update DB
        try:
            self.mongo.sales_orders.update_one(
                {"so_number": self.sales_order["so_number"]},
                {"$set": updated_data}
            )
        except Exception as e:
            from PySide6.QtWidgets import QMessageBox
            QMessageBox.critical(self, "Error", str(e))
            return

        super().accept()
