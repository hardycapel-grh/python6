# ui/pages/admin/labour_rate_manager_page.py

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QTableWidget, QTableWidgetItem, QMessageBox
)
from ui.pages.admin.labour_rate_edit_dialog import LabourRateEditDialog
from datetime import datetime

class LabourRateManagerPage(QWidget):
    def __init__(self, mongo, user, main_window):
        super().__init__()
        self.mongo = mongo
        self.user = user
        self.main_window = main_window

        layout = QVBoxLayout(self)

        # Buttons
        btns = QHBoxLayout()
        self.btn_new = QPushButton("New Rate")
        self.btn_edit = QPushButton("Edit Selected")
        self.btn_delete = QPushButton("Deactivate Selected")

        btns.addWidget(self.btn_new)
        btns.addWidget(self.btn_edit)
        btns.addWidget(self.btn_delete)

        layout.addLayout(btns)

        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["Code", "Description", "Rate", "Active"])
        layout.addWidget(self.table)

        self.btn_new.clicked.connect(self._new_rate)
        self.btn_edit.clicked.connect(self._edit_rate)
        self.btn_delete.clicked.connect(self._deactivate_rate)

        self.load_rates()

    # ---------------------------------------------------------
    # Load Rates
    # ---------------------------------------------------------
    def load_rates(self):
        rates = list(self.mongo.labour_rates.find({}).sort("code", 1))
        self.table.setRowCount(len(rates))

        for row, rate in enumerate(rates):
            self.table.setItem(row, 0, QTableWidgetItem(rate["code"]))
            self.table.setItem(row, 1, QTableWidgetItem(rate["description"]))
            self.table.setItem(row, 2, QTableWidgetItem(f"{rate['rate']:.2f}"))
            self.table.setItem(row, 3, QTableWidgetItem("Yes" if rate.get("active", True) else "No"))

    # ---------------------------------------------------------
    # New Rate
    # ---------------------------------------------------------
    def _new_rate(self):
        dlg = LabourRateEditDialog(self.mongo, self.user, None, self)
        if dlg.exec():
            self.load_rates()

    # ---------------------------------------------------------
    # Edit Rate
    # ---------------------------------------------------------
    def _edit_rate(self):
        row = self.table.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Select Rate", "Please select a rate to edit.")
            return

        code = self.table.item(row, 0).text()
        rate = self.mongo.labour_rates.find_one({"code": code})

        dlg = LabourRateEditDialog(self.mongo, self.user, rate, self)
        if dlg.exec():
            self.load_rates()

    # ---------------------------------------------------------
    # Deactivate Rate
    # ---------------------------------------------------------
    def _deactivate_rate(self):
        row = self.table.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Select Rate", "Please select a rate to deactivate.")
            return

        code = self.table.item(row, 0).text()

        self.mongo.labour_rates.update_one(
            {"code": code},
            {"$set": {"active": False}}
        )

        self.mongo.audit_log.insert_one({
            "event": "labour_rate.deactivate",
            "performed_by": self.user.username,
            "timestamp": datetime.utcnow(),
            "details": {"code": code}
        })

        self.load_rates()
