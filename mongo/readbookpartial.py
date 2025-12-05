# mongo/readbookpartial.py
# A PySide6 application to look up persons in a MongoDB collection
# by partial, case-insensitive name match and display results in a table.

from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLabel,
    QLineEdit, QPushButton, QMessageBox, QTableWidget, QTableWidgetItem
)
from pymongo import MongoClient
import sys, re

class PersonLookupApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("MongoDB Person Lookup")

        # MongoDB connection
        self.client = MongoClient("mongodb://localhost:27017/")
        self.db = self.client["test"]
        self.collection = self.db["people"]

        layout = QVBoxLayout()

        # Input field for name
        self.name_input = QLineEdit()
        layout.addWidget(QLabel("Enter name to search (partial, case-insensitive):"))
        layout.addWidget(self.name_input)

        # Search button
        search_btn = QPushButton("Find Person(s)")
        search_btn.clicked.connect(self.find_persons)
        layout.addWidget(search_btn)

        # Table to display results
        self.results_table = QTableWidget()
        self.results_table.setColumnCount(3)
        self.results_table.setHorizontalHeaderLabels(["Name", "Age", "Address"])
        layout.addWidget(self.results_table)

        self.setLayout(layout)

    def find_persons(self):
        name = self.name_input.text().strip()
        if not name:
            QMessageBox.warning(self, "Input Error", "Please enter a name.")
            return

        # Case-insensitive partial match
        cursor = self.collection.find({"name": re.compile(re.escape(name), re.IGNORECASE)})
        results = list(cursor)

        if results:
            self.results_table.setRowCount(len(results))
            for row, person in enumerate(results):
                self.results_table.setItem(row, 0, QTableWidgetItem(person.get("name", "")))
                self.results_table.setItem(row, 1, QTableWidgetItem(str(person.get("age", ""))))
                self.results_table.setItem(row, 2, QTableWidgetItem(person.get("address", "")))
        else:
            QMessageBox.information(self, "Not Found", f"No entries found containing '{name}'")
            self.results_table.setRowCount(0)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = PersonLookupApp()
    window.show()
    sys.exit(app.exec())