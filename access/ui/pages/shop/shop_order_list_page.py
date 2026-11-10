from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QComboBox,
    QTableWidget,
    QTableWidgetItem,
    QAbstractItemView
)

from PySide6.QtCore import Qt


class ShopOrderListPage(QWidget):

    def __init__(self, user, mongo, window):
        super().__init__()

        self.user = user
        self.mongo = mongo
        self.window = window

        self._build_ui()
        self._load_shop_orders()

    # ---------------------------------------------------------
    # UI
    # ---------------------------------------------------------
    def _build_ui(self):

        layout = QVBoxLayout(self)

        filter_row = QHBoxLayout()

        filter_row.addWidget(QLabel("Status:"))

        self.status_filter = QComboBox()
        self.status_filter.addItems([
            "All",
            "new",
            "released",
            "in-work",
            "finished"
        ])
        self.status_filter.currentTextChanged.connect(
            self._load_shop_orders
        )

        filter_row.addWidget(self.status_filter)

        filter_row.addWidget(QLabel("Search:"))

        self.search_edit = QLineEdit()
        self.search_edit.textChanged.connect(
            self._load_shop_orders
        )

        filter_row.addWidget(self.search_edit)

        filter_row.addStretch()

        layout.addLayout(filter_row)

        # -----------------------------------------------------
        # Table
        # -----------------------------------------------------

        self.table = QTableWidget()
        self.table.setColumnCount(8)

        self.table.setHorizontalHeaderLabels([
            "ShO Number",
            "WO Number",
            "SO Number",
            "Part Number",
            "Description",
            "Qty",
            "Required Date",
            "Status"
        ])

        self.table.setSelectionBehavior(
            QAbstractItemView.SelectRows
        )

        self.table.setEditTriggers(
            QAbstractItemView.NoEditTriggers
        )

        self.table.doubleClicked.connect(
            self._open_selected_order
        )

        layout.addWidget(self.table)

    # ---------------------------------------------------------
    # Load
    # ---------------------------------------------------------
    def _load_shop_orders(self):

        search_text = self.search_edit.text().lower()
        status_filter = self.status_filter.currentText()

        query = {}

        if status_filter != "All":
            query["status"] = status_filter

        orders = list(
            self.mongo.shop_orders.find(query)
        )

        rows = []

        for sho in orders:

            searchable = " ".join([
                str(sho.get("sho_number", "")),
                str(sho.get("wo_number", "")),
                str(sho.get("so_number", "")),
                str(sho.get("part_number", "")),
                str(sho.get("description", "")),
                str(sho.get("customer", ""))
            ]).lower()

            if search_text and search_text not in searchable:
                continue

            rows.append(sho)

        self.table.setRowCount(len(rows))

        for row, sho in enumerate(rows):

            self.table.setItem(
                row, 0,
                QTableWidgetItem(
                    str(sho.get("sho_number", ""))
                )
            )

            self.table.setItem(
                row, 1,
                QTableWidgetItem(
                    str(sho.get("wo_number", ""))
                )
            )

            self.table.setItem(
                row, 2,
                QTableWidgetItem(
                    str(sho.get("so_number", ""))
                )
            )

            self.table.setItem(
                row, 3,
                QTableWidgetItem(
                    sho.get("part_number", "")
                )
            )

            self.table.setItem(
                row, 4,
                QTableWidgetItem(
                    sho.get("description", "")
                )
            )

            self.table.setItem(
                row, 5,
                QTableWidgetItem(
                    str(sho.get("qty", ""))
                )
            )

            self.table.setItem(
                row, 6,
                QTableWidgetItem(
                    str(sho.get("req_date", ""))
                )
            )

            self.table.setItem(
                row, 7,
                QTableWidgetItem(
                    sho.get("status", "")
                )
            )

        self.table.resizeColumnsToContents()

    # ---------------------------------------------------------
    # Open Editor
    # ---------------------------------------------------------
    def _open_selected_order(self):

        row = self.table.currentRow()

        if row < 0:
            return

        sho_number = int(
            self.table.item(row, 0).text()
        )

        self.window.open_shop_order_edit(
            sho_number
        )

    # ---------------------------------------------------------
    # Refresh
    # ---------------------------------------------------------
    def refresh(self):
        self._load_shop_orders()