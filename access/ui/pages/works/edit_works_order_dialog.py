from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QFormLayout, QLineEdit, QComboBox,
    QDialogButtonBox, QListWidget, QListWidgetItem, QAbstractItemView, QPushButton,
    QHBoxLayout, QLabel, QDateEdit, QInputDialog, QMessageBox
)
from PySide6.QtCore import Qt, QDate
from PySide6.QtWidgets import QDoubleSpinBox, QCheckBox

from ui.components.logger_utils import log_event
from ui.pages.sales.add_item_dialog import AddItemDialog

from backend.sales_order_costing import calculate_sales_order_cost
from backend.invoice_generator import generate_invoice
from backend.dispatch_generator import generate_dispatch_note


class EditWorksOrderDialog(QDialog):
    def __init__(self, mongo, user, works_order, parent=None):
        super().__init__(parent)
        self.setWindowTitle(f"Works Order {works_order['wo_number']}")
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Works Order editor coming soon"))
        btn = QDialogButtonBox(QDialogButtonBox.Close)
        btn.rejected.connect(self.close)
        layout.addWidget(btn)
