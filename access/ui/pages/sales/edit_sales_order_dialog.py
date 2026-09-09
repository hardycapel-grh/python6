"""
Dialog for editing an existing Sales Order.

This dialog mirrors AddItemDialog but loads an existing SO,
allows editing of fields, editing/removing items, and logs changes.
"""

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QFormLayout, QLineEdit, QComboBox,
    QDialogButtonBox, QListWidget, QListWidgetItem, QAbstractItemView, QPushButton,
    QHBoxLayout, QLabel, QDateEdit, QInputDialog, QMessageBox
)
from PySide6.QtCore import Qt, QDate
from PySide6.QtWidgets import QDoubleSpinBox, QCheckBox

from ui.components.logger_utils import log_event
from ui.pages.sales.add_item_dialog import AddItemDialog

from backend.sales_order_costing import calculate_sales_order_cost
from backend.invoice_generator import generate_invoice
from backend.dispatch_generator import generate_dispatch_note


ALLOWED_TRANSITIONS = {
    "new":        {"new", "released"},
    "released":   {"released", "in-work"},
    "in-work":    {"in-work", "finished"},
    "finished":   set(),
    "cancelled":  set()
}


class BomMultiSelectDialog(QDialog):
    def __init__(self, items, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Select BOM Items")

        layout = QVBoxLayout(self)

        self.list = QListWidget()
        self.list.setSelectionMode(QAbstractItemView.MultiSelection)

        for item in items:
            lw_item = QListWidgetItem(
                f"{item['part_number']} - {item['description']} (qty: {item['qty']} {item['uom']})"
            )
            lw_item.setFlags(lw_item.flags() | Qt.ItemIsUserCheckable)
            lw_item.setCheckState(Qt.Unchecked)
            self.list.addItem(lw_item)

        layout.addWidget(self.list)

        btns = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        btns.accepted.connect(self.accept)
        btns.rejected.connect(self.reject)
        layout.addWidget(btns)

        self.items = items

    def get_selected_items(self):
        selected = []
        for i in range(self.list.count()):
            lw_item = self.list.item(i)
            if lw_item.checkState() == Qt.Checked:
                selected.append(self.items[i])
        return selected


class EditSalesOrderDialog(QDialog):
    def __init__(self, mongo, user, sales_order, parent=None):
        super().__init__(parent)

        self.mongo = mongo
        self.user = user
        self.sales_order = sales_order

        self.setWindowTitle(f"Edit Sales Order {sales_order['so_number']}")
        self.setMinimumWidth(450)

        main_layout = QVBoxLayout(self)
        form = QFormLayout()

        # SO Number (read-only)
        self.so_number_edit = QLineEdit()
        self.so_number_edit.setText(str(sales_order["so_number"]))
        self.so_number_edit.setReadOnly(True)
        self.so_number_edit.setEnabled(False)
        form.addRow("SO Number:", self.so_number_edit)

        # Customer dropdown (read-only)
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

        # Status (read-only)
        self.txt_status = QLineEdit(sales_order["status"])
        self.txt_status.setReadOnly(True)
        form.addRow("Status:", self.txt_status)

        # Type (read-only)
        self.txt_type = QLineEdit(sales_order.get("type", "SO"))
        self.txt_type.setReadOnly(True)
        form.addRow("Type:", self.txt_type)

        main_layout.addLayout(form)

        # -------------------------
        # Items list
        # -------------------------
        items_layout = QVBoxLayout()
        items_layout.addWidget(QLabel("Order Items:"))
        self.items_list = QListWidget()
        items_layout.addWidget(self.items_list)

        for item in sales_order["items"]:
            if isinstance(item, str):
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

        # Enquiry link (readonly)
        self.enquiry_link = sales_order.get("enquiry_link")
        self.txt_enquiry_link = QLineEdit(self.enquiry_link or "")
        self.txt_enquiry_link.setReadOnly(True)
        form.addRow("Enquiry Link:", self.txt_enquiry_link)

        # -------------------------
        # Works Orders section
        # -------------------------
        self.wo_list = QListWidget()
        form.addRow("Works Orders:", self.wo_list)

        # Attach WO button
        self.btn_attach_wo = QPushButton("Attach Works Order")
        status = self.sales_order.get("status")
        self.btn_attach_wo.setEnabled(status == "released")
        form.addRow("", self.btn_attach_wo)
        self.btn_attach_wo.clicked.connect(self._attach_wo)

        # -------------------------
        # Buttons for item editing + workflow
        # -------------------------
        btn_layout = QHBoxLayout()
        self.add_item_btn = QPushButton("Add Item")
        self.edit_qty_btn = QPushButton("Edit Qty")
        self.remove_item_btn = QPushButton("Remove Item")
        self.btn_release = QPushButton("Release")
        self.btn_release.setEnabled(sales_order.get("status", "") == "new")

        self.btn_in_work = QPushButton("Move to In‑Work")
        self.btn_in_work.setVisible(False)
        self.btn_in_work.clicked.connect(self._move_to_in_work)

        self.btn_finish = QPushButton("Finish Order")
        self.btn_finish.setVisible(False)
        self.btn_finish.clicked.connect(self._finish_order)

        form.addRow("", self.btn_in_work)
        form.addRow("", self.btn_finish)

        btn_layout.addWidget(self.add_item_btn)
        btn_layout.addWidget(self.edit_qty_btn)
        btn_layout.addWidget(self.remove_item_btn)
        btn_layout.addWidget(self.btn_release)

        items_layout.addLayout(btn_layout)
        main_layout.addLayout(items_layout)

        # HELD SALES ORDER
        if self.sales_order.get("held", False):
            self._add_held_banner(self.sales_order.get("held_reason", ""))
            self._set_read_only_mode()

        # CANCELLED SALES ORDER
        if self.sales_order.get("status", "").lower() == "cancelled":
            self._add_cancelled_banner(self.sales_order.get("cancelled_reason", ""))
            self._set_read_only_mode()

        # IN‑WORK SALES ORDER → lock item editing
        if self.sales_order.get("status", "").lower() == "in-work":
            self.add_item_btn.setEnabled(False)
            self.edit_qty_btn.setEnabled(False)
            self.remove_item_btn.setEnabled(False)

        # Load existing WOs and update buttons
        self._load_attached_wos()
        self._update_in_work_button_visibility()
        self._update_finish_button_visibility()

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

        # -------------------------
        # Connections
        # -------------------------
        self.edit_qty_btn.clicked.connect(self._edit_item_qty)
        self.remove_item_btn.clicked.connect(self._remove_item)
        self.add_item_btn.clicked.connect(self._add_item)
        self.btn_release.clicked.connect(self._release_sales_order)

        if self.sales_order.get("enquiry_link"):
            self._add_enquiry_banner(self.sales_order["enquiry_link"])

    # ---------------------------------------------------------
    # Item quantity editing
    # ---------------------------------------------------------
    def _add_item(self):
        dlg = AddItemDialog(self.mongo, self.user, self)
        if dlg.exec():
            new_item_data = dlg.get_data()["items"]
            if not new_item_data:
                return

            for item in new_item_data:
                display = (
                    f"{item['part_number']} - {item['description']} "
                    f"(qty: {item['qty']} {item['uom']})"
                )

                list_item = QListWidgetItem(display)
                list_item.setData(Qt.UserRole, item)
                self.items_list.addItem(list_item)

                self.mongo.log_event(
                    "sales_order.item_add",
                    performed_by=getattr(self.user, "username", None),
                    details=(
                        f"Added item {item['part_number']} qty {item['qty']} {item['uom']} "
                        f"to Sales Order {self.so_number_edit.text()}"
                    )
                )

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

            self.mongo.log_event(
                "sales_order.item_qty_update",
                performed_by=getattr(self.user, "username", None),
                details=(
                    f"Updated qty for {data['part_number']} "
                    f"from {old_qty} to {new_qty} "
                    f"in Sales Order {self.so_number_edit.text()}"
                )
            )

            log_event(
                "info",
                "Sales order item qty updated",
                user=getattr(self.user, "username", None),
                so_number=self.so_number_edit.text(),
                part_number=data["part_number"],
                old_qty=old_qty,
                new_qty=new_qty
            )

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

        self.mongo.log_event(
            "sales_order.item_remove",
            performed_by=getattr(self.user, "username", None),
            details=(
                f"Removed item {data['part_number']} qty {data['qty']} {data['uom']} "
                f"from Sales Order {self.so_number_edit.text()}"
            )
        )

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
        self.req_date_edit.setEnabled(False)
        self.txt_status.setEnabled(False)
        self.txt_type.setEnabled(False)
        self.items_list.setEnabled(False)
        self.add_item_btn.setEnabled(False)
        self.edit_qty_btn.setEnabled(False)
        self.remove_item_btn.setEnabled(False)

        status = self.sales_order.get("status", "").lower()
        if status == "cancelled":
            self.setWindowTitle(f"Sales Order {self.sales_order['so_number']} (Cancelled - Read Only)")
        else:
            self.setWindowTitle(f"Sales Order {self.sales_order['so_number']} (Held - Read Only)")

    # ---------------------------------------------------------
    # Gather updated data
    # ---------------------------------------------------------
    def get_data(self):
        return {
            "so_number": self.so_number_edit.text().strip(),
            "customer": self.customer_combo.currentText(),
            "req_date": self.req_date_edit.date().toString("yyyy-MM-dd"),
            "type": self.txt_type.text(),
            "status": self.txt_status.text(),
            "items": [
                self.items_list.item(i).data(Qt.UserRole)
                for i in range(self.items_list.count())
            ],
            "updated_by": getattr(self.user, "username", None),
            "enquiry_link": self.sales_order.get("enquiry_link"),
        }

    def accept(self):
        updated_data = self.get_data()

        old_status = self.sales_order.get("status", "").lower()
        new_status = updated_data.get("status", "").lower()

        if new_status not in ALLOWED_TRANSITIONS.get(old_status, set()):
            QMessageBox.warning(
                self,
                "Invalid Status Change",
                f"You cannot change status from '{old_status}' to '{new_status}'."
            )
            return

        if updated_data["status"] == "in-work":
            so_number = self.sales_order["so_number"]
            wos = list(self.mongo.works_orders.find({"so_number": so_number}))

            if not wos:
                QMessageBox.warning(
                    self,
                    "Cannot Move to In‑Work",
                    "You must attach at least one Works Order before moving to In‑Work."
                )
                return

            allocated = set()
            for wo in wos:
                for item in wo.get("items", []):
                    allocated.add(item["part_number"])

            so_items = self.sales_order.get("items", [])
            required = {item["part_number"] for item in so_items}

            missing = required - allocated
            if missing:
                QMessageBox.warning(
                    self,
                    "Cannot Move to In‑Work",
                    "Not all BOM items have been allocated to Works Orders."
                )
                return

        try:
            self.mongo.sales_orders.update_one(
                {"so_number": self.sales_order["so_number"]},
                {"$set": updated_data}
            )
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))
            return

        if updated_data["status"] == "in-work":
            self.btn_attach_wo.setEnabled(False)

        super().accept()

    def _add_held_banner(self, reason: str):
        from PySide6.QtGui import QFont, QColor, QPalette

        banner = QLabel(f"⚠️  This Sales Order is HELD\nReason: {reason}")
        banner.setWordWrap(True)
        banner.setFont(QFont("Arial", 11, QFont.Bold))

        palette = banner.palette()
        palette.setColor(QPalette.Window, QColor("#FFCC66"))
        palette.setColor(QPalette.WindowText, QColor("#000000"))
        banner.setAutoFillBackground(True)
        banner.setPalette(palette)
        banner.setMargin(10)

        self.layout().insertWidget(0, banner)

    def _add_cancelled_banner(self, reason: str):
        from PySide6.QtGui import QFont, QColor, QPalette

        banner = QLabel(f"❌  This Sales Order is CANCELLED\nReason: {reason}")
        banner.setWordWrap(True)

        palette = banner.palette()
        palette.setColor(QPalette.Window, QColor("#FF6666"))
        palette.setColor(QPalette.WindowText, QColor("#000000"))
        banner.setAutoFillBackground(True)
        banner.setPalette(palette)

        banner.setFont(QFont("Arial", 11, QFont.Bold))
        banner.setMargin(10)

        self.layout().insertWidget(0, banner)

    def _add_enquiry_banner(self, enquiry_number):
        banner = QLabel(f"🔗 Linked to Enquiry SO{enquiry_number}")
        banner.setWordWrap(True)
        banner.setStyleSheet("""
            QLabel {
                background-color: #CCE5FF;
                color: #003366;
                font-weight: bold;
                padding: 10px;
            }
        """)
        self.layout().insertWidget(0, banner)

    def _load_attached_wos(self):
        self.wo_list.clear()
        so_number = self.sales_order["so_number"]

        wos = list(self.mongo.works_orders.find({"so_number": so_number}))
        for wo in wos:
            status = wo.get("status", "new")
            self.wo_list.addItem(f"WO{wo['wo_number']} - {status}")

    def _release_sales_order(self):
        if self.txt_type.text() == "firm" and not self.enquiry_link:
            self._prompt_enquiry_link()
            if not self.enquiry_link:
                return

        self.txt_status.setText("released")
        self.sales_order["status"] = "released"
        self.btn_release.setEnabled(False)
        self.btn_attach_wo.setEnabled(True)

        so_number = self.sales_order.get("so_number")

        self.mongo.sales_orders.update_one(
            {"so_number": so_number},
            {"$set": {
                "status": "released",
                "enquiry_link": self.enquiry_link
            }}
        )

        self._update_in_work_button_visibility()
        self._update_finish_button_visibility()

    def _prompt_enquiry_link(self):
        customer = self.customer_combo.currentText()

        enquiries = list(self.mongo.sales_orders.find({
            "type": "enquiry",
            "customer": customer,
            "status": {"$nin": ["cancelled"]}
        }))

        if not enquiries:
            QMessageBox.warning(self, "No Enquiries",
                                "There are no enquiries for this customer.")
            return

        dlg = QDialog(self)
        dlg.setWindowTitle("Select Enquiry")
        layout = QVBoxLayout(dlg)

        list_widget = QListWidget()
        for enq in enquiries:
            list_widget.addItem(f"{enq['so_number']} - {enq.get('req_date', '')}")
        layout.addWidget(list_widget)

        btn_ok = QPushButton("Link")
        layout.addWidget(btn_ok)
        btn_ok.clicked.connect(dlg.accept)

        if dlg.exec() == QDialog.Accepted:
            selected = list_widget.currentItem()
            if selected:
                enq_number = selected.text().split(" - ")[0]
                self.enquiry_link = enq_number
                self.sales_order["enquiry_link"] = enq_number
                self.txt_enquiry_link.setText(enq_number)

    def _attach_wo(self):
        so_number = self.sales_order["so_number"]

        wo_number = self.mongo.get_next_works_order_number()

        self.mongo.works_orders.insert_one({
            "wo_number": wo_number,
            "so_number": so_number,
            "customer": self.sales_order["customer"],
            "items": [],
            "status": "new",
            "created_by": getattr(self.user, "username", None)
        })

        self._prompt_load_items_into_wo(wo_number)

        self._load_attached_wos()
        self._update_in_work_button_visibility()
        self._update_finish_button_visibility()

    def _prompt_load_items_into_wo(self, wo_number):
        so_items = self.sales_order.get("items", [])

        so_number = self.sales_order["so_number"]
        existing_wos = list(self.mongo.works_orders.find({"so_number": so_number}))

        allocated = set()
        for wo in existing_wos:
            for item in wo.get("items", []):
                allocated.add(item["part_number"])

        available_items = [
            item for item in so_items
            if item["part_number"] not in allocated
        ]

        if not available_items:
            QMessageBox.information(
                self,
                "No Items Available",
                "All BOM items have already been allocated to Works Orders."
            )
            return

        dlg = BomMultiSelectDialog(available_items, self)
        if dlg.exec() != QDialog.Accepted:
            return

        selected_items = dlg.get_selected_items()
        if not selected_items:
            return

        self.mongo.works_orders.update_one(
            {"wo_number": wo_number},
            {"$push": {"items": {"$each": selected_items}}}
        )

        self.sales_order = self.mongo.sales_orders.find_one({"so_number": so_number})

        self._load_attached_wos()
        self._update_in_work_button_visibility()
        self._update_finish_button_visibility()

    def _update_in_work_button_visibility(self):
        status = self.sales_order.get("status")

        if status != "released":
            self.btn_in_work.setVisible(False)
            return

        so_items = self.sales_order.get("items", [])
        required = {item["part_number"] for item in so_items}

        so_number = self.sales_order["so_number"]
        wos = list(self.mongo.works_orders.find({"so_number": so_number}))

        allocated = set()
        for wo in wos:
            for item in wo.get("items", []):
                allocated.add(item["part_number"])

        self.btn_in_work.setVisible(required.issubset(allocated))

    def _move_to_in_work(self):
        so_number = self.sales_order["so_number"]

        wos = list(self.mongo.works_orders.find({"so_number": so_number}))
        if not wos:
            QMessageBox.warning(self, "Cannot Move to In‑Work",
                                "You must attach at least one Works Order.")
            return

        so_items = self.sales_order.get("items", [])
        required = {item["part_number"] for item in so_items}

        allocated = set()
        for wo in wos:
            for item in wo.get("items", []):
                allocated.add(item["part_number"])

        if not required.issubset(allocated):
            QMessageBox.warning(self, "Cannot Move to In‑Work",
                                "Not all BOM items have been allocated.")
            return

        self.mongo.sales_orders.update_one(
            {"so_number": so_number},
            {"$set": {"status": "in-work"}}
        )

        self.sales_order["status"] = "in-work"
        self.txt_status.setText("in-work")

        QMessageBox.information(self, "Sales Order Updated",
                                "Sales Order is now In‑Work.")

        self.btn_attach_wo.setEnabled(False)
        self.btn_in_work.setVisible(False)

        self._update_finish_button_visibility()

        self.accept()

    def _update_finish_button_visibility(self):
        status = self.sales_order.get("status")

        if status != "in-work":
            self.btn_finish.setVisible(False)
            return

        so_number = self.sales_order["so_number"]
        wos = list(self.mongo.works_orders.find({"so_number": so_number}))

        if not wos:
            self.btn_finish.setVisible(False)
            return

        all_completed = all(wo.get("status") == "completed" for wo in wos)
        self.btn_finish.setVisible(all_completed)

    def _finish_order(self):
        so_number = self.sales_order["so_number"]

        # Validate WOs completed
        wos = list(self.mongo.works_orders.find({"so_number": so_number}))
        if not all(wo.get("status") == "completed" for wo in wos):
            QMessageBox.warning(self, "Cannot Finish Order",
                                "All Works Orders must be completed.")
            return

        # Calculate costs
        cost_data = calculate_sales_order_cost(self.mongo, so_number)

        # Generate invoice
        invoice_number = generate_invoice(self.mongo, so_number, cost_data)

        # Generate dispatch note
        dispatch_number = generate_dispatch_note(self.mongo, so_number)

        # Update status in Mongo
        self.mongo.sales_orders.update_one(
            {"so_number": so_number},
            {"$set": {
                "status": "finished",
                "invoice_number": invoice_number,
                "dispatch_number": dispatch_number,
                "cost_summary": cost_data
            }}
        )

        # Update UI BEFORE closing
        self.sales_order["status"] = "finished"
        self.txt_status.setText("finished")

        QMessageBox.information(
            self,
            "Order Finished",
            f"Order finished.\nInvoice: {invoice_number}\nDispatch: {dispatch_number}"
        )

        # Close dialog WITHOUT triggering overridden accept()
        super().accept()

