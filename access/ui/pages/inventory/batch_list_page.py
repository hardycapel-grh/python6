from PySide6.QtWidgets import (
    QHeaderView, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QTableView, QSizePolicy, QDialog, QTextEdit, QMenu, QLineEdit, QComboBox, QMessageBox, QDateEdit, QCheckBox
)
from PySide6.QtCore import Qt, QAbstractTableModel, QModelIndex, QSortFilterProxyModel, QDate
from PySide6.QtGui import QColor, QBrush, QAction
from datetime import datetime






class BatchTableModel(QAbstractTableModel):
    def __init__(self, batches):
        super().__init__()
        self.batches = batches

        # Column → field mapping
        self.columns = [
            ("GRN Number", "grn_number"),
            ("Batch Number", "batch_number"),
            ("Quantity", "quantity"),
            ("Unit Cost", "unit_cost"),
            ("Expiry Date", "expiry_date"),
            ("Store", "store_name"),
            ("Received Date", "received_date"),
            ("Days Until Expiry", "days_until_expiry"),
        ]
        

    def rowCount(self, parent=None):
        return len(self.batches)

    def columnCount(self, parent=None):
        return len(self.columns)

    def data(self, index, role):
        if not index.isValid():
            return None

        field = self.columns[index.column()][1]
        value = self.batches[index.row()].get(field, "")

        # Display formatting
        if role == Qt.DisplayRole:
            if field == "days_until_expiry":
                expiry_value = self.batches[index.row()].get("expiry_date", "")
                return self._days_until_expiry(expiry_value)
            return self._format_value(field, value)

        # Alignment
        if role == Qt.TextAlignmentRole:
            if field in ("quantity", "unit_cost"):
                return Qt.AlignRight | Qt.AlignVCenter
            if field in ("expiry_date", "received_date"):
                return Qt.AlignCenter
            if field == "days_until_expiry":
                return Qt.AlignCenter

            return Qt.AlignLeft | Qt.AlignVCenter

        # Background colour for expiry date
    
        if role == Qt.BackgroundRole:
            # Colour for expiry date and days-until-expiry use the same status
            if field in ("expiry_date", "days_until_expiry"):
                expiry_value = self.batches[index.row()].get("expiry_date", "")
                status = self._expiry_status(expiry_value)

                if status == "expired":
                    return QBrush(QColor("#ffcccc"))   # soft red
                if status == "soon":
                    return QBrush(QColor("#fff2cc"))   # soft amber
                if status == "ok":
                    return QBrush(QColor("#d9f7be"))   # soft green

                return QBrush(QColor("#e0e0e0"))       # invalid/missing

            return None



    def flags(self, index):
        return Qt.ItemIsSelectable | Qt.ItemIsEnabled




    def headerData(self, section, orientation, role):
        if role == Qt.DisplayRole and orientation == Qt.Horizontal:
            return self.columns[section][0]
        return None

    def sort(self, column, order):
        field = self.columns[column][1]
        reverse = (order == Qt.DescendingOrder)

        self.layoutAboutToBeChanged.emit()


        self.batches.sort(
            key=lambda batch: self._sort_key(field, batch),
            reverse=reverse
        )



        self.layoutChanged.emit()



    def _sort_key(self, field, batch):
        value = batch.get(field, "")

        # Numeric fields
        if field in ("quantity", "unit_cost"):
            try:
                return float(value)
            except:
                return 0

        # Days Until Expiry (numeric)
        if field == "days_until_expiry":
            expiry_value = batch.get("expiry_date", "")
            return self._days_until_expiry_numeric(expiry_value)

        # Date fields
        if field in ("expiry_date", "received_date"):
            from datetime import datetime
            for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%Y/%m/%d"):
                try:
                    return datetime.strptime(value, fmt)
                except:
                    pass
            return datetime.min

        # Default: string
        return str(value).lower()



    def _format_value(self, field, value):
        # Numeric formatting
        if field == "quantity":
            try:
                return f"{int(value)}"
            except:
                return value

        if field == "unit_cost":
            try:
                return f"£{float(value):,.2f}"
            except:
                return value

        # Date formatting
        if field in ("expiry_date", "received_date"):
            from datetime import datetime
            for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%Y/%m/%d"):
                try:
                    dt = datetime.strptime(value, fmt)
                    return dt.strftime("%d %b %Y")  # e.g., 05 Jun 2026
                except:
                    pass
            return value

        # Default: string
        return str(value)

    def _expiry_status(self, value):
        from datetime import datetime, timedelta

        if not value:
            return "invalid"

        # If it's already a datetime
        if isinstance(value, datetime):
            dt = value
        else:
            dt = None
            s = str(value)
            for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%Y/%m/%d"):
                try:
                    dt = datetime.strptime(s, fmt)
                    break
                except:
                    continue

        if not dt:
            return "invalid"

        today = datetime.today()

        if dt < today:
            return "expired"

        if dt <= today + timedelta(days=30):
            return "soon"

        return "ok"
    
    def _days_until_expiry(self, value):
        from datetime import datetime

        # Parse date
        dt = None
        for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%Y/%m/%d"):
            try:
                dt = datetime.strptime(value, fmt)
                break
            except:
                continue

        if not dt:
            return "Invalid"

        today = datetime.today()
        delta = (dt - today).days

        if delta < 0:
            return f"Expired {abs(delta)} days ago"
        if delta == 0:
            return "Expires today"
        return f"In {delta} days"
    
    def _days_until_expiry_numeric(self, value):
        from datetime import datetime

        # Parse date
        dt = None
        for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%Y/%m/%d"):
            try:
                dt = datetime.strptime(value, fmt)
                break
            except:
                continue

        if not dt:
            return 999999  # invalid dates go to bottom

        today = datetime.today()
        return (dt - today).days



