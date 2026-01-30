from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QTableWidget, QTableWidgetItem, QPushButton, QLineEdit, QTextEdit, QComboBox
from PySide6.QtCore import Qt

from ui.logger import logger
from database import db   # direct access to MongoDB for table data


class DataTablePage(QWidget):
    def __init__(self):
        super().__init__()
        self.title = "Data Table"
        self.read_only = True
        self.build_ui()

    def build_ui(self):
        layout = QVBoxLayout()

        label = QLabel("Data Table")
        label.setAlignment(Qt.AlignCenter)
        layout.addWidget(label)

        # Table widget
        self.table = QTableWidget()
        layout.addWidget(self.table)

        self.setLayout(layout)

        # Load data on startup
        self.load_data()

    def load_data(self):
        """
        Loads data from MongoDB into the table.
        Expects a collection named 'records' (you can rename this).
        """
        try:
            collection = db["records"]  # You can change this to any collection name
            data = list(collection.find({}, {"_id": 0}))  # Hide MongoDB _id

            if not data:
                logger.info("DataTablePage: No data found in 'records' collection")
                self.table.setRowCount(0)
                self.table.setColumnCount(0)
                return

            # Extract column names from first document
            columns = list(data[0].keys())
            self.table.setColumnCount(len(columns))
            self.table.setHorizontalHeaderLabels(columns)

            # Populate rows
            self.table.setRowCount(len(data))

            for row_idx, row_data in enumerate(data):
                for col_idx, col_name in enumerate(columns):
                    value = row_data.get(col_name, "")
                    item = QTableWidgetItem(str(value))
                    item.setFlags(item.flags() & ~Qt.ItemIsEditable)  # Always non-editable by default
                    self.table.setItem(row_idx, col_idx, item)

            logger.info("DataTablePage: Data loaded successfully")

        except Exception as e:
            logger.error(f"DataTablePage: Failed to load data: {e}")

    def set_read_only(self, readonly: bool):
        """
        Enables or disables editing based on permission.
        """
        self.read_only = readonly

        if readonly:
            logger.info("DataTablePage set to read-only mode")
            # Disable editing
            for row in range(self.table.rowCount()):
                for col in range(self.table.columnCount()):
                    item = self.table.item(row, col)
                    if item:
                        item.setFlags(item.flags() & ~Qt.ItemIsEditable)
        else:
            logger.info("DataTablePage set to read-write mode")
            # Enable editing
            for row in range(self.table.rowCount()):
                for col in range(self.table.columnCount()):
                    item = self.table.item(row, col)
                    if item:
                        item.setFlags(item.flags() | Qt.ItemIsEditable)

    def set_read_only(self, ro: bool):
        """Enable or disable editing for all input widgets."""
        for widget in self.findChildren((QLineEdit, QTextEdit, QComboBox)):
            if isinstance(widget, QLineEdit):
                widget.setReadOnly(ro)
            elif isinstance(widget, QTextEdit):
                widget.setReadOnly(ro)
            elif isinstance(widget, QComboBox):
                widget.setEnabled(not ro)

        # Disable buttons that modify data
        for btn in self.findChildren(QPushButton):
            if btn.objectName() not in ("nav", "close", "back"):
                btn.setEnabled(not ro)
