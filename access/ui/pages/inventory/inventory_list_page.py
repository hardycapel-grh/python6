from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLineEdit,
    QLabel, QComboBox, QTableView
)
from PySide6.QtCore import Qt

from ui.components.logger_utils import log_event
from bson import ObjectId


class InventoryListPage(QWidget):
    def __init__(self, user, mongo, parent=None):
        super().__init__(parent)

        self.user = user
        self.mongo = mongo
        self.app = parent

        log_event("info", "InventoryListPage initialized", user=user.username)

        self._build_ui()

        self.btn_add.clicked.connect(self._open_add_dialog)
        self.btn_delete.clicked.connect(self._disable_selected_item)
        self.btn_receive.clicked.connect(self._open_receive_stock_dialog)
        self.btn_batches.clicked.connect(self._open_batch_list)
        self.btn_edit.clicked.connect(self._open_edit_dialog)
        self.btn_move.clicked.connect(self._open_move_dialog)


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
        self.btn_receive = QPushButton("Receive Stock")
        self.btn_batches = QPushButton("View Batches")
        self.btn_move = QPushButton("Move Stock")








        # Permission-aware buttons
        self.btn_add.setEnabled("inventory.create" in self.user.permissions or "*" in self.user.permissions)
        self.btn_edit.setEnabled("inventory.edit" in self.user.permissions or "*" in self.user.permissions)
        self.btn_delete.setEnabled("inventory.edit" in self.user.permissions or "*" in self.user.permissions)
        self.btn_receive.setEnabled("inventory.receive" in self.user.permissions or "*" in self.user.permissions)
        self.btn_batches.setEnabled("inventory.batches.read" in self.user.permissions or "*" in self.user.permissions)
        self.btn_move.setEnabled("inventory.move" in self.user.permissions or "*" in self.user.permissions)



        toolbar.addWidget(self.btn_add)
        toolbar.addWidget(self.btn_edit)
        toolbar.addWidget(self.btn_delete)
        toolbar.addWidget(self.btn_receive)
        toolbar.addWidget(self.btn_batches)
        toolbar.addWidget(self.btn_move)
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
        from PySide6.QtGui import QStandardItemModel, QStandardItem

        model = QStandardItemModel()
        model.setHorizontalHeaderLabels([
            "Part Number",
            "Description",
            "Revision",
            "Type",
            "UOM",
            "Category",
            "Make/Buy",
            "Supplier",
            "Status",
            "Store Type",
            "Customer",
            "Ownership",
            "Store",
            "Location"
        ])


        # Load all items from MongoDB
        items = list(self.mongo.inventory.find({}))

        for item in items:
            row_items = []

            fields = [
                item.get("part_number", ""),
                item.get("description", ""),
                item.get("revision", ""),
                item.get("type", ""),
                item.get("uom", ""),
                item.get("category", ""),
                item.get("make_buy", ""),
                item.get("supplier", ""),
                item.get("status", ""),
                item.get("store_type", ""),
                item.get("customer", ""),
                item.get("ownership", ""),
                item.get("store_name", ""),
                item.get("store_location_name", "")
            ]


            for col, value in enumerate(fields):
                cell = QStandardItem(str(value))
                if col == 0:
                    # Store MongoDB _id in UserRole for disable/edit
                    cell.setData(item["_id"], Qt.UserRole)
                row_items.append(cell)

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


    def _disable_selected_item(self):
        # Get selected row
        selection = self.table.selectionModel().selectedRows()
        if not selection:
            self.window().show_error("Please select an item first.")
            return

        index = selection[0]
        source_index = self.proxy.mapToSource(index)
        model = self.proxy.sourceModel()

        part_number = model.index(source_index.row(), 0).data()
        item_id = model.index(source_index.row(), 0).data(Qt.UserRole)  # we will set this later

        # Confirmation dialog
        from PySide6.QtWidgets import QMessageBox
        confirm = QMessageBox.question(
            self,
            "Disable Item",
            f"Are you sure you want to disable item '{part_number}'?",
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
                details=f"Disabled inventory item {part_number}"
            )

            log_event("info", "Inventory item disabled",
                    user=self.user.username, part_number=part_number)

            self._load_data()  # refresh table

        except Exception as e:
            log_event("error", "Failed to disable inventory item",
                    user=self.user.username, error=str(e))
            self.window().show_error("Please select an item first.")

    def _open_add_dialog(self):
        from ui.pages.inventory.add_item_dialog import AddItemDialog
        dlg = AddItemDialog(self.mongo, self.user, self)
        if dlg.exec():
            self._load_data()

    def _open_receive_stock_dialog(self):
        selection = self.table.selectionModel().selectedRows()
        if not selection:
            self.window().show_error("Please select an item first.")
            return

        index = selection[0]
        source_index = self.proxy.mapToSource(index)
        model = self.proxy.sourceModel()

        item_id = model.index(source_index.row(), 0).data(Qt.UserRole)
        item = self.mongo.inventory.find_one({"_id": item_id})

        from ui.pages.inventory.receive_stock_dialog import ReceiveStockDialog
        dlg = ReceiveStockDialog(self.mongo, self.user, item, self)
        if dlg.exec():
            self.window().show_info("Stock received successfully.")



    def _open_batch_list(self):
        import ui.pages.inventory.batch_list_page as blp
        import inspect


        import ui.pages.inventory.batch_list_page as blp



        try:
            from ui.pages.inventory.batch_list_page import BatchListPage

        except Exception as e:

            return



        selection = self.table.selectionModel().selectedRows()


        if not selection:
            self.window().show_error("Please select an item first.")
            return

        index = selection[0]


        source_index = self.proxy.mapToSource(index)


        model = self.proxy.sourceModel()


        try:
            item_id = model.index(source_index.row(), 0).data(Qt.UserRole)

        except Exception as e:

            self.window().show_error(f"Failed to get item ID: {e}")
            return

        # ⭐ THIS MUST BE HERE — otherwise 'item' does not exist
        item = self.mongo.inventory.find_one({"_id": ObjectId(item_id)})


        if not item:

            self.window().show_error("Item not found in database.")
            return

        # Test import
        try:
            from ui.pages.inventory.batch_list_page import BatchListPage

        except Exception as e:

            self.window().show_error(f"Import failed: {e}")
            return


        self.batch_window = BatchListPage(self.mongo, item)

        self.batch_window.show()

    def _open_edit_dialog(self):
        selection = self.table.selectionModel().selectedRows()
        if not selection:
            self.window().show_error("Please select an item first.")
            return

        index = selection[0]
        source_index = self.proxy.mapToSource(index)
        model = self.proxy.sourceModel()

        item_id = model.index(source_index.row(), 0).data(Qt.UserRole)
        item = self.mongo.inventory.find_one({"_id": item_id})

        from ui.pages.inventory.edit_item_dialog import EditItemDialog
        dlg = EditItemDialog(self.mongo, self.user, item, self)

        if dlg.exec():
            updated = dlg.get_updated_values()

            self.mongo.inventory.update_one(
                {"_id": item_id},
                {"$set": updated}
            )

            self.mongo.log_event(
                "inventory.edit",
                performed_by=self.user.username,
                details=f"Edited inventory item {item.get('part_number')}"
            )

            self._load_data()

    def _open_move_dialog(self):
        selection = self.table.selectionModel().selectedRows()
        if not selection:
            self.window().show_error("Please select an item first.")
            return

        index = selection[0]
        source_index = self.proxy.mapToSource(index)
        model = self.proxy.sourceModel()

        item_id = model.index(source_index.row(), 0).data(Qt.UserRole)
        item = self.mongo.inventory.find_one({"_id": item_id})

        from ui.pages.inventory.stock_movement_dialog import StockMovementDialog
        dlg = StockMovementDialog(self.mongo, self.user, item, self)

        if dlg.exec():
            self.window().show_info("Stock moved successfully.")