class EditBatchDialog(QDialog):
    def __init__(self, batch, stores, parent=None):
        super().__init__(parent)
        self.batch = batch
        self.stores = stores

        self.setWindowTitle("Edit Batch")
        self.setMinimumWidth(400)

        layout = QVBoxLayout(self)

        # Quantity
        self.qty = QLineEdit(str(batch.get("quantity", "")))
        layout.addWidget(QLabel("Quantity"))
        layout.addWidget(self.qty)

        # Unit Cost
        self.cost = QLineEdit(str(batch.get("unit_cost", "")))
        layout.addWidget(QLabel("Unit Cost"))
        layout.addWidget(self.cost)

        # Expiry Date
        layout.addWidget(QLabel("Expiry Date"))

        self.expiry = QDateEdit()
        self.expiry.setCalendarPopup(True)
        self.expiry.setDisplayFormat("yyyy-MM-dd")
        layout.addWidget(self.expiry)

        

        layout.addWidget(QLabel("Received Date"))

        self.received = QDateEdit()
        self.received.setCalendarPopup(True)
        self.received.setDisplayFormat("yyyy-MM-dd")
        layout.addWidget(self.received)

        layout.addWidget(QLabel("Expiry Date"))

        self.expiry = QDateEdit()
        self.expiry.setCalendarPopup(True)
        self.expiry.setDisplayFormat("yyyy-MM-dd")
        layout.addWidget(self.expiry)

        # Add "No expiry" checkbox
        self.no_expiry = QCheckBox("No expiry date")
        layout.addWidget(self.no_expiry)
        self.no_expiry.toggled.connect(lambda checked: self.expiry.setEnabled(not checked))


        # Pre-fill received date
        raw_received = batch.get("received_date", "")
        dt_received = self._parse_date(raw_received)
        if dt_received:
            self.received.setDate(dt_received)
        else:
            self.received.setDate(QDate.currentDate())

        self.received.setMaximumDate(QDate.currentDate())
        self.expiry.setMinimumDate(QDate.currentDate())
        self.expiry.setMaximumDate(QDate.currentDate().addYears(10))

        # Pre-fill the date
        raw = batch.get("expiry_date", "")
        dt = self._parse_date(raw)

        if dt:
            self.expiry.setDate(dt)
            self.no_expiry.setChecked(False)
            self.expiry.setEnabled(True)
        else:
            self.no_expiry.setChecked(True)
            self.expiry.setEnabled(False)
            self.expiry.setDate(QDate.currentDate())



        # Store dropdown
        self.store = QComboBox()
        self.store.addItems([s["name"] for s in stores.values()])
        current_store = batch.get("store_name")
        if current_store in [s["name"] for s in stores.values()]:
            self.store.setCurrentText(current_store)

        layout.addWidget(QLabel("Store"))
        layout.addWidget(self.store)

        # Buttons
        btn_row = QHBoxLayout()
        btn_cancel = QPushButton("Cancel")
        btn_save = QPushButton("Save")
        btn_save.setStyleSheet("background-color: #0275d8; color: white;")

        btn_cancel.clicked.connect(self.reject)
        btn_save.clicked.connect(self._validate_and_accept)

        btn_row.addStretch()
        btn_row.addWidget(btn_cancel)
        btn_row.addWidget(btn_save)
        layout.addLayout(btn_row)

    # -------------------------
    # VALIDATION LOGIC
    # -------------------------
    def _validate_and_accept(self):
        from datetime import datetime

        # Validate quantity
        try:
            qty = int(self.qty.text())
            if qty < 0:
                raise ValueError
        except:
            QMessageBox.warning(self, "Invalid Quantity",
                                "Quantity must be a non-negative integer.")
            return

        # Validate unit cost
        try:
            cost = float(self.cost.text())
            if cost < 0:
                raise ValueError
        except:
            QMessageBox.warning(self, "Invalid Unit Cost",
                                "Unit cost must be a non-negative number.")
            return

        # Dates from pickers
        received_qdate = self.received.date()

        # Rule: Received cannot be in the future
        if received_qdate > QDate.currentDate():
            QMessageBox.warning(self, "Invalid Received Date",
                                "Received date cannot be in the future.")
            return

        # Handle "No expiry"
        if self.no_expiry.isChecked():
            self._validated_expiry = ""
        else:
            expiry_qdate = self.expiry.date()

            # Rule: Expiry cannot be before received
            if expiry_qdate < received_qdate:
                QMessageBox.warning(self, "Invalid Dates",
                                    "Expiry date cannot be before the received date.")
                return

            self._validated_expiry = expiry_qdate.toString("yyyy-MM-dd")

        # Store validated received date
        self._validated_received = received_qdate.toString("yyyy-MM-dd")

        self.accept()





    # -------------------------
    # RETURN CLEAN VALUES
    # -------------------------
    def get_updated_values(self):
        return {
            "quantity": int(self.qty.text()),
            "unit_cost": float(self.cost.text()),
            "expiry_date": self._validated_expiry,
            "received_date": self._validated_received,
            "store_name": self.store.currentText(),
        }

    
    def _parse_date(self, value):
        if not value:
            return None

        for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%Y/%m/%d"):
            try:
                from datetime import datetime
                dt = datetime.strptime(value, fmt)
                return QDate(dt.year, dt.month, dt.day)
            except:
                continue

        return None
    
