from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QTableView, QDialog, QFormLayout, QLineEdit, QComboBox, QDialogButtonBox
)
from PySide6.QtCore import Qt, QAbstractTableModel, QModelIndex
from bson import ObjectId


class StoresTableModel(QAbstractTableModel):
    def __init__(self, stores):
        super().__init__()
        self.stores = stores
        self.headers = ["Name", "Type", "Status"]

    def rowCount(self, parent=None):
        return len(self.stores)

    def columnCount(self, parent=None):
        return len(self.headers)

    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid():
            return None

        store = self.stores[index.row()]
        col = index.column()

        if role == Qt.DisplayRole:
            if col == 0: return store.get("name", "")
            if col == 1: return store.get("type", "")
            if col == 2: return store.get("status", "")

        if role == Qt.UserRole:
            return store["_id"]

        return None

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if role == Qt.DisplayRole and orientation == Qt.Horizontal:
            return self.headers[section]
        return None


class StoreDialog(QDialog):
    def __init__(self, mongo, store=None, parent=None):
        super().__init__(parent)
        self.mongo = mongo
        self.store = store

        self.setWindowTitle("Edit Store" if store else "New Store")

        layout = QFormLayout(self)

        self.name_edit = QLineEdit()
        self.type_combo = QComboBox()
        self.type_combo.addItems(["Internal", "Customer"])

        self.status_combo = QComboBox()
        self.status_combo.addItems(["Active", "Inactive"])

        layout.addRow("Name", self.name_edit)
        layout.addRow("Type", self.type_combo)
        layout.addRow("Status", self.status_combo)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addRow(buttons)

        if store:
            self.name_edit.setText(store.get("name", ""))
            self.type_combo.setCurrentText(store.get("type", "Internal"))
            self.status_combo.setCurrentText(store.get("status", "Active"))

    def get_data(self):
        return {
            "name": self.name_edit.text().strip(),
            "type": self.type_combo.currentText(),
            "status": self.status_combo.currentText(),
            # customer_id will be wired later when Customers module exists
            "customer_id": self.store.get("customer_id") if self.store else None,
        }


class StoresListPage(QWidget):
    def __init__(self, mongo, user, parent=None):
        super().__init__(parent)
        self.mongo = mongo
        self.user = user

        self.setWindowTitle("Stores")

        layout = QVBoxLayout(self)

        # Toolbar
        toolbar = QHBoxLayout()
        self.btn_add = QPushButton("Add")
        self.btn_edit = QPushButton("Edit")
        self.btn_delete = QPushButton("Delete")

        toolbar.addWidget(self.btn_add)
        toolbar.addWidget(self.btn_edit)
        toolbar.addWidget(self.btn_delete)
        toolbar.addStretch()
        layout.addLayout(toolbar)

        # Table
        self.table = QTableView()
        layout.addWidget(self.table)

        self._apply_permissions()
        self._connect_signals()
        self.load_stores()

        self.resize(700, 400)

    def _apply_permissions(self):
        perms = getattr(self.user, "permissions", [])
        can_create = "stores.create" in perms or "*" in perms
        can_update = "stores.update" in perms or "*" in perms
        can_delete = "stores.delete" in perms or "*" in perms

        self.btn_add.setEnabled(can_create)
        self.btn_edit.setEnabled(can_update)
        self.btn_delete.setEnabled(can_delete)

    def _connect_signals(self):
        self.btn_add.clicked.connect(self._add_store)
        self.btn_edit.clicked.connect(self._edit_store)
        self.btn_delete.clicked.connect(self._delete_store)

    def load_stores(self):
        stores = list(self.mongo.stores.find().sort("name", 1))
        self.model = StoresTableModel(stores)
        self.table.setModel(self.model)
        self.table.setSelectionBehavior(QTableView.SelectRows)
        self.table.setSelectionMode(QTableView.SingleSelection)
        self.table.resizeColumnsToContents()

    def _get_selected_store_id(self):
        selection = self.table.selectionModel().selectedRows()
        if not selection:
            return None
        index = selection[0]
        return self.model.data(index, Qt.UserRole)

    def _add_store(self):
        dlg = StoreDialog(self.mongo, parent=self)
        if dlg.exec() == QDialog.Accepted:
            data = dlg.get_data()
            if not data["name"]:
                self.window().show_error("Store name is required.")
                return
            self.mongo.stores.insert_one(data)
            self.load_stores()

    def _edit_store(self):
        store_id = self._get_selected_store_id()
        if not store_id:
            self.window().show_error("Please select a store first.")
            return

        store = self.mongo.stores.find_one({"_id": store_id})
        dlg = StoreDialog(self.mongo, store, parent=self)
        if dlg.exec() == QDialog.Accepted:
            data = dlg.get_data()
            if not data["name"]:
                self.window().show_error("Store name is required.")
                return
            self.mongo.stores.update_one({"_id": store_id}, {"$set": data})
            self.load_stores()

    def _delete_store(self):
        store_id = self._get_selected_store_id()
        if not store_id:
            self.window().show_error("Please select a store first.")
            return

        # TODO: add safety check: prevent delete if batches exist for this store
        self.mongo.stores.delete_one({"_id": store_id})
        self.load_stores()
