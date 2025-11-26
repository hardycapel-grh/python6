from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLabel,
    QLineEdit, QPushButton, QMessageBox
)
from pymongo import MongoClient
import sys

class PersonLookupApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("MongoDB Person Lookup")

        # MongoDB connection
        self.client = MongoClient("mongodb://localhost:27017/")
        self.db = self.client["test"]
        self.collection = self.db["people"]

        # Layout
        layout = QVBoxLayout()

        # Input field for name
        self.name_input = QLineEdit()
        layout.addWidget(QLabel("Enter name to search:"))
        layout.addWidget(self.name_input)

        # Search button
        search_btn = QPushButton("Find Person")
        search_btn.clicked.connect(self.find_person)
        layout.addWidget(search_btn)

        # Labels to display results
        self.result_name = QLabel("Name: ")
        self.result_age = QLabel("Age: ")
        self.result_address = QLabel("Address: ")

        layout.addWidget(self.result_name)
        layout.addWidget(self.result_age)
        layout.addWidget(self.result_address)

        self.setLayout(layout)

    def find_person(self):
        name = self.name_input.text().strip()
        if not name:
            QMessageBox.warning(self, "Input Error", "Please enter a name.")
            return

        person = self.collection.find_one({"name": name})
        if person:
            self.result_name.setText(f"Name: {person.get('name', '')}")
            self.result_age.setText(f"Age: {person.get('age', '')}")
            self.result_address.setText(f"Address: {person.get('address', '')}")
        else:
            QMessageBox.information(self, "Not Found", f"No entry found for '{name}'")
            self.result_name.setText("Name: ")
            self.result_age.setText("Age: ")
            self.result_address.setText("Address: ")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = PersonLookupApp()
    window.show()
    sys.exit(app.exec())