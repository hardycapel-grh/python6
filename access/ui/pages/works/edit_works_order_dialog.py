from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout, QLineEdit, QTextEdit,
    QDoubleSpinBox, QComboBox, QPushButton, QLabel, QDialogButtonBox, QMessageBox,
    QGroupBox, QTableWidget, QTableWidgetItem
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

        self.txt_type = QLineEdit(works_order.get("type", "enquiry"))
        self.txt_type.setReadOnly(True)

        header_layout.addRow("WO Number:", self.txt_wo_number)
        header_layout.addRow("Sales Order:", self.txt_so_number)
        header_layout.addRow("Customer:", self.txt_customer)
        header_layout.addRow("Type:", self.txt_type)
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
        self.btn_edit_labour = QPushButton("Edit Breakdown")
        self.btn_edit_labour.clicked.connect(self._open_labour_editor)
        wo_type = self.works_order.get("type", "enquiry")
        wo_status = self.works_order.get("status", "new")

        self.btn_edit_labour.setEnabled(
            wo_type == "enquiry" and wo_status == "released"
        )




        # self.labour_rate = QDoubleSpinBox()
        # self.labour_rate.setRange(0, 99999)
        # self.labour_rate.setValue(works_order.get("labour_rate", 0))

        self.cmb_labour_rate = QComboBox()
        self._populate_labour_rates()

        self.material_cost = QDoubleSpinBox()
        self.material_cost.setRange(0, 999999)
        self.material_cost.setValue(works_order.get("material_cost", 0))

        self.subcontract_cost = QDoubleSpinBox()
        self.subcontract_cost.setRange(0, 999999)
        self.subcontract_cost.setValue(works_order.get("subcontract_cost", 0))

        self.overhead_cost = QDoubleSpinBox()
        self.overhead_cost.setRange(0, 999999)
        self.overhead_cost.setValue(works_order.get("overhead_cost", 0))

        labour_row = QHBoxLayout()
        labour_row.addWidget(self.labour_hours)
        labour_row.addWidget(self.btn_edit_labour)

        estimate_layout.addRow("Labour Hours:", labour_row)

        estimate_layout.addRow("Labour Rate:", self.cmb_labour_rate)
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
            self.labour_hours,
            self.material_cost, self.subcontract_cost, self.overhead_cost
        ]:
            widget.valueChanged.connect(self._update_cost_summary)

        self.cmb_labour_rate.currentIndexChanged.connect(self._update_cost_summary)


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
        selected_rate = self.cmb_labour_rate.currentData()
        labour_rate_value = selected_rate["rate"]

        labour_cost = self.labour_hours.value() * labour_rate_value
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
        selected = self.cmb_labour_rate.currentData()
        cost_data = calculate_enquiry_wo_cost(self.mongo, self.works_order["wo_number"])
        self.mongo.works_orders.update_one(
            {"wo_number": self.works_order["wo_number"]},
            {"$set": {
                "status": "finished",
                "estimated_cost": cost_data,
                "notes": self.txt_notes.toPlainText(),
                "updated_by": self.user.username,
                "labour_rate_code": selected["code"],
                "labour_rate_value": selected["rate"]
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

        self.btn_edit_labour.setEnabled(
            status == "released" and self.works_order.get("type") == "enquiry"
        )

        for widget in [
            self.labour_hours, self.cmb_labour_rate,
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
        selected = self.cmb_labour_rate.currentData()

        updated = {
            "type": self.txt_type.text(),
            "labour_rate_code": selected["code"],
            "labour_rate_value": selected["rate"],
            "labour_hours": self.labour_hours.value(),
            "material_cost": self.material_cost.value(),
            "subcontract_cost": self.subcontract_cost.value(),
            "overhead_cost": self.overhead_cost.value(),
            "notes": self.txt_notes.toPlainText(),
            "updated_by": self.user.username
        }


        updated["labour_breakdown"] = self.works_order.get("labour_breakdown", [])

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

        updated["labour_breakdown"] = self.works_order.get("labour_breakdown", [])

        super().accept()

    def _populate_labour_rates(self):
        self.cmb_labour_rate.clear()

        rates = list(self.mongo.labour_rates.find({"active": True}).sort("code", 1))

        for r in rates:
            # Store the entire Mongo document as userData
            self.cmb_labour_rate.addItem(
                f"{r['code']} – £{r['rate']:.2f}",
                r
            )

        # Pre-select the WO's existing rate if present
        if "labour_rate_code" in self.works_order:
            for i in range(self.cmb_labour_rate.count()):
                if self.cmb_labour_rate.itemData(i)["code"] == self.works_order["labour_rate_code"]:
                    self.cmb_labour_rate.setCurrentIndex(i)
                    break

    def _open_labour_editor(self):
        dlg = LabourHoursEditorDialog(self.mongo, self.works_order, self)
        if dlg.exec():
            breakdown, total_hours = dlg.get_breakdown()

            # Save into WO object (not Mongo yet)
            self.works_order["labour_breakdown"] = breakdown

            # Update labour hours field
            self.labour_hours.setValue(total_hours)

            # Update cost summary
            self._update_cost_summary()
            

class LabourHoursEditorDialog(QDialog):
    def __init__(self, mongo, works_order, parent=None):
        super().__init__(parent)
        self.mongo = mongo
        self.works_order = works_order

        self.setWindowTitle("Labour Hours Breakdown")
        self.resize(1200, 600)

        layout = QVBoxLayout(self)

        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["Component", "Description", "Qty", "Hours"])
        layout.addWidget(self.table)

        self._load_bom()

        buttons = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def _load_bom(self):
        # Use WO items as BOM
        bom = self.works_order.get("items", [])
        breakdown = self.works_order.get("labour_breakdown", [])

        # Map existing hours by component
        hours_map = {item["component"]: item["hours"] for item in breakdown}

        self.table.setRowCount(len(bom))

        for row, item in enumerate(bom):
            comp = item.get("part_number")
            desc = item.get("description", "")
            qty = item.get("qty", 1)
            hours = hours_map.get(comp, 0)

            self.table.setItem(row, 0, QTableWidgetItem(comp))
            self.table.setItem(row, 1, QTableWidgetItem(desc))
            self.table.setItem(row, 2, QTableWidgetItem(str(qty)))

            spin = QDoubleSpinBox()
            spin.setRange(0, 999)
            spin.setValue(hours)
            self.table.setCellWidget(row, 3, spin)


    def get_breakdown(self):
        breakdown = []
        total = 0

        for row in range(self.table.rowCount()):
            comp = self.table.item(row, 0).text()
            desc = self.table.item(row, 1).text()
            qty = int(float(self.table.item(row, 2).text()))
            hours = self.table.cellWidget(row, 3).value()

            breakdown.append({
                "component": comp,
                "description": desc,
                "qty": qty,
                "hours": hours
            })

            total += hours

        return breakdown, total
