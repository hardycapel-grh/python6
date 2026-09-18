# ui/windows/works_order_window.py

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QComboBox,
    QLineEdit, QPushButton
)

from ui.pages.works.works_order_list_page import WorksOrderListPage


class WorksOrderWindow(QWidget):
    def __init__(self, mongo, user, main_window):
        super().__init__()

        self.mongo = mongo
        self.user = user
        self.main_window = main_window

        layout = QVBoxLayout(self)

        # ---------------------------------------------------------
        # Filter Toolbar
        # ---------------------------------------------------------
        toolbar = QHBoxLayout()

        # Status filter
        self.cmb_status = QComboBox()
        self.cmb_status.addItem("All")
        self.cmb_status.addItem("new")
        self.cmb_status.addItem("released")
        self.cmb_status.addItem("in-work")
        self.cmb_status.addItem("finished")

        # Customer filter
        self.cmb_customer = QComboBox()
        self.cmb_customer.addItem("All Customers")
        self._populate_customer_filter()

        # SO number filter
        self.txt_so_number = QLineEdit()
        self.txt_so_number.setPlaceholderText("SO Number")

        # Text search
        self.txt_search = QLineEdit()
        self.txt_search.setPlaceholderText("Search WO…")

        # Refresh button
        self.btn_refresh = QPushButton("Refresh")

        toolbar.addWidget(QLabel("Status:"))
        toolbar.addWidget(self.cmb_status)

        toolbar.addWidget(QLabel("Customer:"))
        toolbar.addWidget(self.cmb_customer)


        toolbar.addWidget(QLabel("SO:"))
        toolbar.addWidget(self.txt_so_number)

        toolbar.addWidget(self.txt_search)
        toolbar.addWidget(self.btn_refresh)

        layout.addLayout(toolbar)

        # ---------------------------------------------------------
        # Works Order List Page
        # ---------------------------------------------------------
        self.page = WorksOrderListPage(mongo, user, main_window)
        layout.addWidget(self.page)

        # ---------------------------------------------------------
        # Connect filters
        # ---------------------------------------------------------
        self.cmb_status.currentTextChanged.connect(self.apply_filters)
        self.cmb_customer.currentTextChanged.connect(self.apply_filters)
        self.txt_so_number.textChanged.connect(self.apply_filters)
        self.txt_search.textChanged.connect(self.apply_filters)
        self.btn_refresh.clicked.connect(self.apply_filters)

        # Initial load
        self.apply_filters()

    # ---------------------------------------------------------
    # Apply Filters
    # ---------------------------------------------------------
    def apply_filters(self):
        status = self.cmb_status.currentText()
        so_number = self.txt_so_number.text().strip()
        search = self.txt_search.text().strip()

        # Refresh customer dropdown
        if self.sender() == self.btn_refresh:
            self._populate_customer_filter()


        query = {}

        # Status filter
        if status != "All":
            query["status"] = status

        # Customer filter
        customer = self.cmb_customer.currentText()
        if customer != "All Customers":
            query["customer"] = customer

        # SO number filter
        if so_number:
            query["so_number"] = so_number

        # Text search (WO number or customer)
        if search:
            query["$or"] = [
                {"wo_number": {"$regex": search, "$options": "i"}},
                {"customer": {"$regex": search, "$options": "i"}},
            ]

        self.page.load_filtered(query)


    def _populate_customer_filter(self):
        customers = sorted({
            wo.get("customer", "")
            for wo in self.mongo.works_orders.find({})
            if wo.get("customer")
        })

        for cust in customers:
            self.cmb_customer.addItem(cust)
