# ui/pages/admin/dialogs/add_store_location_dialog.py

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QPushButton, QMessageBox
)


class AddStoreLocationDialog(QDialog):
    def __init__(self, mongo, user, parent=None):
        super().__init__(parent)
        self.mongo = mongo
        self.user = user

        self.setWindowTitle("Add Store Location")
        self.setMinimumWidth(350)

        layout = QVBoxLayout(self)

        # Name
        layout.addWidget(QLabel("Location Name"))
        self.name = QLineEdit()
        layout.addWidget(self.name)

        # Description
        layout.addWidget(QLabel("Description"))
        self.description = QLineEdit()
        layout.addWidget(self.description)

        # Buttons
        btn_row = QHBoxLayout()
        btn_save = QPushButton("Save")
        btn_cancel = QPushButton("Cancel")

        btn_save.clicked.connect(self.save)
        btn_cancel.clicked.connect(self.reject)

        btn_row.addWidget(btn_save)
        btn_row.addWidget(btn_cancel)
        layout.addLayout(btn_row)

    def save(self):
        name = self.name.text().strip()

        if not name:
            QMessageBox.warning(self, "Missing Field", "Location name is required.")
            return

        doc = {
            "location_name": name,
            "description": self.description.text().strip(),
            "is_active": True
        }

        self.mongo.store_locations.insert_one(doc)
        self.accept()
