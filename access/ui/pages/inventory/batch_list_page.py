from PySide6.QtWidgets import (
    QHeaderView, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QTableView, QSizePolicy, QDialog, QTextEdit
)
from PySide6.QtCore import Qt, QAbstractTableModel, QModelIndex
# duplicate import removed



class BatchTableModel(QAbstractTableModel):
    def __init__(self, batches):
        super().__init__()
        self.batches = batches

        self.headers = [
            "GRN",
            "Batch",
            "Quantity",
            "Unit Cost",
            "Expiry",
            "Store",
            "Received"
        ]


    def rowCount(self, parent=None):
        return len(self.batches)

    def columnCount(self, parent=None):
        return 7

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
            if col == 5: return batch.get("store_name", "")
            if col == 6: return batch.get("received_date", "")

        if role == Qt.UserRole:
            return batch.get("_id")

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

        self.setWindowTitle(f"Batches — {item['part_number']}")
        self.setMinimumSize(600, 400)
        self.resize(900, 500)

        layout = QVBoxLayout(self)

        title = QLabel(f"Batches for {item['part_number']} — {item['description']}")
        title.setStyleSheet("font-size: 18px; font-weight: bold;")
        layout.addWidget(title)

        self.table = QTableView()
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setSelectionBehavior(QTableView.SelectRows)
        self.table.setSelectionMode(QTableView.SingleSelection)
        layout.addWidget(self.table)

        # Connect double-click
        self.table.doubleClicked.connect(self._open_batch_details)

        # Close button row
        btn_row = QHBoxLayout()
        btn_close = QPushButton("Close")
        btn_close.clicked.connect(self.close)
        btn_row.addStretch()
        btn_row.addWidget(btn_close)
        layout.addLayout(btn_row)

        self.load_batches()

    def load_batches(self):
        stores = {s["_id"]: s for s in self.mongo.stores.find()}

        batches = list(self.mongo.inventory_batches.find(
            {"item_id": self.item["_id"]}
        ))

        for b in batches:
            store = stores.get(b.get("store_id"))
            b["store_name"] = store["name"] if store else "Unknown"

        self.model = BatchTableModel(batches)
        self.table.setModel(self.model)

        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

    def _open_batch_details(self, index):
        row = index.row()
        batch = self.model.batches[row]

        details = (
            f"GRN Number: {batch.get('grn_number', '')}\n"
            f"Batch Number: {batch.get('batch_number', '')}\n"
            f"Quantity: {batch.get('quantity', '')}\n"
            f"Unit Cost: {batch.get('unit_cost', '')}\n"
            f"Expiry Date: {batch.get('expiry_date', '')}\n"
            f"Store: {batch.get('store_name', '')}\n"
            f"Received Date: {batch.get('received_date', '')}\n"
        )

        dlg = QDialog(self)
        dlg.setWindowTitle("Batch Details")
        dlg.setMinimumWidth(400)

        layout = QVBoxLayout(dlg)

        text = QTextEdit()
        text.setReadOnly(True)
        text.setText(details)
        layout.addWidget(text)

        btn = QPushButton("Close")
        btn.clicked.connect(dlg.accept)
        layout.addWidget(btn)

        dlg.exec()

