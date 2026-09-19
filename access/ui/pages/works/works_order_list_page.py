from PySide6.QtWidgets import QWidget, QVBoxLayout, QListWidget, QListWidgetItem, QLabel
from PySide6.QtCore import Qt
from datetime import datetime


class WorksOrderListPage(QWidget):
    def __init__(self, mongo, user, window):
        super().__init__()

        self.mongo = mongo
        self.user = user
        self.window = window

        layout = QVBoxLayout(self)

        layout.addWidget(QLabel("Works Orders"))

        self.list = QListWidget()
        layout.addWidget(self.list)

        self._load_works_orders()

        self.list.itemDoubleClicked.connect(self._open_selected_order)

    def _load_works_orders(self):
        self.load_filtered({})
        self.list.clear()

        wos = list(self.mongo.works_orders.find({}).sort("wo_number", 1))

        for wo in wos:
            display = f"WO{wo['wo_number']} - {wo.get('status', 'new')} - SO{wo.get('so_number', '')}"
            item = QListWidgetItem(display)
            item.setData(Qt.UserRole, wo["wo_number"])
            self.list.addItem(item)

    def _open_selected_order(self, item):
        wo_number = item.data(Qt.UserRole)

        self.mongo.audit_log.insert_one({
            "event": "works_order.open",
            "performed_by": self.user.username,
            "timestamp": datetime.utcnow(),
            "details": {
                "wo_number": wo_number
            }
        })
        
        self.window.open_works_order_edit(wo_number)

    def load_filtered(self, query):
        self.list.clear()

        wos = list(self.mongo.works_orders.find(query).sort("wo_number", 1))

        for wo in wos:
            display = f"WO{wo['wo_number']} - {wo.get('status', 'new')} - SO{wo.get('so_number', '')}"
            item = QListWidgetItem(display)
            item.setData(Qt.UserRole, wo["wo_number"])
            self.list.addItem(item)
