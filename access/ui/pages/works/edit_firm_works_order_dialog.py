from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout, QLineEdit, QTextEdit,
    QDoubleSpinBox, QComboBox, QPushButton, QLabel, QDialogButtonBox, QMessageBox,
    QGroupBox, QTableWidget, QTableWidgetItem
)
from PySide6.QtCore import Qt
from datetime import datetime
from backend.wo_costing import calculate_enquiry_wo_cost
from PySide6.QtWidgets import QListWidget, QListWidgetItem

class ShopOrderQuantityDialog(QDialog):

    def __init__(
        self,
        part_number,
        description,
        required_qty,
        allocated_qty,
        parent=None
    ):
        super().__init__(parent)

        self.setWindowTitle("Create Shop Order")

        remaining_qty = required_qty - allocated_qty

        layout = QVBoxLayout(self)

        form = QFormLayout()

        form.addRow("Part Number:", QLabel(part_number))
        form.addRow("Description:", QLabel(description))
        form.addRow("Required Qty:", QLabel(str(required_qty)))
        form.addRow("Allocated Qty:", QLabel(str(allocated_qty)))
        form.addRow("Remaining Qty:", QLabel(str(remaining_qty)))

        self.qty_spin = QDoubleSpinBox()
        self.qty_spin.setDecimals(2)
        self.qty_spin.setMinimum(0.01)
        self.qty_spin.setMaximum(remaining_qty)
        self.qty_spin.setValue(remaining_qty)

        form.addRow("Qty To Make:", self.qty_spin)

        layout.addLayout(form)

        buttons = QDialogButtonBox(
            QDialogButtonBox.Ok |
            QDialogButtonBox.Cancel
        )

        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)

        layout.addWidget(buttons)

    def quantity(self):
        return self.qty_spin.value()

