from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLineEdit,
    QLabel, QComboBox, QTableView
)
from PySide6.QtCore import Qt, QSortFilterProxyModel

from ui.components.logger_utils import log_event


class InventoryListPage(QWidget):
    def __init__(self, user, mongo, parent=None):
        super().__init__(parent)

        self.user = user
        self.mongo = mongo
        self.app = parent

        log_event("info", "InventoryListPage initialized", user=user.username)

        self._build_ui()

        self.btn_delete.clicked.connect(self._disable_selected_item)

        self._load_data()

    # ---------------------------------------------------------
    # Build UI
    # ---------------------------------------------------------
    def _build_ui(self):
        layout = QVBoxLayout(self)

        # -------------------------
        # Toolbar (Add / Edit / Delete)
        # -------------------------
        toolbar = QHBoxLayout()

        self.btn_add = QPushButton("Add Item")
        self.btn_edit = QPushButton("Edit Item")
        self.btn_delete = QPushButton("Disable Item")

        # Permission-aware buttons
        self.btn_add.setEnabled("inventory.create" in self.user.permissions or "*" in self.user.permissions)
        self.btn_edit.setEnabled("inventory.edit" in self.user.permissions or "*" in self.user.permissions)
        self.btn_delete.setEnabled("inventory.edit" in self.user.permissions or "*" in self.user.permissions)

        toolbar.addWidget(self.btn_add)
        toolbar.addWidget(self.btn_edit)
        toolbar.addWidget(self.btn_delete)
        toolbar.addStretch()

        layout.addLayout(toolbar)

        # -------------------------
        # Search + Filters
        # -------------------------
        filter_bar = QHBoxLayout()

        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText("Search inventory…")
        self.search_box.textChanged.connect(self._apply_filters)

        self.type_filter = QComboBox()
        self.type_filter.addItems(["All Types", "Part", "Assembly", "Tool", "Resource"])
        self.type_filter.currentIndexChanged.connect(self._apply_filters)

        self.status_filter = QComboBox()
        self.status_filter.addItems(["All Status", "Active", "Disabled", "Discontinued"])
        self.status_filter.currentIndexChanged.connect(self._apply_filters)

        self.makebuy_filter = QComboBox()
        self.makebuy_filter.addItems(["All", "Make", "Buy"])
        self.makebuy_filter.currentIndexChanged.connect(self._apply_filters)

        filter_bar.addWidget(QLabel("Search:"))
        filter_bar.addWidget(self.search_box)
        filter_bar.addWidget(QLabel("Type:"))
        filter_bar.addWidget(self.type_filter)
        filter_bar.addWidget(QLabel("Status:"))
        filter_bar.addWidget(self.status_filter)
        filter_bar.addWidget(QLabel("Make/Buy:"))
        filter_bar.addWidget(self.makebuy_filter)
        filter_bar.addStretch()

        layout.addLayout(filter_bar)

        # -------------------------
        # Table
        # -------------------------
        self.table = QTableView()
        self.table.setSortingEnabled(True)

        # Proxy model for search + filters
        from ui.models.inventory_filter_proxy import InventoryFilterProxyModel 
        self.proxy = InventoryFilterProxyModel()

        self.proxy.setFilterCaseSensitivity(Qt.CaseInsensitive)
        self.proxy.setFilterKeyColumn(-1)  # search all columns

        self.table.setModel(self.proxy)

        layout.addWidget(self.table)

    # ---------------------------------------------------------
    # Load data (placeholder for now)
    # ---------------------------------------------------------
    def _load_data(self):
        """
        For now, this loads an empty model.
        Later we will plug in InventoryTableModel.
        """
        from PySide6.QtGui import QStandardItemModel, QStandardItem

        model = QStandardItemModel()
        model.setHorizontalHeaderLabels([
            "SKU", "Name", "Type", "Category", "Make/Buy",
            "Supplier", "Stock", "Purchase Cost", "Sell Cost", "Status"
        ])

        # Placeholder row (so you can see the table working)
        placeholder = [
            "ABC123", "Example Item", "Part", "Components", "Buy",
            "Supplier A", "120", "12.50", "19.99", "Active"
        ]
        row_items = []
        for col, value in enumerate(placeholder):
            item = QStandardItem(value)
            if col == 0:
                # Store MongoDB _id in UserRole
                item.setData("PLACEHOLDER-ID", Qt.UserRole)
            row_items.append(item)

        model.appendRow(row_items)


        self.proxy.setSourceModel(model)

    # ---------------------------------------------------------
    # Apply search + filters
    # ---------------------------------------------------------
    
    def _apply_filters(self):
        self.proxy.set_filters(
            self.search_box.text().strip(),
            self.type_filter.currentText(),
            self.status_filter.currentText(),
            self.makebuy_filter.currentText()
        )

    # def _apply_filters(self):
    #     search_text = self.search_box.text().strip().lower()
    #     type_filter = self.type_filter.currentText()
    #     status_filter = self.status_filter.currentText()
    #     makebuy_filter = self.makebuy_filter.currentText()

    #     def filter_accepts(row, parent):
    #         model = self.proxy.sourceModel()
    #         if model is None:
    #             return True

    #         # Extract row data
    #         row_data = [model.index(row, col).data() for col in range(model.columnCount())]

    #         # Search filter
    #         if search_text:
    #             if not any(search_text in str(cell).lower() for cell in row_data):
    #                 return False

    #         # Type filter
    #         if type_filter != "All Types":
    #             if row_data[2] != type_filter:
    #                 return False

    #         # Status filter
    #         if status_filter != "All Status":
    #             if row_data[9] != status_filter:
    #                 return False
                

    #         # Make/Buy filter
    #         if makebuy_filter != "All":
    #             if row_data[4] != makebuy_filter:
    #                 return False

    #         return True

    #     self.proxy.setFilterAcceptsRow(filter_accepts)

    def _disable_selected_item(self):
        # Get selected row
        selection = self.table.selectionModel().selectedRows()
        if not selection:
            self.app.show_error("Please select an item to disable.")
            return

        index = selection[0]
        source_index = self.proxy.mapToSource(index)
        model = self.proxy.sourceModel()

        sku = model.index(source_index.row(), 0).data()
        item_id = model.index(source_index.row(), 0).data(Qt.UserRole)  # we will set this later

        # Confirmation dialog
        from PySide6.QtWidgets import QMessageBox
        confirm = QMessageBox.question(
            self,
            "Disable Item",
            f"Are you sure you want to disable item '{sku}'?",
            QMessageBox.Yes | QMessageBox.No
        )

        if confirm != QMessageBox.Yes:
            return

        # Perform disable
        try:
            self.mongo.inventory.update_one(
                {"_id": item_id},
                {"$set": {"status": "Disabled"}}
            )

            # Audit log
            self.mongo.log_event(
                "inventory.disable",
                performed_by=self.user.username,
                details=f"Disabled inventory item {sku}"
            )

            log_event("info", "Inventory item disabled",
                    user=self.user.username, sku=sku)

            self._load_data()  # refresh table

        except Exception as e:
            log_event("error", "Failed to disable inventory item",
                    user=self.user.username, error=str(e))
            self.app.show_error(f"Failed to disable item: {e}")

