from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout, QLineEdit, QTextEdit,
    QDoubleSpinBox, QComboBox, QPushButton, QLabel, QDialogButtonBox, QMessageBox,
    QGroupBox, QTableWidget, QTableWidgetItem
)
from PySide6.QtCore import Qt
from datetime import datetime
from backend.wo_costing import calculate_enquiry_wo_cost
from PySide6.QtWidgets import QListWidget, QListWidgetItem

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
            text = (
                f"{item.get('part_number', '')} - "
                f"{item.get('description', '')} "
                f"(Qty: {item.get('qty', '')} "
                f"{item.get('uom', '')})"
            )

            self.bom_list.addItem(text)

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

        sho_number = self.mongo.get_next_shop_order_number()

        self.mongo.shop_orders.insert_one({
            "sho_number": sho_number,
            "wo_number": self.works_order["wo_number"],
            "so_number": self.works_order.get(
                "so_number"
            ),
            "customer": self.works_order.get(
                "customer"
            ),
            "status": "new",
            "created_by": self.user.username
        })

        self._load_shop_orders()

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
            self.btn_workflow.setText(
                "Finish"
            )
            self.btn_workflow.show()

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