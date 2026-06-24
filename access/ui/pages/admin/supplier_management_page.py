from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QMessageBox, QHeaderView
)
from PySide6.QtCore import Qt

from ui.components.logger_utils import log_event


class SupplierManagementPage(QWidget):
    def __init__(self, mongo, user, parent=None):
        super().__init__(parent)

        self.mongo = mongo
        self.user = user

        self._build_ui()
        self._load_data()

    # ---------------------------------------------------------
    # Build UI
    # ---------------------------------------------------------
    def _build_ui(self):
        layout = QVBoxLayout(self)

        title = QLabel("Manage Suppliers")
        title.setStyleSheet("font-size: 18px; font-weight: bold;")
        layout.addWidget(title)

        # Table
        self.table = QTableWidget(0, 8)
        self.table.setHorizontalHeaderLabels([
            "Name", "Contact Name", "Email", "Phone",
            "City", "Postcode", "Country", "Notes"
        ])


        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(4, QHeaderView.Stretch)

        layout.addWidget(self.table)   # ⭐⭐ THIS WAS MISSING ⭐⭐

        self.table.cellDoubleClicked.connect(self._view_supplier)


        # Buttons
        btn_row = QHBoxLayout()
        self.btn_add = QPushButton("Add Supplier")
        self.btn_edit = QPushButton("Edit Selected")
        self.btn_delete = QPushButton("Delete Selected")
        self.btn_view = QPushButton("View Details")




        self.btn_add.clicked.connect(self._add_supplier)
        self.btn_edit.clicked.connect(self._edit_supplier)
        self.btn_delete.clicked.connect(self._delete_supplier)
        self.btn_view.clicked.connect(self._view_supplier)

        btn_row.addStretch()
        btn_row.addWidget(self.btn_add)
        btn_row.addWidget(self.btn_edit)
        btn_row.addWidget(self.btn_delete)
        btn_row.addWidget(self.btn_view)

        layout.addLayout(btn_row)


    # ---------------------------------------------------------
    # Load data
    # ---------------------------------------------------------
    def _load_data(self):
        self.table.setRowCount(0)

        suppliers = list(self.mongo.suppliers.find().sort("name", 1))

        for row_idx, s in enumerate(suppliers):
            self.table.insertRow(row_idx)

            def cell(value):
                return QTableWidgetItem(value if value else "")

            self.table.setItem(row_idx, 0, cell(s.get("name")))
            self.table.setItem(row_idx, 1, cell(s.get("contact_name")))
            self.table.setItem(row_idx, 2, cell(s.get("email")))
            self.table.setItem(row_idx, 3, cell(s.get("phone")))
            self.table.setItem(row_idx, 4, cell(s.get("city")))
            self.table.setItem(row_idx, 5, cell(s.get("postcode")))
            self.table.setItem(row_idx, 6, cell(s.get("country")))
            self.table.setItem(row_idx, 7, cell(s.get("notes")))


    # ---------------------------------------------------------
    # Add Supplier
    # ---------------------------------------------------------
    def _add_supplier(self):
        from ui.pages.admin.supplier_dialogs import AddSupplierDialog

        dlg = AddSupplierDialog(self.mongo, self.user, self)
        if dlg.exec():
            self._load_data()

    # ---------------------------------------------------------
    # Edit Supplier
    # ---------------------------------------------------------
    def _edit_supplier(self):
        row = self.table.currentRow()
        if row < 0:
            QMessageBox.warning(self, "No Selection", "Please select a supplier to edit.")
            return

        name = self.table.item(row, 0).text()

        from ui.pages.admin.supplier_dialogs import EditSupplierDialog

        dlg = EditSupplierDialog(self.mongo, self.user, name, self)
        if dlg.exec():
            self._load_data()

    # ---------------------------------------------------------
    # Delete Supplier
    # ---------------------------------------------------------
    def _delete_supplier(self):
        row = self.table.currentRow()
        if row < 0:
            QMessageBox.warning(self, "No Selection", "Please select a supplier to delete.")
            return

        name = self.table.item(row, 0).text()

        # Prevent deleting suppliers in use
        in_use = self.mongo.inventory.find_one({"supplier": name})
        if in_use:
            QMessageBox.warning(
                self,
                "In Use",
                f"Supplier '{name}' is used by inventory items and cannot be deleted."
            )
            return

        confirm = QMessageBox.question(
            self,
            "Confirm Delete",
            f"Delete supplier '{name}'?"
        )

        if confirm != QMessageBox.Yes:
            return

        try:
            self.mongo.suppliers.delete_one({"name": name})

            self.mongo.log_event(
                "supplier.delete",
                performed_by=self.user.username,
                details=f"Deleted supplier '{name}'"
            )

            log_event("info", "Supplier deleted", user=self.user.username, supplier=name)

            self._load_data()

        except Exception as e:
            log_event("error", "Failed to delete supplier",
                      user=self.user.username, supplier=name, error=str(e))
            QMessageBox.critical(self, "Error", f"Failed to delete supplier:\n{e}")

    def _view_supplier(self):
        row = self.table.currentRow()
        if row < 0:
            QMessageBox.warning(self, "No Selection", "Please select a supplier to view.")
            return

        name = self.table.item(row, 0).text()

        from ui.pages.admin.supplier_dialogs import ViewSupplierDialog
        dlg = ViewSupplierDialog(self.mongo, name, self)
        dlg.exec()
