from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox
from pymongo import MongoClient
import sys

class DataEntryApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("MongoDB Data Entry")

        # MongoDB connection
        self.client = MongoClient("mongodb://localhost:27017/")
        self.db = self.client["test"]
        self.collection = self.db["people"]

        # Layout
        layout = QVBoxLayout()

        # Name field
        self.name_input = QLineEdit()
        layout.addWidget(QLabel("Name:"))
        layout.addWidget(self.name_input)

        # Age field
        self.age_input = QLineEdit()
        layout.addWidget(QLabel("Age:"))
        layout.addWidget(self.age_input)

        # Address field
        self.address_input = QLineEdit()
        layout.addWidget(QLabel("Address:"))
        layout.addWidget(self.address_input)

        # Submit button
        submit_btn = QPushButton("Save to MongoDB")
        submit_btn.clicked.connect(self.save_data)
        layout.addWidget(submit_btn)

        self.setLayout(layout)

    def save_data(self):
        name = self.name_input.text().strip()
        age = self.age_input.text().strip()
        address = self.address_input.text().strip()

        if not name or not age or not address:
            QMessageBox.warning(self, "Input Error", "All fields are required!")
            return

        try:
            age = int(age)  # ensure age is numeric
        except ValueError:
            QMessageBox.warning(self, "Input Error", "Age must be a number!")
            return

        # Insert into MongoDB
        self.collection.insert_one({
            "name": name,
            "age": age,
            "address": address
        })

        QMessageBox.information(self, "Success", "Data saved to MongoDB!")
        self.name_input.clear()
        self.age_input.clear()
        self.address_input.clear()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = DataEntryApp()
    window.show()
    sys.exit(app.exec())