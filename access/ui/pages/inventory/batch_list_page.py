from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QTableView
)
from PySide6.QtCore import Qt, QAbstractTableModel, QModelIndex


class BatchTableModel(QAbstractTableModel):
    def __init__(self, batches):
        super().__init__()
        self.batches = batches

        self.headers = [
            "GRN", "Batch", "Qty", "Unit Cost", "Expiry",
            "Store Type", "Ownership", "Customer", "Received"
        ]

    def rowCount(self, parent=None):
        return len(self.batches)

    def columnCount(self, parent=None):
        return len(self.headers)

    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid():
            return None

        batch = self.batches[index.row()]
        col = index.column()

        if role == Qt.DisplayRole:
            if col == 0: return batch.get("grn_number", "")
            if col == 1: return batch.get("batch_number", "")
            if col == 2: return batch.get("quantity", "")
            if col == 3: return batch.get("unit_cost", "")
            if col == 4: return batch.get("expiry_date", "")
            if col == 5: return batch.get("store_type", "")
            if col == 6: return batch.get("ownership", "")
            if col == 7: return batch.get("customer", "")
            if col == 8: return batch.get("received_date", "")

        return None

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if role == Qt.DisplayRole and orientation == Qt.Horizontal:
            return self.headers[section]
        return None


class BatchListPage(QWidget):
    def __init__(self, mongo, item, parent=None):
        super().__init__(parent)

        self.mongo = mongo
        self.item = item

        # Force proper window behaviour
        self.setWindowFlag(Qt.Window, True)
        self.setAttribute(Qt.WA_DeleteOnClose, True)
        self.setStyleSheet("background-color: white;")

        self.setWindowTitle(f"Batches — {item['part_number']}")

        layout = QVBoxLayout(self)

        title = QLabel(f"Batches for {item['part_number']} — {item['description']}")
        title.setStyleSheet("font-size: 18px; font-weight: bold;")
        layout.addWidget(title)

        self.table = QTableView()
        layout.addWidget(self.table)

        btn_row = QHBoxLayout()
        btn_close = QPushButton("Close")
        btn_close.clicked.connect(self.close)
        btn_row.addStretch()
        btn_row.addWidget(btn_close)
        layout.addLayout(btn_row)

        self.resize(900, 500)
        self.setMinimumSize(600, 400)

        self.load_batches()


    def load_batches(self):
        batches = list(self.mongo.inventory_batches.find(
            {"item_id": self.item["_id"]}
        ))

        self.model = BatchTableModel(batches)
        self.table.setModel(self.model)
        self.table.resizeColumnsToContents()
