from datetime import datetime

from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QFormLayout,
    QLineEdit,
    QTextEdit,
    QPushButton,
    QGroupBox,
    QMessageBox
)


class EditShopOrderDialog(QDialog):

    def __init__(self, mongo, user, shop_order, parent=None):
        super().__init__(parent)

        self.mongo = mongo
        self.user = user
        self.shop_order = shop_order

        self.setWindowTitle(
            f"Shop Order {shop_order['sho_number']}"
        )

        self.setMinimumSize(800, 600)

        main_layout = QVBoxLayout(self)

        # ---------------------------------------------------------
        # Header
        # ---------------------------------------------------------
        header_box = QGroupBox("Shop Order Details")
        header_layout = QFormLayout(header_box)

        self.txt_sho_number = QLineEdit(
            str(shop_order.get("sho_number", ""))
        )
        self.txt_sho_number.setReadOnly(True)

        self.txt_wo_number = QLineEdit(
            str(shop_order.get("wo_number", ""))
        )
        self.txt_wo_number.setReadOnly(True)

        self.txt_so_number = QLineEdit(
            str(shop_order.get("so_number", ""))
        )
        self.txt_so_number.setReadOnly(True)

        self.txt_customer = QLineEdit(
            shop_order.get("customer", "")
        )
        self.txt_customer.setReadOnly(True)

        self.txt_req_date = QLineEdit(
            str(shop_order.get("req_date", ""))
        )
        self.txt_req_date.setReadOnly(True)

        self.txt_part_number = QLineEdit(
            shop_order.get("part_number", "")
        )
        self.txt_part_number.setReadOnly(True)

        self.txt_description = QLineEdit(
            shop_order.get("description", "")
        )
        self.txt_description.setReadOnly(True)

        self.txt_qty = QLineEdit(
            str(shop_order.get("qty", ""))
        )
        self.txt_qty.setReadOnly(True)

        self.txt_uom = QLineEdit(
            shop_order.get("uom", "")
        )
        self.txt_uom.setReadOnly(True)

        self.txt_status = QLineEdit(
            shop_order.get("status", "new")
        )
        self.txt_status.setReadOnly(True)

        header_layout.addRow("ShO Number:", self.txt_sho_number)
        header_layout.addRow("WO Number:", self.txt_wo_number)
        header_layout.addRow("SO Number:", self.txt_so_number)
        header_layout.addRow("Customer:", self.txt_customer)
        header_layout.addRow("Required Date:", self.txt_req_date)
        header_layout.addRow("Part Number:", self.txt_part_number)
        header_layout.addRow("Description:", self.txt_description)
        header_layout.addRow("Qty:", self.txt_qty)
        header_layout.addRow("UOM:", self.txt_uom)
        header_layout.addRow("Status:", self.txt_status)

        main_layout.addWidget(header_box)
        # ---------------------------------------------------------
        # BOM Item
        # ---------------------------------------------------------
        bom_box = QGroupBox("BOM Item")
        bom_layout = QVBoxLayout(bom_box)
        bom_layout.addWidget(
                QLineEdit("BOM will be added later")
            )
        
        main_layout.addWidget(bom_box)
        # ---------------------------------------------------------
        # Placeholder Sections
        # ---------------------------------------------------------
        routing_box = QGroupBox("Routing")
        routing_layout = QVBoxLayout(routing_box)
        routing_layout.addWidget(
            QLineEdit("Routing will be added later")
        )

        main_layout.addWidget(routing_box)

        booking_box = QGroupBox("Time Bookings")
        booking_layout = QVBoxLayout(booking_box)
        booking_layout.addWidget(
            QLineEdit("Time booking will be added later")
        )

        main_layout.addWidget(booking_box)

        # ---------------------------------------------------------
        # Notes
        # ---------------------------------------------------------
        notes_box = QGroupBox("Notes")
        notes_layout = QVBoxLayout(notes_box)

        self.txt_notes = QTextEdit()
        self.txt_notes.setPlainText(
            shop_order.get("notes", "")
        )

        notes_layout.addWidget(self.txt_notes)

        main_layout.addWidget(notes_box)

        # ---------------------------------------------------------
        # Workflow
        # ---------------------------------------------------------
        button_layout = QHBoxLayout()

        self.btn_workflow = QPushButton()
        self.btn_workflow.clicked.connect(
            self._workflow_action
        )

        button_layout.addWidget(
            self.btn_workflow
        )

        button_layout.addStretch()

        main_layout.addLayout(button_layout)

        self._update_workflow_button()
        self._apply_locking_rules()

    # ---------------------------------------------------------
    # Workflow Button
    # ---------------------------------------------------------
    def _update_workflow_button(self):

        status = self.shop_order.get(
            "status",
            "new"
        )

        if status == "new":
            self.btn_workflow.setText("Release")
            self.btn_workflow.show()

        elif status == "released":
            self.btn_workflow.setText("Set To In Work")
            self.btn_workflow.show()

        elif status == "in-work":
            self.btn_workflow.setText("Finish")
            self.btn_workflow.show()

        else:
            self.btn_workflow.hide()

    # ---------------------------------------------------------
    # Workflow Actions
    # ---------------------------------------------------------
    def _workflow_action(self):

        status = self.shop_order.get(
            "status"
        )

        if status == "new":
            self._update_status(
                "released"
            )

        elif status == "released":
            self._update_status(
                "in-work"
            )

        elif status == "in-work":
            self._update_status(
                "finished"
            )

    # ---------------------------------------------------------
    # Status Update
    # ---------------------------------------------------------
    def _update_status(
        self,
        new_status
    ):

        self.mongo.audit_log.insert_one({
            "event": "shop_order.status_change",
            "performed_by": self.user.username,
            "timestamp": datetime.utcnow(),
            "details": {
                "sho_number": self.shop_order[
                    "sho_number"
                ],
                "old_status": self.shop_order.get(
                    "status"
                ),
                "new_status": new_status
            }
        })

        self.mongo.shop_orders.update_one(
            {
                "sho_number":
                    self.shop_order["sho_number"]
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

        self.shop_order["status"] = new_status

        self.txt_status.setText(
            new_status
        )

        self._update_workflow_button()
        self._apply_locking_rules()

        if new_status == "finished":

            QMessageBox.information(
                self,
                "Finished",
                "Shop Order marked as finished."
            )

    # ---------------------------------------------------------
    # Locking
    # ---------------------------------------------------------
    def _apply_locking_rules(self):

        status = self.shop_order.get(
            "status"
        )

        can_edit = self.user.has_permission(
            "shop_orders.edit"
        )

        self.txt_notes.setReadOnly(
            status == "finished"
        )

        self.btn_workflow.setEnabled(
            can_edit
        )