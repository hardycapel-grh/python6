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
from PySide6.QtCore import Qt, QDate, QTimer
from PySide6.QtWidgets import QDoubleSpinBox, QCheckBox

from ui.components.logger_utils import log_event
from ui.pages.sales.add_item_dialog import AddItemDialog

from ui.pages.sales.add_item_dialog import AddItemDialog



ALLOWED_TRANSITIONS = {
    "new":        {"new","released"},
    "released":   {"released", "in-work"},
    "in-work":    {"in-work","finished"},
    # "held":       {"new", "released", "in-work", "cancelled"},
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

        # Add items with checkboxes
        for item in items:
            lw_item = QListWidgetItem(
                f"{item['part_number']} - {item['description']} (qty: {item['qty']} {item['uom']})"
            )
            lw_item.setFlags(lw_item.flags() | Qt.ItemIsUserCheckable)
            lw_item.setCheckState(Qt.Unchecked)
            self.list.addItem(lw_item)

        layout.addWidget(self.list)

        # OK / Cancel buttons
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

        # Status 
        self.txt_status = QLineEdit(sales_order["status"])
        self.txt_status.setReadOnly(True)
        form.addRow("Status:", self.txt_status)

        # Type (readonly)
        self.txt_type = QLineEdit(sales_order.get("type", "SO"))
        self.txt_type.setReadOnly(True)
        form.addRow("Type:", self.txt_type)

        if self.sales_order.get("status") == "in-work":
            self.items_table.setEnabled(False)



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

        # Load existing WOs linked to this SO
        self._load_attached_wos()

        # Button to attach WO (only enabled when SO is released)
        self.btn_attach_wo = QPushButton("Attach Works Order")
        # self.btn_attach_wo.setEnabled(sales_order.get("status") == "released")
        status = self.sales_order.get("status")
        self.btn_attach_wo.setEnabled(status == "released")

        form.addRow("", self.btn_attach_wo)

        self.btn_attach_wo.clicked.connect(self._attach_wo)


        # Buttons for item editing
        btn_layout = QHBoxLayout()
        self.add_item_btn = QPushButton("Add Item")
        self.edit_qty_btn = QPushButton("Edit Qty")
        self.remove_item_btn = QPushButton("Remove Item")
        self.btn_release = QPushButton("Release")
        self.btn_release.setEnabled(sales_order.get("status", "") == "new")


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
        self.req_date_edit.setEnabled(False)
        self.status_combo.setEnabled(False)
        self.type_combo.setEnabled(False)
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
            "status": self.txt_status.text(),   # ← FIXED
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

        # ⭐ Firm order must link to an enquiry before release
        # if updated_data.get("type") == "firm" and new_status == "released":
        #     if not self.sales_order.get("enquiry_link"):
        #         # Fetch enquiries for this customer
        #         enquiries = list(self.mongo.sales_orders.find({
        #             "customer": updated_data.get("customer"),
        #             "type": "enquiry",
        #             "status": {"$in": ["new", "released", "in-work"]}  # allowed enquiry states
        #         }))

        #         if not enquiries:
        #             QMessageBox.warning(
        #                 self,
        #                 "No Enquiries Available",
        #                 "This firm order cannot be released because there are no valid enquiries "
        #                 "for this customer."
        #             )
        #             return

        #         # Build selection list
        #         enquiry_numbers = [str(e["so_number"]) for e in enquiries]

        #         selected, ok = QInputDialog.getItem(
        #             self,
        #             "Select Enquiry",
        #             "Select the enquiry this firm order relates to:",
        #             enquiry_numbers,
        #             editable=False
        #         )

        #         if not ok:
        #             return

        #         # Store the link
        #         updated_data["enquiry_link"] = selected
        #         self.sales_order["enquiry_link"] = selected



        # ⭐ Workflow rule enforcement
        if new_status not in ALLOWED_TRANSITIONS.get(old_status, set()):
            from PySide6.QtWidgets import QMessageBox
            QMessageBox.warning(
                self,
                "Invalid Status Change",
                f"You cannot change status from '{old_status}' to '{new_status}'."
            )
            return  # stop the save
        
        if updated_data["status"] == "in-work":
            so_number = self.sales_order["so_number"]

            # Fetch all WOs for this SO
            wos = list(self.mongo.works_orders.find({"so_number": so_number}))

            if not wos:
                QMessageBox.warning(
                    self,
                    "Cannot Move to In‑Work",
                    "You must attach at least one Works Order before moving to In‑Work."
                )
                return

            # Collect allocated BOM part_numbers
            allocated = set()
            for wo in wos:
                for item in wo.get("items", []):
                    allocated.add(item["part_number"])

            # Collect SO BOM part_numbers
            so_items = self.sales_order.get("items", [])
            required = {item["part_number"] for item in so_items}

            # Check if all BOM items are allocated
            missing = required - allocated
            if missing:
                QMessageBox.warning(
                    self,
                    "Cannot Move to In‑Work",
                    "Not all BOM items have been allocated to Works Orders."
                )
                return

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
        
        if updated_data["status"] == "in-work":
            self.btn_attach_wo.setEnabled(False)

        super().accept()

    def _add_held_banner(self, reason: str):
        from PySide6.QtWidgets import QLabel
        from PySide6.QtGui import QFont, QColor, QPalette

        banner = QLabel(f"⚠️  This Sales Order is HELD\nReason: {reason}")
        banner.setWordWrap(True)

        # Style the banner
        banner.setFont(QFont("Arial", 11, QFont.Bold))

        palette = banner.palette()
        palette.setColor(QPalette.Window, QColor("#FFCC66"))   # amber background
        palette.setColor(QPalette.WindowText, QColor("#000000"))
        banner.setAutoFillBackground(True)
        banner.setPalette(palette)

        banner.setMargin(10)

        # Insert at top of the dialog layout
        self.layout().insertWidget(0, banner)

    def _add_cancelled_banner(self, reason: str):
        from PySide6.QtGui import QFont, QColor, QPalette

        banner = QLabel(f"❌  This Sales Order is CANCELLED\nReason: {reason}")
        banner.setWordWrap(True)

        palette = banner.palette()
        palette.setColor(QPalette.Window, QColor("#FF6666"))   # red
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
        """Load all Works Orders linked to this Sales Order."""
        self.wo_list.clear()
        so_number = self.sales_order["so_number"]

        wos = list(self.mongo.works_orders.find({"so_number": so_number}))
        for wo in wos:
            status = wo.get("status", "new")
            self.wo_list.addItem(f"WO{wo['wo_number']} - {status}")


    def _release_sales_order(self):
        # If firm order and no enquiry link → block release
        if self.txt_type.text() == "firm" and not self.enquiry_link:
            self._prompt_enquiry_link()
            if not self.enquiry_link:
                return  # user cancelled

        self.txt_status.setText("released")
        self.btn_release.setEnabled(False)   # ← disable it
        self.btn_attach_wo.setEnabled(True)

            
        so_number = self.sales_order.get("so_number")

        # update Mongo immediately
        self.mongo.sales_orders.update_one(
            {"so_number": so_number},
            {"$set": {
                "status": "released",
                "enquiry_link": self.enquiry_link
            }}
        )


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
            list_widget.addItem(f"{enq['so_number']} - {enq.get('req_date','')}")
        layout.addWidget(list_widget)

        btn_ok = QPushButton("Link")
        layout.addWidget(btn_ok)
        btn_ok.clicked.connect(dlg.accept)

        if dlg.exec() == QDialog.Accepted:
            selected = list_widget.currentItem()
            if selected:
                enq_number = selected.text().split(" - ")[0]

                # ⭐ THESE THREE LINES ARE THE FIX
                self.enquiry_link = enq_number
                self.sales_order["enquiry_link"] = enq_number
                self.txt_enquiry_link.setText(enq_number)

    def _attach_wo(self):
        """Always create a new Works Order and attach it to this SO."""
        so_number = self.sales_order["so_number"]

        # Create new WO number
        wo_number = self.mongo.get_next_works_order_number()

        # Insert new WO
        self.mongo.works_orders.insert_one({
            "wo_number": wo_number,
            "so_number": so_number,
            "customer": self.sales_order["customer"],
            "items": [],
            "status": "new",
            "created_by": getattr(self.user, "username", None)
        })

        # Ask whether to load SO items
        self._prompt_load_items_into_wo(wo_number)

        # Refresh WO list
        self._load_attached_wos()

    def _prompt_load_items_into_wo(self, wo_number):
        """Allow user to select multiple BOM items that have not yet been allocated."""
        so_items = self.sales_order.get("items", [])

        # Find all WOs already attached to this SO
        so_number = self.sales_order["so_number"]
        existing_wos = list(self.mongo.works_orders.find({"so_number": so_number}))

        # Collect already allocated part_numbers
        allocated = set()
        for wo in existing_wos:
            for item in wo.get("items", []):
                allocated.add(item["part_number"])

        # Filter SO items to only those not yet allocated
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

        # Show multi-select dialog
        dlg = BomMultiSelectDialog(available_items, self)
        if dlg.exec() != QDialog.Accepted:
            return

        selected_items = dlg.get_selected_items()
        if not selected_items:
            return

        # Add all selected items to the WO
        self.mongo.works_orders.update_one(
            {"wo_number": wo_number},
            {"$push": {"items": {"$each": selected_items}}}
        )

        # Refresh WO list
        self._load_attached_wos()



