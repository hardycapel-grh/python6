from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout, QLineEdit, QTextEdit,
    QDoubleSpinBox, QComboBox, QPushButton, QLabel, QDialogButtonBox, QMessageBox,
    QGroupBox, QTableWidget, QTableWidgetItem
)
from PySide6.QtCore import Qt
from datetime import datetime
from backend.wo_costing import calculate_enquiry_wo_cost
from PySide6.QtWidgets import QListWidget, QListWidgetItem




            

class LabourHoursEditorDialog(QDialog):
    def __init__(self, mongo, works_order, parent=None):
        super().__init__(parent)
        self.mongo = mongo
        self.works_order = works_order

        self.setWindowTitle("Labour Hours Breakdown")
        self.resize(1200, 600)

        layout = QVBoxLayout(self)

        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels([
            "Component", "Description", "Qty",
            "Labour Hours", "Material Cost",
            "Subcontract Cost", "Overhead Cost"
        ])

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

        # Map existing hours + costs by component
        hours_map = {item["component"]: item.get("hours", 0) for item in breakdown}
        material_map = {item["component"]: item.get("material_cost", 0) for item in breakdown}
        subcontract_map = {item["component"]: item.get("subcontract_cost", 0) for item in breakdown}
        overhead_map = {item["component"]: item.get("overhead_cost", 0) for item in breakdown}

        self.table.setRowCount(len(bom))

        for row, item in enumerate(bom):
            comp = item.get("part_number")
            desc = item.get("description", "")
            qty = item.get("qty", 1)

            # Existing values or defaults
            hours = hours_map.get(comp, 0)
            material = material_map.get(comp, 0)
            subcontract = subcontract_map.get(comp, 0)
            overhead = overhead_map.get(comp, 0)

            # Component
            self.table.setItem(row, 0, QTableWidgetItem(comp))
            self.table.setItem(row, 1, QTableWidgetItem(desc))
            self.table.setItem(row, 2, QTableWidgetItem(str(qty)))

            # Labour Hours
            spin_hours = QDoubleSpinBox()
            spin_hours.setRange(0, 999)
            spin_hours.setValue(hours)
            self.table.setCellWidget(row, 3, spin_hours)

            # Material Cost
            spin_material = QDoubleSpinBox()
            spin_material.setRange(0, 999999)
            spin_material.setValue(material)
            self.table.setCellWidget(row, 4, spin_material)

            # Subcontract Cost
            spin_sub = QDoubleSpinBox()
            spin_sub.setRange(0, 999999)
            spin_sub.setValue(subcontract)
            self.table.setCellWidget(row, 5, spin_sub)

            # Overhead Cost
            spin_over = QDoubleSpinBox()
            spin_over.setRange(0, 999999)
            spin_over.setValue(overhead)
            self.table.setCellWidget(row, 6, spin_over)



    def get_breakdown(self):
        breakdown = []
        total_hours = 0
        total_material = 0
        total_subcontract = 0
        total_overhead = 0

        for row in range(self.table.rowCount()):
            comp = self.table.item(row, 0).text()
            desc = self.table.item(row, 1).text()
            qty = int(float(self.table.item(row, 2).text()))

            hours = self.table.cellWidget(row, 3).value()
            material = self.table.cellWidget(row, 4).value()
            subcontract = self.table.cellWidget(row, 5).value()
            overhead = self.table.cellWidget(row, 6).value()

            breakdown.append({
                "component": comp,
                "description": desc,
                "qty": qty,
                "hours": hours,
                "material_cost": material,
                "subcontract_cost": subcontract,
                "overhead_cost": overhead
            })

            total_hours += hours
            total_material += material
            total_subcontract += subcontract
            total_overhead += overhead

        totals = {
            "labour": total_hours,
            "material": total_material,
            "subcontract": total_subcontract,
            "overhead": total_overhead,
            "total": total_hours + total_material + total_subcontract + total_overhead
        }

        return breakdown, totals



from datetime import datetime

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QFormLayout,
    QGroupBox,
    QLineEdit,
    QTextEdit,
    QPushButton,
    QListWidget,
    QListWidgetItem,
    QMessageBox,
)


