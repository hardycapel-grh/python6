# ui/pages/admin/dialogs/edit_store_location_dialog.py

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QPushButton, QMessageBox
)


class EditStoreLocationDialog(QDialog):
    def __init__(self, mongo, user, location, parent=None):
        super().__init__(parent)
        self.mongo = mongo
        self.user = user
        self.location = location

        self.setWindowTitle(f"Edit Location — {location['location_name']}")
        self.setMinimumWidth(350)

        layout = QVBoxLayout(self)

        # Name
        layout.addWidget(QLabel("Location Name"))
        self.name = QLineEdit(location.get("location_name", ""))
        layout.addWidget(self.name)

        # Description
        layout.addWidget(QLabel("Description"))
        self.description = QLineEdit(location.get("description", ""))
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

        self.mongo.store_locations.update_one(
            {"_id": self.location["_id"]},
            {
                "$set": {
                    "location_name": name,
                    "description": self.description.text().strip()
                }
            }
        )

        self.accept()
