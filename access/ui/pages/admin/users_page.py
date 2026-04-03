from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QTableView, QMessageBox, QDialog, QLineEdit
)
from PySide6.QtCore import Qt, QAbstractTableModel, QSortFilterProxyModel

from services.mongo_service import MongoService
from ui.components.logger import logger
from ui.dialogs.edit_user_dialog import EditUserDialog
from PySide6.QtWidgets import QComboBox

from PySide6.QtWidgets import QStyledItemDelegate
from PySide6.QtGui import QTextDocument, QAbstractTextDocumentLayout, QPainter
from PySide6.QtCore import QRectF


class HighlightDelegate(QStyledItemDelegate):
    def __init__(self, parent, get_search_text):
        super().__init__(parent)
        self.get_search_text = get_search_text  # function to retrieve current search text

    def paint(self, painter, option, index):
        text = index.data(Qt.DisplayRole)
        search = self.get_search_text().strip()

        # If no search text, paint normally
        if not search or search.lower() not in text.lower():
            super().paint(painter, option, index)
            return

        # Build highlighted HTML
        highlighted = text.replace(
            search,
            f"<span style='background-color: yellow; color: black;'>{search}</span>",
        )

        doc = QTextDocument()
        doc.setHtml(highlighted)

        painter.save()
        painter.translate(option.rect.topLeft())
        clip = QRectF(0, 0, option.rect.width(), option.rect.height())
        doc.drawContents(painter, clip)
        painter.restore()


# =========================================================
# Table Model
# =========================================================
class UsersTableModel(QAbstractTableModel):
    def __init__(self, users):
        super().__init__()
        self.users = users
        self.headers = ["Username", "Email", "Role", "Status"]

    def get_user(self, row):
        return self.users[row]

    def rowCount(self, parent=None):
        return len(self.users)

    def columnCount(self, parent=None):
        return len(self.headers)

    def data(self, index, role):
        if not index.isValid():
            return None

        user = self.users[index.row()]
        col = index.column()

        if role == Qt.DisplayRole:
            if col == 0:
                return user.get("username", "")
            if col == 1:
                return user.get("email", "")
            if col == 2:
                return user.get("role", "")
            if col == 3:
                return user.get("status", "")

        return None

    def headerData(self, section, orientation, role):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return self.headers[section]
        return None


