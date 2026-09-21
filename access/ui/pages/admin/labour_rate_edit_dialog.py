# ui/pages/admin/labour_rate_edit_dialog.py

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QFormLayout, QLineEdit,
    QDoubleSpinBox, QDialogButtonBox, QMessageBox
)
from datetime import datetime

class LabourRateEditDialog(QDialog):
    def __init__(self, mongo, user, rate, parent=None):
        super().__init__(parent)

        self.mongo = mongo
        self.user = user
        self.rate = rate

        self.setWindowTitle("Edit Labour Rate" if rate else "New Labour Rate")

        layout = QVBoxLayout(self)
        form = QFormLayout()

        self.txt_code = QLineEdit(rate["code"] if rate else "")
        self.txt_description = QLineEdit(rate["description"] if rate else "")

        self.spin_rate = QDoubleSpinBox()
        self.spin_rate.setRange(0, 9999)
        self.spin_rate.setValue(rate["rate"] if rate else 0)

        form.addRow("Code:", self.txt_code)
        form.addRow("Description:", self.txt_description)
        form.addRow("Rate (£/hr):", self.spin_rate)

        layout.addLayout(form)

        buttons = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def accept(self):
        code = self.txt_code.text().strip()
        desc = self.txt_description.text().strip()
        rate_value = self.spin_rate.value()

        if not code:
            QMessageBox.warning(self, "Missing Code", "Code is required.")
            return

        doc = {
            "code": code,
            "description": desc,
            "rate": rate_value,
            "active": True
        }

        if self.rate:
            self.mongo.labour_rates.update_one({"code": code}, {"$set": doc})
            event = "labour_rate.update"
        else:
            self.mongo.labour_rates.insert_one(doc)
            event = "labour_rate.create"

        self.mongo.audit_log.insert_one({
            "event": event,
            "performed_by": self.user.username,
            "timestamp": datetime.utcnow(),
            "details": doc
        })

        super().accept()
