from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QComboBox,
    QLineEdit, QTableView, QHeaderView
)
from PySide6.QtGui import QStandardItemModel, QStandardItem
from PySide6.QtCore import Qt

from ui.models.workbench_filter_proxy import WorkbenchFilterProxyModel
from ui.components.logger_utils import log_event

class WorkbenchPage(QWidget):
    def __init__(self, user, mongo, window):
        super().__init__()
        self.resize(1400, 600)
        self.user = user
        self.mongo = mongo
        self.window = window


        self._build_ui()
        self._load_workbench()

        # Audit log
        self.mongo.audit(
            event="workbench.view",
            performed_by=self.user.username,
            details={"action": "open_workbench"}
        )

        log_event("info", "Workbench opened", user=self.user.username)

    # ---------------------------------------------------------
    # UI Layout
    # ---------------------------------------------------------
    def _build_ui(self):
        layout = QVBoxLayout(self)

        # Filters row
        filter_row = QHBoxLayout()

        # Order type filter
        filter_row.addWidget(QLabel("Order Type:"))
        self.type_filter = QComboBox()
        self.type_filter.addItems(["All", "SO", "WO", "ShO", "PO", "IM"])
        self.type_filter.currentIndexChanged.connect(self._apply_filters)
        filter_row.addWidget(self.type_filter)

        # Status filter
        filter_row.addWidget(QLabel("Status:"))
        self.status_filter = QComboBox()
        self.status_filter.addItems(["All", "new", "released", "in-work", "enquired", "ordered", "received", "processed"])
        self.status_filter.currentIndexChanged.connect(self._apply_filters)
        filter_row.addWidget(self.status_filter)

        # Held filter
        filter_row.addWidget(QLabel("Held:"))
        self.held_filter = QComboBox()
        self.held_filter.addItems(["All", "Held Only", "Not Held"])
        self.held_filter.currentIndexChanged.connect(self._apply_filters)
        filter_row.addWidget(self.held_filter)

        # Search box
        filter_row.addWidget(QLabel("Search:"))
        self.search_box = QLineEdit()
        self.search_box.textChanged.connect(self._apply_filters)
        filter_row.addWidget(self.search_box)

        layout.addLayout(filter_row)

        # Table
        self.table = QTableView()
        self.table.doubleClicked.connect(self._open_selected_order)
        layout.addWidget(self.table)

        # Proxy model
        self.proxy = WorkbenchFilterProxyModel()
        self.table.setModel(self.proxy)

        # Table behaviour
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Stretch)
        self.table.setSortingEnabled(True)

    # ---------------------------------------------------------
    # Load Workbench Data
    # ---------------------------------------------------------
    def _load_workbench(self):
        rows = []

        # Load Sales Orders
        sales = list(self.mongo.sales_orders.find({
            "status": {"$nin": ["finished", "cancelled"]}
        }))

        for so in sales:
            rows.append({
                "order_type": "SO",
                "order_number": str(so.get("so_number", "")),
                "customer": so.get("customer", ""),
                "req_date": so.get("req_date", ""),
                "status": so.get("status", ""),
                "source_id": so["_id"],
                "linked_so": so.get("so_number", ""),
                "held": bool(so.get("held", False))
            })

        # Load Works Orders
        works = list(self.mongo.works_orders.find({
            "status": {"$nin": ["finished", "cancelled"]}
        }))

        for wo in works:
            rows.append({
                "order_type": "WO",
                "order_number": str(wo.get("wo_number", "")),
                "customer": wo.get("customer", ""),
                "req_date": wo.get("req_date", ""),
                "status": wo.get("status", ""),
                "source_id": wo["_id"],
                "linked_so": wo.get("so_number", ""),
                "held": bool(wo.get("held", False))
            })

        # Load Shop Orders
        shops = list(self.mongo.shop_orders.find({
            "status": {"$nin": ["finished", "cancelled"]}
        })) if hasattr(self.mongo, "shop_orders") else []

        for sho in shops:
            rows.append({
                "order_type": "ShO",
                "order_number": str(sho.get("sho_number", "")),
                "customer": sho.get("customer", ""),
                "req_date": sho.get("req_date", ""),
                "status": sho.get("status", ""),
                "source_id": sho["_id"],
                "linked_so": sho.get("so_number", ""),
                "held": bool(sho.get("held", False))
            })

        # -----------------------------
        # Purchase Orders (PO)
        # -----------------------------
        pos = list(self.mongo.purchase_orders.find({
            "status": {"$nin": ["cancelled"]}
        }))

        for po in pos:
            rows.append({
                "order_type": "PO",
                "order_number": str(po.get("po_number", "")),
                "customer": po.get("supplier", ""),
                "req_date": po.get("req_date", ""),
                "status": po.get("status", ""),
                "source_id": po["_id"],
                "linked_so": po.get("linked_so", ""),
                "held": bool(po.get("held", False))
            })

        # -----------------------------
        # Inventory Movements (IM)
        # -----------------------------
        ims = list(self.mongo.inventory_movements.find({
            "status": {"$nin": ["cancelled"]}
        }))

        for im in ims:
            rows.append({
                "order_type": "IM",
                "order_number": str(im.get("im_number", "")),
                "customer": im.get("movement_type", ""),  # movement type shown in customer column
                "req_date": im.get("req_date", ""),
                "status": im.get("status", ""),
                "source_id": im["_id"],
                "linked_so": im.get("linked_so", ""),
                "held": bool(im.get("held", False))
            })


        # Build model
        model = QStandardItemModel(len(rows), 6)
        model.setHorizontalHeaderLabels([
            "Type", "Number", "Customer", "Req Date", "Status", "SO Link", "Held"
        ])

        for row_idx, row in enumerate(rows):
            model.setItem(row_idx, 0, QStandardItem(row["order_type"]))
            model.setItem(row_idx, 1, QStandardItem(row["order_number"]))
            model.setItem(row_idx, 2, QStandardItem(row["customer"]))
            model.setItem(row_idx, 3, QStandardItem(row["req_date"]))
            model.setItem(row_idx, 4, QStandardItem(row["status"]))
            model.setItem(row_idx, 5, QStandardItem(str(row["linked_so"])))
            model.setItem(row_idx, 6, QStandardItem("Yes" if row["held"] else "No"))


        self.proxy.setSourceModel(model)
        self._apply_filters()

    # ---------------------------------------------------------
    # Apply Filters
    # ---------------------------------------------------------
    def _apply_filters(self):
        self.proxy.set_type_filter(self.type_filter.currentText())
        self.proxy.set_status_filter(self.status_filter.currentText())
        self.proxy.set_search_filter(self.search_box.text())
        self.proxy.set_held_filter(self.held_filter.currentText())

        log_event(
            "info",
            "Workbench filters applied",
            user=self.user.username,
            type=self.type_filter.currentText(),
            status=self.status_filter.currentText(),
            search=self.search_box.text()
        )

    # ---------------------------------------------------------
    # Open Selected Order
    # ---------------------------------------------------------
    def _open_selected_order(self, index):
        proxy_index = self.proxy.mapToSource(index)
        model = self.proxy.sourceModel()

        order_type = model.item(proxy_index.row(), 0).text()
        order_number = model.item(proxy_index.row(), 1).text()

        log_event(
            "info",
            "Workbench open order",
            user=self.user.username,
            order_type=order_type,
            order_number=order_number
        )

        # Route to correct edit page
        if order_type == "SO":
            self.window.open_sales_order_edit(order_number)
        elif order_type == "WO":
            self.window.open_works_order_edit(order_number)
        elif order_type == "ShO":
            self.window.open_shop_order_edit(order_number)