class EditFirmWorksOrderDialog(QDialog):

    def __init__(self, mongo, user, works_order, parent=None):
        super().__init__(parent)

        self.mongo = mongo
        self.user = user
        self.works_order = works_order

        self.setWindowTitle(
            f"Firm Works Order {works_order['wo_number']}"
        )
        self.setMinimumSize(800, 700)

        main_layout = QVBoxLayout(self)

        # ---------------------------------------------------------
        # Header
        # ---------------------------------------------------------
        header_box = QGroupBox("Works Order Details")
        header_layout = QFormLayout(header_box)

        self.txt_wo_number = QLineEdit(
            str(works_order["wo_number"])
        )
        self.txt_wo_number.setReadOnly(True)

        self.txt_so_number = QLineEdit(
            str(works_order.get("so_number", ""))
        )
        self.txt_so_number.setReadOnly(True)

        self.txt_customer = QLineEdit(
            works_order.get("customer", "")
        )
        self.txt_customer.setReadOnly(True)

        self.txt_req_date = QLineEdit(
            str(works_order.get("req_date", ""))
        )
        self.txt_req_date.setReadOnly(True)

        self.txt_status = QLineEdit(
            works_order.get("status", "new")
        )
        self.txt_status.setReadOnly(True)

        self.txt_type = QLineEdit("firm")
        self.txt_type.setReadOnly(True)

        header_layout.addRow("WO Number:", self.txt_wo_number)
        header_layout.addRow("Sales Order:", self.txt_so_number)
        header_layout.addRow("Customer:", self.txt_customer)
        header_layout.addRow("Type:", self.txt_type)
        header_layout.addRow("Required Date:", self.txt_req_date)
        header_layout.addRow("Status:", self.txt_status)

        main_layout.addWidget(header_box)

        # ---------------------------------------------------------
        # BOM + Shop Orders
        # ---------------------------------------------------------
        split_layout = QHBoxLayout()

        # BOM
        bom_box = QGroupBox("BOM Items")
        bom_layout = QVBoxLayout(bom_box)

        self.bom_list = QListWidget()
        bom_layout.addWidget(self.bom_list)

        split_layout.addWidget(bom_box)

        # Shop Orders
        sho_box = QGroupBox("Shop Orders")
        sho_layout = QVBoxLayout(sho_box)

        self.sho_list = QListWidget()
        self.sho_list.itemDoubleClicked.connect(
            self._open_shop_order
        )

        sho_layout.addWidget(self.sho_list)

        split_layout.addWidget(sho_box)

        main_layout.addLayout(split_layout)

        # ---------------------------------------------------------
        # Notes
        # ---------------------------------------------------------
        notes_box = QGroupBox("Notes")
        notes_layout = QVBoxLayout(notes_box)

        self.txt_notes = QTextEdit()
        self.txt_notes.setPlainText(
            works_order.get("notes", "")
        )

        notes_layout.addWidget(self.txt_notes)
        main_layout.addWidget(notes_box)

        # ---------------------------------------------------------
        # Buttons
        # ---------------------------------------------------------
        toolbar = QHBoxLayout()

        self.btn_workflow = QPushButton()
        self.btn_workflow.clicked.connect(
            self._workflow_action
        )

        self.btn_create_shop_order = QPushButton(
            "Create Shop Order"
        )
        self.btn_create_shop_order.clicked.connect(
            self._create_shop_order
        )

        toolbar.addWidget(self.btn_workflow)
        toolbar.addWidget(self.btn_create_shop_order)
        toolbar.addStretch()

        main_layout.addLayout(toolbar)

        # ---------------------------------------------------------
        # Initial load
        # ---------------------------------------------------------
        self._load_bom_items()
        self._load_shop_orders()

        self._update_workflow_button()
        self._apply_locking_rules()

    # ---------------------------------------------------------
    # BOM
    # ---------------------------------------------------------
    def _load_bom_items(self):
        self.bom_list.clear()

        items = self.works_order.get("items", [])

        if not items:
            self.bom_list.addItem(
                "No BOM items allocated."
            )
            return

        for item in items:

            required_qty = float(item.get("qty", 0))

            allocated_qty = self._allocated_qty_for_item(
                item["part_number"]
            )

            remaining_qty = (
                required_qty - allocated_qty
            )

            display_text = (
                f"{item['part_number']} - "
                f"{item['description']} | "
                f"Required: {required_qty:g} | "
                f"Allocated: {allocated_qty:g} | "
                f"Remaining: {remaining_qty:g}"
            )

            row = QListWidgetItem(display_text)

            row.setData(
                Qt.ItemDataRole.UserRole,
                item
            )

            self.bom_list.addItem(row)

    # ---------------------------------------------------------
    # Shop Orders
    # ---------------------------------------------------------
    def _load_shop_orders(self):
        self.sho_list.clear()

        wo_number = self.works_order["wo_number"]

        shops = list(
            self.mongo.shop_orders.find(
                {"wo_number": wo_number}
            )
        )

        if not shops:
            self.sho_list.addItem(
                "No Shop Orders linked."
            )
            return

        for sho in shops:

            status = sho.get("status", "new")

            item = QListWidgetItem(
                f"ShO {sho['sho_number']} - {status}"
            )

            item.setData(
                Qt.ItemDataRole.UserRole,
                sho["sho_number"]
            )

            self.sho_list.addItem(item)

    # ---------------------------------------------------------
    # Create Shop Order
    # ---------------------------------------------------------
    def _create_shop_order(self):

        selected = self.bom_list.currentItem()

        if not selected:
            QMessageBox.warning(
                self,
                "No Item Selected",
                "Please select a BOM item."
            )
            return

        bom_item = selected.data(Qt.ItemDataRole.UserRole)

        required_qty = float(bom_item["qty"])

        allocated_qty = self._allocated_qty_for_item(
            bom_item["part_number"]
        )

        remaining_qty = required_qty - allocated_qty

        if remaining_qty <= 0:
            QMessageBox.information(
                self,
                "Fully Allocated",
                "This BOM item has already been fully allocated."
            )
            return

        dlg = ShopOrderQuantityDialog(
            bom_item["part_number"],
            bom_item["description"],
            required_qty,
            allocated_qty,
            self
        )

        if dlg.exec() != QDialog.Accepted:
            return

        qty_to_make = dlg.quantity()

        sho_number = self.mongo.get_next_shop_order_number()

        self.mongo.shop_orders.insert_one({
            "sho_number": sho_number,

            "wo_number": self.works_order["wo_number"],
            "so_number": self.works_order.get("so_number"),
            "req_date": self.works_order.get("req_date"),
            "customer": self.works_order.get("customer"),

            "part_number": bom_item["part_number"],
            "description": bom_item["description"],
            "qty": qty_to_make,
            "uom": bom_item["uom"],

            "status": "new",

            "created_by": self.user.username
        })

        self._load_shop_orders()
        self._load_bom_items()

        QMessageBox.information(
            self,
            "Shop Order Created",
            f"Shop Order {sho_number} created."
        )

    # ---------------------------------------------------------
    # Open Shop Order
    # ---------------------------------------------------------
    def _open_shop_order(self, item):

        sho_number = item.data(
            Qt.ItemDataRole.UserRole
        )

        parent = self.parent()

        while parent is not None:

            if hasattr(
                parent,
                "open_shop_order_edit"
            ):
                parent.open_shop_order_edit(
                    sho_number
                )
                return

            parent = parent.parent()

    # ---------------------------------------------------------
    # Workflow button
    # ---------------------------------------------------------
    def _update_workflow_button(self):

        status = self.works_order.get(
            "status",
            "new"
        )

        if status == "new":
            self.btn_workflow.setText(
                "Release"
            )
            self.btn_workflow.show()

        elif status == "released":
            self.btn_workflow.setText(
                "Set To In Work"
            )
            self.btn_workflow.show()

        elif status == "in-work":

            self.btn_workflow.setText("Finish")
            self.btn_workflow.show()

            can_finish = self._all_shop_orders_finished()

            self.btn_workflow.setEnabled(
                can_finish
            )

        else:
            self.btn_workflow.hide()

    def _workflow_action(self):

        status = self.works_order.get(
            "status"
        )

        if status == "new":
            self._update_status("released")

        elif status == "released":
            self._update_status("in-work")

        elif status == "in-work":

            if not self._all_shop_orders_finished():

                QMessageBox.warning(
                    self,
                    "Cannot Finish Works Order",
                    "All Shop Orders must be finished before the Works Order can be finished."
                )
                return

            self._update_status("finished")

    # ---------------------------------------------------------
    # Status update
    # ---------------------------------------------------------
    def _update_status(
        self,
        new_status
    ):

        self.mongo.audit_log.insert_one({
            "event": "firm_works_order.status_change",
            "performed_by": self.user.username,
            "timestamp": datetime.utcnow(),
            "details": {
                "wo_number": self.works_order[
                    "wo_number"
                ],
                "old_status":
                    self.works_order.get(
                        "status"
                    ),
                "new_status":
                    new_status
            }
        })

        self.mongo.works_orders.update_one(
            {
                "wo_number":
                    self.works_order[
                        "wo_number"
                    ]
            },
            {
                "$set": {
                    "status": new_status,
                    "notes":
                        self.txt_notes.toPlainText(),
                    "updated_by":
                        self.user.username
                }
            }
        )

        self.works_order[
            "status"
        ] = new_status

        self.txt_status.setText(
            new_status
        )

        self._apply_locking_rules()
        self._update_workflow_button()

        if new_status == "finished":
            QMessageBox.information(
                self,
                "Works Order Finished",
                "Works Order marked as finished."
            )

    # ---------------------------------------------------------
    # Locking
    # ---------------------------------------------------------
    def _apply_locking_rules(self):

        status = self.works_order.get(
            "status"
        )

        can_edit = (
            self.user.has_permission(
                "worksorders.edit"
            )
        )

        self.txt_notes.setReadOnly(
            status == "finished"
        )

        self.btn_workflow.setEnabled(
            can_edit
        )

        self.btn_create_shop_order.setEnabled(
            can_edit and
            status in ("released", "in-work")
        )

    def _allocated_qty_for_item(self, part_number):

        total = 0

        shop_orders = self.mongo.shop_orders.find({
            "wo_number": self.works_order["wo_number"],
            "part_number": part_number
        })

        for sho in shop_orders:
            total += float(sho.get("qty", 0))

        return total

    def _all_shop_orders_finished(self):

        shops = list(
            self.mongo.shop_orders.find({
                "wo_number": self.works_order["wo_number"]
            })
        )

        if not shops:
            return False

        return all(
            sho.get("status") == "finished"
            for sho in shops
        )

    def _all_bom_allocated(self):

        for item in self.works_order.get("items", []):

            required_qty = float(item.get("qty", 0))

            allocated_qty = self._allocated_qty_for_item(
                item["part_number"]
            )

            if allocated_qty < required_qty:
                return False

        return True