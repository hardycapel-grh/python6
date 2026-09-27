from PySide6.QtWidgets import QWidget, QVBoxLayout, QListWidget, QListWidgetItem, QLabel, QHBoxLayout, QComboBox
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

        # ---------------------------------------------------------
        # Filter Bar
        # ---------------------------------------------------------
        filter_bar = QHBoxLayout()

        self.cmb_type = QComboBox()
        self.cmb_type.addItems(["All", "Enquiry", "Firm"])
        self.cmb_type.currentTextChanged.connect(self.apply_filters)

        filter_bar.addWidget(QLabel("Type:"))
        filter_bar.addWidget(self.cmb_type)

        layout.addLayout(filter_bar)
        # ---------------------------------------------------------

        # Only ONE list widget
        self.list = QListWidget()
        layout.addWidget(self.list)

        # Only ONE initial load
        self._load_works_orders()

        # Only ONE double-click handler
        self.list.itemDoubleClicked.connect(self._open_selected_order)



    def _load_works_orders(self):
        self.load_filtered({})
        # self.list.clear()

        # wos = list(self.mongo.works_orders.find({}).sort("wo_number", 1))

        # for wo in wos:
        #     display = f"WO{wo['wo_number']} - {wo.get('status', 'new')} - SO{wo.get('so_number', '')}"
        #     item = QListWidgetItem(display)
        #     item.setData(Qt.UserRole, wo["wo_number"])
        #     self.list.addItem(item)

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
            wo_type = wo.get("type", "enquiry")  # default
            self.list.addItem(item)

    


    def apply_filters(self):
        query = {}

        wo_type = self.cmb_type.currentText()
        if wo_type != "All":
            query["type"] = wo_type.lower()

        self.load_filtered(query)