class StockAdjustmentDialog(QDialog):
    def __init__(self, batch, parent=None):
        super().__init__(parent)
        self.batch = batch

        self.setWindowTitle("Adjust Stock")
        self.setMinimumWidth(350)

        layout = QVBoxLayout(self)

        layout.addWidget(QLabel(
            f"Batch: {batch.get('batch_number')} (Current Qty: {batch.get('quantity')})"
        ))

        # Adjustment type
        layout.addWidget(QLabel("Adjustment Type"))
        self.type_box = QComboBox()
        self.type_box.addItems(["Increase", "Decrease"])
        layout.addWidget(self.type_box)

        # Quantity
        layout.addWidget(QLabel("Quantity"))
        self.qty_edit = QLineEdit()
        layout.addWidget(self.qty_edit)

        # Reason
        layout.addWidget(QLabel("Reason"))
        self.reason_box = QComboBox()
        self.reason_box.addItems([
            "Stock Take Correction",
            "Damaged",
            "Lost",
            "Expired",
            "Administrative Correction",
            "Other"
        ])
        layout.addWidget(self.reason_box)

        # Notes
        layout.addWidget(QLabel("Notes (optional)"))
        self.notes_edit = QLineEdit()
        layout.addWidget(self.notes_edit)

        # Buttons
        btn_row = QHBoxLayout()
        btn_cancel = QPushButton("Cancel")
        btn_apply = QPushButton("Apply")
        btn_apply.setStyleSheet("background-color: #0275d8; color: white;")

        btn_cancel.clicked.connect(self.reject)
        btn_apply.clicked.connect(self._validate_and_accept)

        btn_row.addStretch()
        btn_row.addWidget(btn_cancel)
        btn_row.addWidget(btn_apply)
        layout.addLayout(btn_row)

    def _validate_and_accept(self):
        try:
            qty = int(self.qty_edit.text())
            if qty <= 0:
                raise ValueError
        except:
            QMessageBox.warning(self, "Invalid Quantity",
                                "Quantity must be a positive integer.")
            return

        self.adjust_type = self.type_box.currentText()
        self.adjust_qty = qty
        self.reason = self.reason_box.currentText()
        self.notes = self.notes_edit.text()

        self.accept()

    def get_adjustment(self):
        return {
            "type": self.adjust_type,
            "qty": self.adjust_qty,
            "reason": self.reason,
            "notes": self.notes
        }



