# ui/pages/admin/store_locations_page.py

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QTableWidget, QTableWidgetItem, QMessageBox
)
from PySide6.QtCore import Qt

from ui.pages.admin.dialogs.add_store_location_dialog import AddStoreLocationDialog
from ui.pages.admin.dialogs.edit_store_location_dialog import EditStoreLocationDialog


class StoreLocationsPage(QWidget):
    def __init__(self, mongo, user, parent=None):
        super().__init__(parent)
        self.mongo = mongo
        self.user = user

        self._build_ui()
        self.load_locations()

    def _build_ui(self):
        layout = QVBoxLayout(self)

        # Table
        self.table = QTableWidget(0, 3)
        self.table.setHorizontalHeaderLabels(["Location Name", "Description", "Active"])
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        layout.addWidget(self.table)

        # Buttons
        btn_row = QHBoxLayout()

        self.btn_add = QPushButton("Add Location")
        self.btn_edit = QPushButton("Edit")
        self.btn_delete = QPushButton("Delete")
        self.btn_toggle = QPushButton("Activate / Deactivate")

        self.btn_add.clicked.connect(self.add_location)
        self.btn_edit.clicked.connect(self.edit_location)
        self.btn_delete.clicked.connect(self.delete_location)
        self.btn_toggle.clicked.connect(self.toggle_active)

        btn_row.addWidget(self.btn_add)
        btn_row.addWidget(self.btn_edit)
        btn_row.addWidget(self.btn_delete)
        btn_row.addWidget(self.btn_toggle)

        layout.addLayout(btn_row)

    # ---------------------------------------------------------
    # Load locations into table
    # ---------------------------------------------------------
    def load_locations(self):
        locations = list(self.mongo.store_locations.find().sort("location_name", 1))

        self.table.setRowCount(0)

        for loc in locations:
            row = self.table.rowCount()
            self.table.insertRow(row)

            self.table.setItem(row, 0, QTableWidgetItem(loc.get("location_name", "")))
            self.table.setItem(row, 1, QTableWidgetItem(loc.get("description", "")))
            self.table.setItem(row, 2, QTableWidgetItem("Yes" if loc.get("is_active", True) else "No"))

            # Store the full document for easy access
            self.table.setRowHeight(row, 28)
            self.table.item(row, 0).setData(Qt.UserRole, loc)

    # ---------------------------------------------------------
    # Helpers
    # ---------------------------------------------------------
    def _get_selected_location(self):
        row = self.table.currentRow()
        if row < 0:
            QMessageBox.warning(self, "No Selection", "Please select a location.")
            return None

        return self.table.item(row, 0).data(Qt.UserRole)

    # ---------------------------------------------------------
    # Add
    # ---------------------------------------------------------
    def add_location(self):
        dlg = AddStoreLocationDialog(self.mongo, self.user, self)
        if dlg.exec():
            self.load_locations()

    # ---------------------------------------------------------
    # Edit
    # ---------------------------------------------------------
    def edit_location(self):
        loc = self._get_selected_location()
        if not loc:
            return

        dlg = EditStoreLocationDialog(self.mongo, self.user, loc, self)
        if dlg.exec():
            self.load_locations()

    # ---------------------------------------------------------
    # Delete
    # ---------------------------------------------------------
    def delete_location(self):
        loc = self._get_selected_location()
        if not loc:
            return

        confirm = QMessageBox.question(
            self,
            "Delete Location",
            f"Delete location '{loc['location_name']}'?"
        )

        if confirm != QMessageBox.Yes:
            return

        self.mongo.store_locations.delete_one({"_id": loc["_id"]})
        self.load_locations()

    # ---------------------------------------------------------
    # Activate / Deactivate
    # ---------------------------------------------------------
    def toggle_active(self):
        loc = self._get_selected_location()
        if not loc:
            return

        new_state = not loc.get("is_active", True)

        self.mongo.store_locations.update_one(
            {"_id": loc["_id"]},
            {"$set": {"is_active": new_state}}
        )

        self.load_locations()