# =========================================================
# Users Page
# =========================================================
class UsersPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        from services.user_service import UserService
        self.user_service = UserService()
        self.mongo = MongoService()
        self.users = []

        layout = QVBoxLayout(self)

        # ---------------------------------------------------------
        # Toolbar
        # ---------------------------------------------------------
        toolbar = QHBoxLayout()

        self.refresh_btn = QPushButton("Refresh")
        self.refresh_btn.clicked.connect(self.load_users)
        toolbar.addWidget(self.refresh_btn)

        self.add_btn = QPushButton("Add User")
        self.add_btn.clicked.connect(self.open_add_user_dialog)
        toolbar.addWidget(self.add_btn)

        edit_btn = QPushButton("Edit User")
        edit_btn.clicked.connect(self._edit_selected_user)
        toolbar.addWidget(edit_btn)

        delete_btn = QPushButton("Delete")
        delete_btn.clicked.connect(self._delete_selected_user)
        toolbar.addWidget(delete_btn)

        toggle_btn = QPushButton("Enable / Disable")
        toggle_btn.clicked.connect(self._toggle_user_status)
        toolbar.addWidget(toggle_btn)

        # Search bar
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search users…")
        self.search_input.textChanged.connect(self._apply_filter)
        toolbar.addWidget(self.search_input)

        self.role_filter = QComboBox()
        self.role_filter.addItem("All Roles")
        self.role_filter.addItem("admin")
        self.role_filter.addItem("user")
        # Add more if you have custom roles
        self.role_filter.addItem("manager")
        self.role_filter.addItem("viewer")

        self.role_filter.currentTextChanged.connect(self._apply_role_filter)
        toolbar.addWidget(self.role_filter)

        self.status_filter = QComboBox()
        self.status_filter.addItem("All Statuses")
        self.status_filter.addItem("Active")
        self.status_filter.addItem("Disabled")

        self.status_filter.currentTextChanged.connect(self._apply_status_filter)
        toolbar.addWidget(self.status_filter)



        toolbar.addStretch()
        layout.addLayout(toolbar)

        # ---------------------------------------------------------
        # Table
        # ---------------------------------------------------------
        self.table = QTableView()
        self.table.setSelectionBehavior(QTableView.SelectRows)
        self.table.setSelectionMode(QTableView.SingleSelection)
        self.table.setAlternatingRowColors(True)

        self.table.setSortingEnabled(True)
        self.highlight_delegate = HighlightDelegate(
            self.table,
            get_search_text=lambda: self.search_input.text()
        )
        self.table.setItemDelegate(self.highlight_delegate)

        # Double-click to edit
        self.table.doubleClicked.connect(self._edit_selected_user)

        layout.addWidget(self.table)

        # Load initial data
        self.load_users()

    # ---------------------------------------------------------
    # Load users from MongoDB
    # ---------------------------------------------------------
    def load_users(self):
        try:
            logger.info("Loading users from MongoDB…")
            self.users = self.mongo.get_all_users()

            # Base model
            model = UsersTableModel(self.users)

            # Proxy model for filtering + sorting
            self.proxy = QSortFilterProxyModel(self)
            self.proxy.setSourceModel(model)
            self.proxy.setFilterCaseSensitivity(Qt.CaseInsensitive)
            self.proxy.setFilterKeyColumn(-1)
            self.proxy.setSortCaseSensitivity(Qt.CaseInsensitive)   # ⭐ ADD THIS
            self.proxy.setDynamicSortFilter(True)



            self.table.setModel(self.proxy)
            self.table.resizeColumnsToContents()

            logger.info(f"Loaded {len(self.users)} users.")
        except Exception as e:
            logger.error(f"Failed to load users: {e}")
            QMessageBox.critical(self, "Error", f"Failed to load users:\n{e}")

    # ---------------------------------------------------------
    # Add User
    # ---------------------------------------------------------
    def open_add_user_dialog(self):
        from ui.dialogs.add_user_dialog import AddUserDialog

        dlg = AddUserDialog(self.user_service, self)

        if dlg.exec():
            self.load_users()

    # ---------------------------------------------------------
    # Edit User
    # ---------------------------------------------------------
    def _edit_selected_user(self):
        index = self.table.currentIndex()
        if not index.isValid():
            QMessageBox.warning(self, "No Selection", "Please select a user to edit.")
            return

        # Map proxy → source
        source_index = self.proxy.mapToSource(index)
        row = source_index.row()

        user_doc = self.proxy.sourceModel().get_user(row)

        dialog = EditUserDialog(user_doc, self)
        if dialog.exec() == QDialog.Accepted:
            self.load_users()

    # ---------------------------------------------------------
    # Delete User
    # ---------------------------------------------------------
    def _delete_selected_user(self):
        index = self.table.currentIndex()
        if not index.isValid():
            QMessageBox.warning(self, "No Selection", "Please select a user to delete.")
            return

        source_index = self.proxy.mapToSource(index)
        row = source_index.row()

        user_doc = self.proxy.sourceModel().get_user(row)
        username = user_doc["username"]

        confirm = QMessageBox.question(
            self,
            "Confirm Delete",
            f"Are you sure you want to delete user '{username}'?",
            QMessageBox.Yes | QMessageBox.No
        )

        if confirm != QMessageBox.Yes:
            return

        try:
            self.mongo.delete_user(user_doc["_id"])
            logger.info(f"User '{username}' deleted.")
            self.load_users()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to delete user:\n{e}")

    # ---------------------------------------------------------
    # Enable / Disable User
    # ---------------------------------------------------------
    def _toggle_user_status(self):
        index = self.table.currentIndex()
        if not index.isValid():
            QMessageBox.warning(self, "No Selection", "Please select a user.")
            return

        source_index = self.proxy.mapToSource(index)
        row = source_index.row()

        user_doc = self.proxy.sourceModel().get_user(row)
        username = user_doc["username"]
        current_status = user_doc.get("status", "Active")

        new_status = "Disabled" if current_status == "Active" else "Active"

        confirm = QMessageBox.question(
            self,
            "Confirm Status Change",
            f"Change status of '{username}' from {current_status} to {new_status}?",
            QMessageBox.Yes | QMessageBox.No
        )

        if confirm != QMessageBox.Yes:
            return

        try:
            self.mongo.update_user(user_doc["_id"], {"status": new_status})
            logger.info(f"User '{username}' status changed to {new_status}")
            self.load_users()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to update status:\n{e}")

    # ---------------------------------------------------------
    # Search Filter
    # ---------------------------------------------------------
    def _apply_filter(self, text):
        if not hasattr(self, "proxy"):
            return

        # Apply search text across all columns
        self.proxy.setFilterKeyColumn(-1)
        self.proxy.setFilterFixedString(text)

        # Reapply role filter if needed
        current_role = self.role_filter.currentText()
        if current_role != "All Roles":
            self._apply_role_filter(current_role)

        # Reapply status filter if needed
        current_status = self.status_filter.currentText()
        if current_status != "All Statuses":
            self._apply_status_filter(current_status)

        # Repaint table to update highlights
        self.table.viewport().update()




    def _apply_role_filter(self, role):
        if not hasattr(self, "proxy"):
            return

        if role == "All Roles":
            # Clear role filter
            self.proxy.setFilterRegularExpression(self.search_input.text())
            return

        # Filter by role AND search text
        pattern = f"^{role}$"
        self.proxy.setFilterKeyColumn(2)  # column 2 = role
        self.proxy.setFilterRegularExpression(pattern)

        # Restore search to apply on all columns
        self.proxy.setFilterKeyColumn(-1)


    def _apply_status_filter(self, status):
        if not hasattr(self, "proxy"):
            return

        if status == "All Statuses":
            # Clear status filter
            self.proxy.setFilterRegularExpression(self.search_input.text())
            return

        # Filter by exact status
        pattern = f"^{status}$"
        self.proxy.setFilterKeyColumn(3)  # column 3 = Status
        self.proxy.setFilterRegularExpression(pattern)

        # Restore search to all columns
        self.proxy.setFilterKeyColumn(-1)

        # Reapply role filter if needed
        current_role = self.role_filter.currentText()
        if current_role != "All Roles":
            self._apply_role_filter(current_role)