class BatchFilterProxy(QSortFilterProxyModel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.mode = "all"
        self.model_ref = None  # we will set this later

    def setFilterMode(self, mode):
        self.mode = mode
        self.invalidateFilter()

    def filterAcceptsRow(self, source_row, source_parent):
        if self.mode == "all":
            return True

        batch = self.model_ref.batches[source_row]
        status = self.model_ref._expiry_status(batch.get("expiry_date", ""))

        if self.mode == "expired":
            return status == "expired"
        if self.mode == "soon":
            return status == "soon"
        if self.mode == "ok":
            return status == "ok"

        return True


class BatchListPage(QWidget):
    def __init__(self, mongo, item, parent=None):
        super().__init__(parent)

        self.mongo = mongo
        self.item = item

        self.setWindowTitle(f"Batches — {item['part_number']}")
        self.setMinimumSize(600, 400)
        self.resize(900, 500)

        layout = QVBoxLayout(self)

        title = QLabel(f"Batches for {item['part_number']} Rev {item.get('revision', '')} — {item['description']}")

        title.setStyleSheet("font-size: 18px; font-weight: bold;")
        layout.addWidget(title)
        filter_row = QHBoxLayout()

        btn_all = QPushButton("All")
        btn_expired = QPushButton("Expired")
        btn_soon = QPushButton("Expiring Soon")
        btn_ok = QPushButton("Valid")

        btn_all.clicked.connect(lambda: self._apply_filter("all"))
        btn_expired.clicked.connect(lambda: self._apply_filter("expired"))
        btn_soon.clicked.connect(lambda: self._apply_filter("soon"))
        btn_ok.clicked.connect(lambda: self._apply_filter("ok"))

        filter_row.addWidget(btn_all)
        filter_row.addWidget(btn_expired)
        filter_row.addWidget(btn_soon)
        filter_row.addWidget(btn_ok)
        filter_row.addStretch()

        layout.addLayout(filter_row)

        self.table = QTableView()

        self.proxy = BatchFilterProxy(self)

        self.proxy.setFilterCaseSensitivity(Qt.CaseInsensitive)
        self.proxy.setSortCaseSensitivity(Qt.CaseInsensitive)

        self.table.setModel(self.proxy)

        self.table.setSelectionBehavior(QTableView.SelectRows)
        self.table.setSelectionMode(QTableView.SingleSelection)
        self.table.setSortingEnabled(True)

        layout.addWidget(self.table)

        # --- Add total quantity footer ---
        self.total_label = QLabel("Total Quantity: 0")
        self.total_label.setStyleSheet("font-weight: bold; padding: 6px;")
        layout.addWidget(self.total_label)


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

        self.table.setContextMenuPolicy(Qt.CustomContextMenu)
        self.table.customContextMenuRequested.connect(self._open_context_menu)


    def load_batches(self):
        stores = {s["_id"]: s for s in self.mongo.stores.find()}

        batches = list(self.mongo.inventory_batches.find(
            {"item_id": self.item["_id"]}
        ))

        for b in batches:
            store = stores.get(b.get("store_id"))
            b["store_name"] = store["name"] if store else "Unknown"

        self.model = BatchTableModel(batches)
        self.proxy.setSourceModel(self.model)
        self.proxy.model_ref = self.model



        # TEMP: print a few expiry dates
        # for b in batches[:5]:
        #     print("EXPIRY RAW:", b.get("expiry_date"))


        header = self.table.horizontalHeader()

        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(6, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(5, QHeaderView.Stretch)

        self.table.sortByColumn(6, Qt.DescendingOrder)


        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        total_qty = sum(int(b.get("quantity", 0)) for b in batches)
        self.total_label.setText(f"Total Quantity: {total_qty:,}")



    def _open_batch_details(self, index):
        source_index = self.proxy.mapToSource(index)
        row = source_index.row()
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

    def _open_context_menu(self, position):
        index = self.table.indexAt(position)
        if not index.isValid():
            return

        source_index = self.proxy.mapToSource(index)
        row = source_index.row()
        batch = self.model.batches[row]


        menu = QMenu(self)

        view_action = QAction("View Details", self)
        edit_action = QAction("Edit Batch", self)
        adjust_action = QAction("Adjust Stock", self)
        delete_action = QAction("Delete Batch", self)

        view_action.triggered.connect(lambda: self._open_batch_details(index))
        edit_action.triggered.connect(lambda: self._edit_batch(batch))
        adjust_action.triggered.connect(lambda: self._adjust_stock(batch))
        delete_action.triggered.connect(lambda: self._delete_batch(batch))

        menu.addAction(view_action)
        menu.addAction(edit_action)
        menu.addAction(adjust_action)
        menu.addAction(delete_action)

        menu.exec(self.table.viewport().mapToGlobal(position))

    def _edit_batch(self, batch):
        # Load stores for dropdown
        stores = {s["_id"]: s for s in self.mongo.stores.find()}

        dlg = EditBatchDialog(batch, stores, self)

        if dlg.exec() == QDialog.Accepted:
            updated = dlg.get_updated_values()

            # Update MongoDB
            self.mongo.inventory_batches.update_one(
                {"_id": batch["_id"]},
                {"$set": updated}
            )

            self.load_batches()


    def _delete_batch(self, batch):
        dlg = QDialog(self)
        dlg.setWindowTitle("Delete Batch")
        dlg.setMinimumWidth(350)

        layout = QVBoxLayout(dlg)

        layout.addWidget(QLabel(
            f"Are you sure you want to delete batch <b>{batch.get('batch_number')}</b>?"
        ))

        btn_row = QHBoxLayout()
        btn_cancel = QPushButton("Cancel")
        btn_delete = QPushButton("Delete")
        btn_delete.setStyleSheet("background-color: #d9534f; color: white;")

        btn_cancel.clicked.connect(dlg.reject)
        btn_delete.clicked.connect(dlg.accept)

        btn_row.addStretch()
        btn_row.addWidget(btn_cancel)
        btn_row.addWidget(btn_delete)
        layout.addLayout(btn_row)

        if dlg.exec() == QDialog.Accepted:
            # Perform delete
            self.mongo.inventory_batches.delete_one({"_id": batch["_id"]})
            self.load_batches()

    def _edit_batch(self, batch):
        # Load stores for dropdown
        stores = {s["_id"]: s for s in self.mongo.stores.find()}

        dlg = EditBatchDialog(batch, stores, self)

        if dlg.exec() == QDialog.Accepted:
            updated = dlg.get_updated_values()

            # Update MongoDB
            self.mongo.inventory_batches.update_one(
                {"_id": batch["_id"]},
                {"$set": updated}
            )

            self.load_batches()

    # def _apply_filter(self, mode):

    #     # ALL → remove custom filter and show everything
    #     if mode == "all":
    #         if hasattr(self.proxy, "_custom_filter"):
    #             del self.proxy._custom_filter

    #         # Reset to built-in behaviour
    #         self.proxy.invalidateFilter()
    #         return

    #     # Custom filtering for expired / soon / ok
    #     def filter_accepts(row, parent):
    #         batch = self.model.batches[row]
    #         status = self.model._expiry_status(batch.get("expiry_date", ""))

    #         if mode == "expired":
    #             return status == "expired"
    #         if mode == "soon":
    #             return status == "soon"
    #         if mode == "ok":
    #             return status == "ok"

    #         return True

    #     # Store custom filter function
    #     self.proxy._custom_filter = filter_accepts

    #     # Install a wrapper that Qt will call safely
    #     def wrapper(proxy, row, parent):
    #         return proxy._custom_filter(row, parent)

    #     self.proxy.filterAcceptsRow = wrapper
    #     self.proxy.invalidateFilter()

    def _apply_filter(self, mode):
        self.proxy.setFilterMode(mode)

    def _adjust_stock(self, batch):
        dlg = StockAdjustmentDialog(batch, self)

        if dlg.exec() != QDialog.Accepted:
            return

        adj = dlg.get_adjustment()
        old_qty = int(batch.get("quantity", 0))

        if adj["type"] == "Increase":
            new_qty = old_qty + adj["qty"]
        else:
            new_qty = old_qty - adj["qty"]
            if new_qty < 0:
                QMessageBox.warning(self, "Invalid Adjustment",
                                    "Stock cannot go below zero.")
                return

        # Update MongoDB
        self.mongo.inventory_batches.update_one(
            {"_id": batch["_id"]},
            {"$set": {"quantity": new_qty}}
        )

        # Audit log
        self.mongo.audit_log.insert_one({
            "event": "stock.adjust",
            "item_id": self.item["_id"],
            "batch_id": batch["_id"],
            "old_qty": old_qty,
            "new_qty": new_qty,
            "reason": adj["reason"],
            "notes": adj["notes"],
            "performed_by": "system",  # replace with logged-in user
            "timestamp": datetime.utcnow(),
        })

        self.load_batches()
