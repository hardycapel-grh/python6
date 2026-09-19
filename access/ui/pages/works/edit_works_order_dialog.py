from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout, QLineEdit, QTextEdit,
    QDoubleSpinBox, QPushButton, QLabel, QDialogButtonBox, QMessageBox,
    QGroupBox
)
from PySide6.QtCore import Qt
from datetime import datetime
from backend.wo_costing import calculate_enquiry_wo_cost


class EditWorksOrderDialog(QDialog):
    def __init__(self, mongo, user, works_order, parent=None):
        super().__init__(parent)

        self.mongo = mongo
        self.user = user
        self.works_order = works_order

        self.setWindowTitle(f"Works Order {works_order['wo_number']}")
        self.setMinimumWidth(600)

        main_layout = QVBoxLayout(self)

        # ---------------------------------------------------------
        # Header Section
        # ---------------------------------------------------------
        header_box = QGroupBox("Works Order Details")
        header_layout = QFormLayout(header_box)

        self.txt_wo_number = QLineEdit(str(works_order["wo_number"]))
        self.txt_wo_number.setReadOnly(True)

        self.txt_so_number = QLineEdit(str(works_order.get("so_number", "")))
        self.txt_so_number.setReadOnly(True)

        self.txt_customer = QLineEdit(works_order.get("customer", ""))
        self.txt_customer.setReadOnly(True)

        self.txt_status = QLineEdit(works_order.get("status", "new"))
        self.txt_status.setReadOnly(True)

        header_layout.addRow("WO Number:", self.txt_wo_number)
        header_layout.addRow("Sales Order:", self.txt_so_number)
        header_layout.addRow("Customer:", self.txt_customer)
        header_layout.addRow("Status:", self.txt_status)

        main_layout.addWidget(header_box)

        # ---------------------------------------------------------
        # Workflow Toolbar
        # ---------------------------------------------------------
        toolbar = QHBoxLayout()

        self.btn_release = QPushButton("Release")
        self.btn_approve = QPushButton("Approve Estimate")
        self.btn_finish = QPushButton("Finish")

        self.btn_release.clicked.connect(self._release_wo)
        self.btn_approve.clicked.connect(self._approve_estimate)
        self.btn_finish.clicked.connect(self._finish_wo)

        toolbar.addWidget(self.btn_release)
        toolbar.addWidget(self.btn_approve)
        toolbar.addWidget(self.btn_finish)

        main_layout.addLayout(toolbar)

        # ---------------------------------------------------------
        # Estimate Section
        # ---------------------------------------------------------
        estimate_box = QGroupBox("Estimate")
        estimate_layout = QFormLayout(estimate_box)

        self.labour_hours = QDoubleSpinBox()
        self.labour_hours.setRange(0, 99999)
        self.labour_hours.setValue(works_order.get("labour_hours", 0))

        self.labour_rate = QDoubleSpinBox()
        self.labour_rate.setRange(0, 99999)
        self.labour_rate.setValue(works_order.get("labour_rate", 0))

        self.material_cost = QDoubleSpinBox()
        self.material_cost.setRange(0, 999999)
        self.material_cost.setValue(works_order.get("material_cost", 0))

        self.subcontract_cost = QDoubleSpinBox()
        self.subcontract_cost.setRange(0, 999999)
        self.subcontract_cost.setValue(works_order.get("subcontract_cost", 0))

        self.overhead_cost = QDoubleSpinBox()
        self.overhead_cost.setRange(0, 999999)
        self.overhead_cost.setValue(works_order.get("overhead_cost", 0))

        estimate_layout.addRow("Labour Hours:", self.labour_hours)
        estimate_layout.addRow("Labour Rate:", self.labour_rate)
        estimate_layout.addRow("Material Cost:", self.material_cost)
        estimate_layout.addRow("Subcontract Cost:", self.subcontract_cost)
        estimate_layout.addRow("Overhead Cost:", self.overhead_cost)

        main_layout.addWidget(estimate_box)

        # ---------------------------------------------------------
        # Cost Summary Panel
        # ---------------------------------------------------------
        summary_box = QGroupBox("Cost Summary")
        summary_layout = QFormLayout(summary_box)

        self.lbl_labour_cost = QLabel("£0.00")
        self.lbl_material_cost = QLabel("£0.00")
        self.lbl_subcontract_cost = QLabel("£0.00")
        self.lbl_overhead_cost = QLabel("£0.00")
        self.lbl_total_cost = QLabel("£0.00")

        summary_layout.addRow("Labour Cost:", self.lbl_labour_cost)
        summary_layout.addRow("Material Cost:", self.lbl_material_cost)
        summary_layout.addRow("Subcontract Cost:", self.lbl_subcontract_cost)
        summary_layout.addRow("Overhead Cost:", self.lbl_overhead_cost)
        summary_layout.addRow("Total Estimated Cost:", self.lbl_total_cost)

        main_layout.addWidget(summary_box)

        # Live update
        for widget in [
            self.labour_hours, self.labour_rate,
            self.material_cost, self.subcontract_cost, self.overhead_cost
        ]:
            widget.valueChanged.connect(self._update_cost_summary)

        self._update_cost_summary()

        # ---------------------------------------------------------
        # Notes Section
        # ---------------------------------------------------------
        notes_box = QGroupBox("Notes")
        notes_layout = QVBoxLayout(notes_box)

        self.txt_notes = QTextEdit()
        self.txt_notes.setPlainText(works_order.get("notes", ""))

        notes_layout.addWidget(self.txt_notes)
        main_layout.addWidget(notes_box)

        # ---------------------------------------------------------
        # Dialog Buttons
        # ---------------------------------------------------------
        buttons = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.close)
        main_layout.addWidget(buttons)

        # Apply locking rules
        self._apply_locking_rules()
        self._update_toolbar_visibility()

    # ---------------------------------------------------------
    # Cost Summary Calculation
    # ---------------------------------------------------------
    def _update_cost_summary(self):
        labour_cost = self.labour_hours.value() * self.labour_rate.value()
        material_cost = self.material_cost.value()
        subcontract_cost = self.subcontract_cost.value()
        overhead_cost = self.overhead_cost.value()

        total = labour_cost + material_cost + subcontract_cost + overhead_cost

        self.lbl_labour_cost.setText(f"£{labour_cost:.2f}")
        self.lbl_material_cost.setText(f"£{material_cost:.2f}")
        self.lbl_subcontract_cost.setText(f"£{subcontract_cost:.2f}")
        self.lbl_overhead_cost.setText(f"£{overhead_cost:.2f}")
        self.lbl_total_cost.setText(f"£{total:.2f}")

    # ---------------------------------------------------------
    # Workflow Actions
    # ---------------------------------------------------------
    def _release_wo(self):
        self.mongo.audit_log.insert_one({
            "event": "works_order.release",
            "performed_by": self.user.username,
            "timestamp": datetime.utcnow(),
            "details": {
                "wo_number": self.works_order["wo_number"],
                "status": "released"
            }
        })
        self._update_status("released")

    def _approve_estimate(self):
        self.mongo.audit_log.insert_one({
            "event": "works_order.approve_estimate",
            "performed_by": self.user.username,
            "timestamp": datetime.utcnow(),
            "details": {
                "wo_number": self.works_order["wo_number"],
                "status": "in-work"
            }
        })
        self._update_status("in-work")

    def _finish_wo(self):
        self.mongo.audit_log.insert_one({
            "event": "works_order.finish",
            "performed_by": self.user.username,
            "timestamp": datetime.utcnow(),
            "details": {
                "wo_number": self.works_order["wo_number"],
                "estimated_cost": cost_data
            }
        })

        cost_data = calculate_enquiry_wo_cost(self.mongo, self.works_order["wo_number"])
        self.mongo.works_orders.update_one(
            {"wo_number": self.works_order["wo_number"]},
            {"$set": {
                "status": "finished",
                "estimated_cost": cost_data,
                "notes": self.txt_notes.toPlainText(),
                "updated_by": self.user.username
            }}
        )
        QMessageBox.information(self, "Finished", "Works Order marked as finished.")
        super().accept()

    def _update_status(self, new_status):
        self.mongo.works_orders.update_one(
            {"wo_number": self.works_order["wo_number"]},
            {"$set": {
                "status": new_status,
                "notes": self.txt_notes.toPlainText(),
                "updated_by": self.user.username
            }}
        )
        self.works_order["status"] = new_status
        self.txt_status.setText(new_status)
        self._apply_locking_rules()
        self._update_toolbar_visibility()

    # ---------------------------------------------------------
    # Locking Rules
    # ---------------------------------------------------------
    def _apply_locking_rules(self):
        status = self.works_order.get("status")

        editable = status in ("new", "released")

        for widget in [
            self.labour_hours, self.labour_rate,
            self.material_cost, self.subcontract_cost, self.overhead_cost
        ]:
            widget.setEnabled(editable)

        if status == "finished":
            self.txt_notes.setReadOnly(True)

    # ---------------------------------------------------------
    # Toolbar Visibility
    # ---------------------------------------------------------
    def _update_toolbar_visibility(self):
        status = self.works_order.get("status")

        self.btn_release.setVisible(status == "new")
        self.btn_approve.setVisible(status == "released")
        self.btn_finish.setVisible(status == "in-work")

    # ---------------------------------------------------------
    # Save
    # ---------------------------------------------------------
    def accept(self):
        updated = {
            "labour_hours": self.labour_hours.value(),
            "labour_rate": self.labour_rate.value(),
            "material_cost": self.material_cost.value(),
            "subcontract_cost": self.subcontract_cost.value(),
            "overhead_cost": self.overhead_cost.value(),
            "notes": self.txt_notes.toPlainText(),
            "updated_by": self.user.username
        }

        self.mongo.works_orders.update_one(
            {"wo_number": self.works_order["wo_number"]},
            {"$set": updated}
        )

        self.mongo.audit_log.insert_one({
            "event": "works_order.save",
            "performed_by": self.user.username,
            "timestamp": datetime.utcnow(),
            "details": {
                "wo_number": self.works_order["wo_number"],
                "fields_updated": list(updated.keys())
            }
        })

        super().accept()

