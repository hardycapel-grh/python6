from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QHeaderView, QMessageBox, QInputDialog
)
from PySide6.QtCore import Qt

from ui.components.logger_utils import log_event


class UomManagementPage(QWidget):
    def __init__(self, mongo, user, parent=None):


        super().__init__(parent)
        self.mongo = mongo
        self.user = user

        # temp bypassing permission check for now, will implement later
        # if not self._check_permissions():
        #     return

        self._build_ui()
        self._load_data()


    # ---------------------------------------------------------
    # Permissions
    # ---------------------------------------------------------
    def _check_permissions(self):
        admin_window = self.parent()
        if not admin_window or not admin_window.has_permission("uom.manage"):
            layout = QVBoxLayout(self)
            layout.addWidget(QLabel("You do not have permission to manage UOMs."))
            self.setLayout(layout)
            self.setDisabled(True)
            return False

        return True




    # ---------------------------------------------------------
    # UI
    # ---------------------------------------------------------
    def _build_ui(self):


        layout = QVBoxLayout(self)

        header_row = QHBoxLayout()
        header_label = QLabel("Unit of Measure (UOM) Management")
        header_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        header_row.addWidget(header_label)
        header_row.addStretch()
        layout.addLayout(header_row)

        # Table
        self.table = QTableWidget(0, 2)
        self.table.setHorizontalHeaderLabels(["UOM", "Description"])
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setSelectionMode(QTableWidget.SingleSelection)
        layout.addWidget(self.table)

       # Buttons
        btn_row = QHBoxLayout()
        self.btn_add = QPushButton("Add UOM")
        self.btn_delete = QPushButton("Delete Selected")
        self.btn_edit_desc = QPushButton("Edit Description")





        # Prevent collapse
        self.btn_add.setFixedHeight(32)
        self.btn_delete.setFixedHeight(32)
        self.btn_edit_desc.setFixedHeight(32)

        self.btn_add.clicked.connect(self._add_uom)
        self.btn_delete.clicked.connect(self._delete_selected)
        self.btn_edit_desc.clicked.connect(self._edit_description)

        btn_row.addStretch()
        btn_row.addWidget(self.btn_add)
        btn_row.addWidget(self.btn_delete)
        btn_row.addWidget(self.btn_edit_desc)
        btn_widget = QWidget()
        btn_widget.setLayout(btn_row)
        btn_widget.setMinimumHeight(40)

        layout.addWidget(btn_widget)


        # TEMP: big red label so we know where the bottom of the layout is

        

        self.setLayout(layout)



    # ---------------------------------------------------------
    # Data
    # ---------------------------------------------------------
    def _load_data(self):
        self.table.setRowCount(0)
        uoms = list(self.mongo.uom_list.find({}).sort("uom", 1))

        for row_idx, doc in enumerate(uoms):
            self.table.insertRow(row_idx)

            uom_item = QTableWidgetItem(doc.get("uom", ""))
            uom_item.setData(Qt.UserRole, str(doc.get("_id")))
            self.table.setItem(row_idx, 0, uom_item)

            desc_item = QTableWidgetItem(doc.get("description", ""))
            self.table.setItem(row_idx, 1, desc_item)


    # ---------------------------------------------------------
    # Add UOM
    # ---------------------------------------------------------
    def _add_uom(self):
    # Ask for UOM code
        uom, ok = QInputDialog.getText(self, "Add UOM", "Enter new UOM code:")
        if not ok or not uom.strip():
            return

        uom = uom.strip().upper()

        # Ask for description
        desc, ok = QInputDialog.getText(self, "UOM Description", f"Enter description for '{uom}':")
        if not ok:
            return

        description = desc.strip()

        # Check duplicate
        existing = self.mongo.uom_list.find_one({"uom": uom})
        if existing:
            QMessageBox.warning(self, "Duplicate", f"UOM '{uom}' already exists.")
            return

        try:
            self.mongo.uom_list.insert_one({"uom": uom, "description": description})

            # Audit
            self.mongo.log_event(
                "uom.create",
                performed_by=self.user.username,
                details=f"Created UOM '{uom}'"
            )

            # Debug
            log_event(
                "info",
                "UOM created",
                user=self.user.username,
                uom=uom
            )

            self._load_data()

        except Exception as e:
            log_event(
                "error",
                "Failed to create UOM",
                user=self.user.username,
                uom=uom,
                error=str(e)
            )
            QMessageBox.critical(self, "Error", f"Failed to create UOM:\n{e}")


    # ---------------------------------------------------------
    # Delete UOM
    # ---------------------------------------------------------
    def _delete_selected(self):
        row = self.table.currentRow()
        if row < 0:
            QMessageBox.warning(self, "No Selection", "Please select a UOM to delete.")
            return

        uom_item = self.table.item(row, 0)
        if not uom_item:
            return

        uom = uom_item.text().strip()

        # Prevent deleting UOMs in use anywhere
        if self._uom_in_use(uom):
            QMessageBox.warning(
                self,
                "In Use",
                f"UOM '{uom}' is in use and cannot be deleted."
            )
            return


        confirm = QMessageBox.question(
            self,
            "Confirm Delete",
            f"Are you sure you want to delete UOM '{uom}'?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        if confirm != QMessageBox.Yes:
            return

        try:
            self.mongo.uom_list.delete_one({"uom": uom})

            # Audit
            self.mongo.log_event(
                "uom.delete",
                performed_by=self.user.username,
                details=f"Deleted UOM '{uom}'"
            )

            # Debug
            log_event(
                "info",
                "UOM deleted",
                user=self.user.username,
                uom=uom
            )

            self._load_data()

        except Exception as e:
            log_event(
                "error",
                "Failed to delete UOM",
                user=self.user.username,
                uom=uom,
                error=str(e)
            )
            QMessageBox.critical(self, "Error", f"Failed to delete UOM:\n{e}")

    # ---------------------------------------------------------
    # UOM in-use check
    # ---------------------------------------------------------
    def _uom_in_use(self, uom: str) -> bool:
        """
        Returns True if the UOM is referenced anywhere in the system.
        Extend this as new collections start using UOMs.
        """
        checks = [
            # Inventory items
            (self.mongo.inventory, {"uom": uom}),

            # If/when you add these, uncomment/extend:
            # (self.mongo.purchase_orders, {"items.uom": uom}),
            # (self.mongo.sales_orders, {"items.uom": uom}),
            # (self.mongo.stock_movements, {"uom": uom}),
            # (self.mongo.bom, {"components.uom": uom}),
        ]

        for collection, query in checks:
            if collection.find_one(query):
                return True

        return False
    
    def _edit_description(self):
        row = self.table.currentRow()
        if row < 0:
            QMessageBox.warning(self, "No Selection", "Please select a UOM to edit.")
            return

        uom = self.table.item(row, 0).text()
        current_desc = self.table.item(row, 1).text()

        new_desc, ok = QInputDialog.getText(
            self,
            "Edit Description",
            f"Enter new description for '{uom}':",
            text=current_desc
        )

        if not ok:
            return

        self.mongo.uom_list.update_one(
            {"uom": uom},
            {"$set": {"description": new_desc.strip()}}
        )

        self._load_data()

