from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QTableView, QMessageBox, QDialog, QLineEdit, QComboBox, QStyledItemDelegate
)
from PySide6.QtCore import Qt, QAbstractTableModel, QSortFilterProxyModel, QRectF
from PySide6.QtGui import QTextDocument, QPainter

from services.mongo_service import MongoService
from services.permission_service import has_permission
from ui.components.logger import logger
from ui.dialogs.user_dialogs import EditUserDialog
from services.user_service import UserService


# =========================================================
# Highlight Delegate
# =========================================================
class HighlightDelegate(QStyledItemDelegate):
    def __init__(self, parent, get_search_text):
        super().__init__(parent)
        self.get_search_text = get_search_text

    def paint(self, painter, option, index):
        text = index.data(Qt.DisplayRole)
        search = self.get_search_text().strip()

        if not search or search.lower() not in text.lower():
            super().paint(painter, option, index)
            return

        highlighted = text.replace(
            search,
            f"<span style='background-color: yellow; color: black;'>{search}</span>"
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
            return [
                user.get("username", ""),
                user.get("email", ""),
                user.get("role", ""),
                user.get("status", "")
            ][col]

        return None

    def headerData(self, section, orientation, role):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return self.headers[section]
        return None


# =========================================================
# Users Page
# =========================================================
class UsersPage(QWidget):
    def __init__(self, user, mongo, parent=None):
        super().__init__(parent)

        self.current_user = user
        self.mongo = mongo
        self.users = []
        self.app = parent

        # ---------------------------------------------------------
        # 1. WINDOW-LEVEL PERMISSION ENFORCEMENT
        # ---------------------------------------------------------
        if not has_permission(self.current_user, "users.read"):
            QMessageBox.warning(self, "Access Denied",
                                "You do not have permission to view Users.")
            self.close()
            return

        # ---------------------------------------------------------
        # 2. BUILD UI
        # ---------------------------------------------------------
        layout = QVBoxLayout(self)

        # Toolbar
        toolbar = QHBoxLayout()

        self.refresh_btn = QPushButton("Refresh")
        self.refresh_btn.clicked.connect(self.load_users)
        toolbar.addWidget(self.refresh_btn)

        self.add_btn = QPushButton("Add User")
        self.add_btn.clicked.connect(self.open_add_user_dialog)
        toolbar.addWidget(self.add_btn)

        self.edit_btn = QPushButton("Edit User")
        self.edit_btn.clicked.connect(self._edit_selected_user)
        toolbar.addWidget(self.edit_btn)

        self.delete_btn = QPushButton("Delete")
        self.delete_btn.clicked.connect(self._delete_selected_user)
        toolbar.addWidget(self.delete_btn)

        self.toggle_btn = QPushButton("Enable / Disable")
        self.toggle_btn.clicked.connect(self._toggle_user_status)
        toolbar.addWidget(self.toggle_btn)

        self.add_btn.setEnabled(self.app.has_permission("users.create"))
        self.edit_btn.setEnabled(self.app.has_permission("users.edit"))
        self.delete_btn.setEnabled(self.app.has_permission("users.delete"))



        # Search bar
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search users…")
        self.search_input.textChanged.connect(self._apply_filter)
        toolbar.addWidget(self.search_input)

        # Role filter
        self.role_filter = QComboBox()
        self.role_filter.addItems(["All Roles", "admin", "user", "manager", "viewer"])
        self.role_filter.currentTextChanged.connect(self._apply_role_filter)
        toolbar.addWidget(self.role_filter)

        # Status filter
        self.status_filter = QComboBox()
        self.status_filter.addItems(["All Statuses", "Active", "Disabled"])
        self.status_filter.currentTextChanged.connect(self._apply_status_filter)
        toolbar.addWidget(self.status_filter)

        toolbar.addStretch()
        layout.addLayout(toolbar)

        # Table
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

        self.table.doubleClicked.connect(self._edit_selected_user)
        layout.addWidget(self.table)

        # ---------------------------------------------------------
        # 3. APPLY UI PERMISSIONS
        # ---------------------------------------------------------
        self._apply_ui_permissions()

        # ---------------------------------------------------------
        # 4. LOAD DATA
        # ---------------------------------------------------------
        self.load_users()

    # ---------------------------------------------------------
    # Load users
    # ---------------------------------------------------------
    def load_users(self):
        try:
            logger.info("Loading users from MongoDB…")
            self.users = list(self.mongo.users.find())

            model = UsersTableModel(self.users)

            self.proxy = QSortFilterProxyModel(self)
            self.proxy.setSourceModel(model)
            self.proxy.setFilterCaseSensitivity(Qt.CaseInsensitive)
            self.proxy.setFilterKeyColumn(-1)
            self.proxy.setSortCaseSensitivity(Qt.CaseInsensitive)
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
        from ui.dialogs.user_dialogs import AddUserDialog
        if not self.app.has_permission("users.create"):
            self.app.show_permission_denied()
            return
        dlg = AddUserDialog(self.mongo, self.current_user, parent=self)
        if dlg.exec():
            self.load_users()


    # ---------------------------------------------------------
    # Edit User
    # ---------------------------------------------------------
    
    def _edit_selected_user(self):
        if not self.app.has_permission("users.edit"):
            self.app.show_permission_denied()
            return

        index = self.table.currentIndex()
        if not index.isValid():
            QMessageBox.warning(self, "No Selection", "Please select a user to edit.")
            return

        source_index = self.proxy.mapToSource(index)
        user_doc = self.proxy.sourceModel().get_user(source_index.row())

        dialog = EditUserDialog(
            self.mongo,
            user_doc,
            self.current_user,
            parent=self
        )
        dialog.saved.connect(self.load_users)   # ← refresh automatically  
        dialog.exec()



    # ---------------------------------------------------------
    # Delete User
    # ---------------------------------------------------------
    def _delete_selected_user(self):
        if not self.app.has_permission("users.delete"):
            self.app.show_permission_denied()
            return

        index = self.table.currentIndex()
        if not index.isValid():
            QMessageBox.warning(self, "No Selection", "Please select a user to delete.")
            return

        source_index = self.proxy.mapToSource(index)
        user_doc = self.proxy.sourceModel().get_user(source_index.row())
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
            self.mongo.delete_user(
                user_doc["_id"],
                performed_by=self.current_user.username
            )
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
        user_doc = self.proxy.sourceModel().get_user(source_index.row())

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
            self.mongo.update_user(
                user_doc["_id"],
                {"status": new_status},
                performed_by=self.current_user.username
            )
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

        self.proxy.setFilterKeyColumn(-1)
        self.proxy.setFilterFixedString(text)

        if self.role_filter.currentText() != "All Roles":
            self._apply_role_filter(self.role_filter.currentText())

        if self.status_filter.currentText() != "All Statuses":
            self._apply_status_filter(self.status_filter.currentText())

        self.table.viewport().update()

    def _apply_role_filter(self, role):
        if not hasattr(self, "proxy"):
            return

        if role == "All Roles":
            self.proxy.setFilterRegularExpression(self.search_input.text())
            return

        pattern = f"^{role}$"
        self.proxy.setFilterKeyColumn(2)
        self.proxy.setFilterRegularExpression(pattern)
        self.proxy.setFilterKeyColumn(-1)

    def _apply_status_filter(self, status):
        if not hasattr(self, "proxy"):
            return

        if status == "All Statuses":
            self.proxy.setFilterRegularExpression(self.search_input.text())
            return

        pattern = f"^{status}$"
        self.proxy.setFilterKeyColumn(3)
        self.proxy.setFilterRegularExpression(pattern)
        self.proxy.setFilterKeyColumn(-1)

        if self.role_filter.currentText() != "All Roles":
            self._apply_role_filter(self.role_filter.currentText())

    # ---------------------------------------------------------
    # Apply UI Permissions
    # ---------------------------------------------------------
    def _apply_ui_permissions(self):
        can_write = has_permission(self.current_user, "users.write")

        self.add_btn.setVisible(self.app.has_permission("users.create"))
        self.edit_btn.setVisible(self.app.has_permission("users.edit"))
        self.delete_btn.setVisible(self.app.has_permission("users.delete"))
        self.toggle_btn.setVisible(self.app.has_permission("users.edit"))

