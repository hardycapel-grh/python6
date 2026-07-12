# ui/pages/admin/bom_editor_page.py

from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel
from ui.widgets.bom_editor_widget import BOMEditorWidget
from datetime import datetime
from PySide6.QtWidgets import QMessageBox


class BOMEditorPage(QWidget):
    def __init__(self, mongo, user, parent=None):
        super().__init__(parent)

        self.mongo = mongo          # ⭐ REQUIRED
        self.user = user            # ⭐ REQUIRED

        uoms = {u["uom"]: u for u in self.mongo.uom_list.find({})}

        items_list = []
        for item in self.mongo.inventory.find({}):
            uom = item["uom"]
            item["uom_quantity_type"] = uoms[uom]["quantity_type"]
            items_list.append(item)



        layout = QVBoxLayout()
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(12)

        title = QLabel("Bill of Materials Editor")
        title.setStyleSheet("font-size: 20px; font-weight: bold;")

        self.editor = BOMEditorWidget(items_list)

        layout.addWidget(title)
        layout.addWidget(self.editor)

        self.setLayout(layout)

        self.editor.save_requested.connect(self._save_bom_to_db)

    

    def _save_bom_to_db(self, bom_data):
        bom_data["created_by"] = self.user.username
        bom_data["created_at"] = datetime.utcnow()

        self.mongo.bom.insert_one(bom_data)

        QMessageBox.information(self, "Saved", "BOM saved successfully.")
