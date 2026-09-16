from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QFormLayout, QLineEdit, QComboBox,
    QDialogButtonBox, QPushButton, QLabel, QDoubleSpinBox, QMessageBox
)
from PySide6.QtCore import Qt

from backend.wo_costing import calculate_enquiry_wo_cost


ALLOWED_WO_TRANSITIONS = {
    "new": {"new", "released"},
    "released": {"released", "in-work"},
    "in-work": {"in-work", "finished"},
    "finished": set()
}


class EditWorksOrderDialog(QDialog):
    def __init__(self, mongo, user, works_order, parent=None):
        super().__init__(parent)

        self.mongo = mongo
        self.user = user
        self.works_order = works_order

        self.setWindowTitle(f"Works Order {works_order['wo_number']}")
        self.setMinimumWidth(450)

        main_layout = QVBoxLayout(self)
        form = QFormLayout()

        # WO Number (read-only)
        self.wo_number_edit = QLineEdit(str(works_order["wo_number"]))
        self.wo_number_edit.setReadOnly(True)
        form.addRow("WO Number:", self.wo_number_edit)

        # SO Number (read-only)
        self.so_number_edit = QLineEdit(str(works_order["so_number"]))
        self.so_number_edit.setReadOnly(True)
        form.addRow("Sales Order:", self.so_number_edit)

        # Customer (read-only)
        self.customer_edit = QLineEdit(works_order.get("customer", ""))
        self.customer_edit.setReadOnly(True)
        form.addRow("Customer:", self.customer_edit)

        # Status (read-only)
        self.txt_status = QLineEdit(works_order.get("status", "new"))
        self.txt_status.setReadOnly(True)
        form.addRow("Status:", self.txt_status)

        # ---------------------------------------------------------
        # Estimate Fields (Enquiry WO)
        # ---------------------------------------------------------
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

        form.addRow("Labour Hours:", self.labour_hours)
        form.addRow("Labour Rate:", self.labour_rate)
        form.addRow("Material Cost:", self.material_cost)
        form.addRow("Subcontract Cost:", self.subcontract_cost)
        form.addRow("Overhead Cost:", self.overhead_cost)

        main_layout.addLayout(form)

        # ---------------------------------------------------------
        # Workflow Buttons
        # ---------------------------------------------------------
        self.btn_release = QPushButton("Release WO")
        self.btn_approve = QPushButton("Approve Estimate (In‑Work)")
        self.btn_finish = QPushButton("Finish WO")

        self.btn_release.clicked.connect(self._release_wo)
        self.btn_approve.clicked.connect(self._approve_estimate)
        self.btn_finish.clicked.connect(self._finish_wo)

        main_layout.addWidget(self.btn_release)
        main_layout.addWidget(self.btn_approve)
        main_layout.addWidget(self.btn_finish)

        self._update_button_visibility()

        # ---------------------------------------------------------
        # Dialog Buttons
        # ---------------------------------------------------------
        buttons = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.close)
        main_layout.addWidget(buttons)

        # Lock fields if needed
        self._apply_locking_rules()

    # ---------------------------------------------------------
    # Locking rules based on status
    # ---------------------------------------------------------
    def _apply_locking_rules(self):
        status = self.works_order.get("status")

        if status == "new":
            return  # fully editable

        if status == "released":
            # Estimate editable
            return

        if status == "in-work":
            # Estimate locked
            self.labour_hours.setEnabled(False)
            self.labour_rate.setEnabled(False)
            self.material_cost.setEnabled(False)
            self.subcontract_cost.setEnabled(False)
            self.overhead_cost.setEnabled(False)

        if status == "finished":
            # Everything locked
            self.labour_hours.setEnabled(False)
            self.labour_rate.setEnabled(False)
            self.material_cost.setEnabled(False)
            self.subcontract_cost.setEnabled(False)
            self.overhead_cost.setEnabled(False)

            self.btn_release.setVisible(False)
            self.btn_approve.setVisible(False)
            self.btn_finish.setVisible(False)

    # ---------------------------------------------------------
    # Button visibility
    # ---------------------------------------------------------
    def _update_button_visibility(self):
        status = self.works_order.get("status")

        self.btn_release.setVisible(status == "new")
        self.btn_approve.setVisible(status == "released")
        self.btn_finish.setVisible(status == "in-work")

    # ---------------------------------------------------------
    # Release WO
    # ---------------------------------------------------------
    def _release_wo(self):
        self.mongo.works_orders.update_one(
            {"wo_number": self.works_order["wo_number"]},
            {"$set": {"status": "released"}}
        )
        self.works_order["status"] = "released"
        self.txt_status.setText("released")
        self._update_button_visibility()
        self._apply_locking_rules()

    # ---------------------------------------------------------
    # Approve Estimate (Move to In‑Work)
    # ---------------------------------------------------------
    def _approve_estimate(self):
        self.mongo.works_orders.update_one(
            {"wo_number": self.works_order["wo_number"]},
            {"$set": {"status": "in-work"}}
        )
        self.works_order["status"] = "in-work"
        self.txt_status.setText("in-work")
        self._update_button_visibility()
        self._apply_locking_rules()

    # ---------------------------------------------------------
    # Finish WO
    # ---------------------------------------------------------
    def _finish_wo(self):
        wo_number = self.works_order["wo_number"]

        # Calculate estimated cost
        cost_data = calculate_enquiry_wo_cost(self.mongo, wo_number)

        # Update WO
        self.mongo.works_orders.update_one(
            {"wo_number": wo_number},
            {"$set": {
                "status": "finished",
                "estimated_cost": cost_data
            }}
        )

        self.works_order["status"] = "finished"
        self.txt_status.setText("finished")

        QMessageBox.information(
            self,
            "Works Order Finished",
            f"Estimated Cost: {cost_data['total_estimated_cost']:.2f}"
        )

        super().accept()

    # ---------------------------------------------------------
    # Save button
    # ---------------------------------------------------------
    def accept(self):
        updated = {
            "labour_hours": self.labour_hours.value(),
            "labour_rate": self.labour_rate.value(),
            "material_cost": self.material_cost.value(),
            "subcontract_cost": self.subcontract_cost.value(),
            "overhead_cost": self.overhead_cost.value(),
            "updated_by": getattr(self.user, "username", None)
        }

        self.mongo.works_orders.update_one(
            {"wo_number": self.works_order["wo_number"]},
            {"$set": updated}
        )

        super().accept()
