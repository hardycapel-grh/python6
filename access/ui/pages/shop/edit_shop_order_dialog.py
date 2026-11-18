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
    QListWidget,
    QMessageBox
)
from ui.pages.shop.edit_shop_order_bom_dialog import (
    EditShopOrderBomDialog
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
        # Create controls first

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

        self.txt_bom_revision = QLineEdit(
            str(shop_order.get("bom_revision", ""))
        )
        self.txt_bom_revision.setReadOnly(True)

        header_box = QGroupBox("Shop Order Details")

        header_layout = QHBoxLayout(header_box)

        left_form = QFormLayout()
        right_form = QFormLayout()

        left_form.addRow("ShO Number:", self.txt_sho_number)
        left_form.addRow("WO Number:", self.txt_wo_number)
        left_form.addRow("SO Number:", self.txt_so_number)
        left_form.addRow("Customer:", self.txt_customer)
        left_form.addRow("Required Date:", self.txt_req_date)

        right_form.addRow("Part Number:", self.txt_part_number)
        right_form.addRow("Description:", self.txt_description)
        right_form.addRow("Qty:", self.txt_qty)
        right_form.addRow("UOM:", self.txt_uom)
        right_form.addRow("Status:", self.txt_status)
        right_form.addRow("BOM Revision:", self.txt_bom_revision)
        header_layout.addLayout(left_form)
        header_layout.addLayout(right_form)

        main_layout.addWidget(header_box)

        # ---------------------------------------------------------
        # BOM
        # ---------------------------------------------------------


        bom_box = QGroupBox("Shop Order BOM")
        bom_layout = QVBoxLayout(bom_box)

        bom_button_row = QHBoxLayout()

        self.btn_load_master_bom = QPushButton(
            "Load Master BOM"
        )

        self.btn_edit_bom = QPushButton(
            "Edit BOM"
        )

        bom_button_row.addWidget(
            self.btn_load_master_bom
        )

        bom_button_row.addWidget(
            self.btn_edit_bom
        )

        bom_layout.addLayout(
            bom_button_row
        )

        self.bom_list = QListWidget()

        bom_layout.addWidget(
            self.bom_list
        )

        main_layout.addWidget(
            bom_box
        )

        self.btn_load_master_bom.clicked.connect(
            self._load_master_bom
        )

        self._load_shop_bom()

        self.btn_edit_bom.clicked.connect(
            self._edit_bom
        )
        
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

        # can_edit = self.user.has_permission(
        #     "shop_orders.edit"
        # )

        can_edit = True

        self.txt_notes.setReadOnly(
            status == "finished"
        )

        self.btn_workflow.setEnabled(
            can_edit
        )

        shop_bom_loaded = bool(
            self.shop_order.get("shop_bom", [])
        )

        self.btn_load_master_bom.setEnabled(
            can_edit
            and status == "released"
            and not shop_bom_loaded
        )

        # Edit BOM
        self.btn_edit_bom.setEnabled(
            can_edit
            and status in ("released", "in-work")
            and shop_bom_loaded
        )

        if shop_bom_loaded:
            self.btn_load_master_bom.setText("BOM Loaded")
        else:
            self.btn_load_master_bom.setText("Load Master BOM")        

    def _load_shop_bom(self):

        self.bom_list.clear()

        shop_bom = self.shop_order.get(
            "shop_bom",
            []
        )

        if not shop_bom:

            self.bom_list.addItem(
                "No Shop Order BOM loaded."
            )

            return

        for line in shop_bom:

            display = (
                f"{line.get('component_part_number', '')} | "
                f"Rev {line.get('component_revision', '')} | "
                f"Qty Per {line.get('quantity', '')} "
                f"{line.get('uom', '')}"
            )

            comments = line.get(
                "comments",
                ""
            )

            if comments:
                display += f" | {comments}"

            self.bom_list.addItem(
                display
            )

    def _load_master_bom(self):

        if self.shop_order.get("status") != "released":

            QMessageBox.warning(
                self,
                "Not Allowed",
                "The Shop Order must be released before a BOM can be loaded."
            )

            return

        assembly_part = self.shop_order.get(
            "part_number"
        )

        boms = list(
            self.mongo.bom.find({
                "assembly_part_number": assembly_part
            })
        )

        if not boms:

            QMessageBox.warning(
                self,
                "No BOM Found",
                f"No BOM exists for {assembly_part}"
            )

            return

        # Select latest BOM revision
        bom = max(
            boms,
            key=lambda b: b.get(
                "created_at",
                datetime.min
            )
        )

        # Copy BOM into the Shop Order
        self.shop_order["shop_bom"] = (
            bom.get("lines", [])
        )


        # Store BOM revision for traceability
        self.shop_order["bom_revision"] = (
            bom.get("revision")
        )

        self.txt_bom_revision.setText(
            str(
                self.shop_order["bom_revision"]
            )
        )

        self.shop_order["bom_loaded_by"] = (
            self.user.username
        )

        self.shop_order["bom_loaded_at"] = (
            datetime.utcnow()
        )

        # Save to Mongo
        self.mongo.shop_orders.update_one(
            {
                "sho_number":
                    self.shop_order["sho_number"]
            },
            {
                "$set": {
                    "shop_bom":
                        self.shop_order["shop_bom"],

                    "bom_revision":
                        self.shop_order["bom_revision"],

                    "bom_loaded_by":
                        self.shop_order["bom_loaded_by"],

                    "bom_loaded_at":
                        self.shop_order["bom_loaded_at"]
                }
            }
        )

        # Update display if BOM Revision control exists
        if hasattr(self, "txt_bom_revision"):

            self.txt_bom_revision.setText(
                str(
                    bom.get("revision", "")
                )
            )

        # Refresh UI
        self._load_shop_bom()
        self._apply_locking_rules()

        QMessageBox.information(
            self,
            "BOM Loaded",
            f"Master BOM Revision "
            f"{bom.get('revision', '?')} loaded."
        )

    def _edit_bom(self):

        items_list = list(
            self.mongo.inventory.find({})
        )

        dlg = EditShopOrderBomDialog(
            self.mongo,
            items_list,
            self.shop_order.get("shop_bom", []),
            self
        )

        if dlg.exec() != QDialog.Accepted:
            return

        self.shop_order["shop_bom"] = dlg.lines

        self.mongo.shop_orders.update_one(
            {
                "sho_number":
                    self.shop_order["sho_number"]
            },
            {
                "$set": {
                    "shop_bom": dlg.lines
                }
            }
        )

        self._load_shop_bom()

        QMessageBox.information(
            self,
            "Saved",
            "Shop Order BOM updated."
        )        