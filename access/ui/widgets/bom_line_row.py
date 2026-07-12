from PySide6.QtWidgets import (
    QWidget, QHBoxLayout, QComboBox, QDoubleSpinBox,
    QPushButton, QLabel, QSizePolicy
)
from PySide6.QtCore import Signal, QSize
from PySide6.QtWidgets import QLineEdit



ROW_HEIGHT = 26


class BOMLineRow(QWidget):
    remove_requested = Signal(QWidget)

    def __init__(self, items_list: list[dict], parent=None):
        super().__init__(parent)

        # Prevent vertical expansion
        self.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
        self.setFixedHeight(ROW_HEIGHT)

        self.items_list = items_list

        # Component selector
        self.item_cb = QComboBox()
        self.item_cb.setMinimumHeight(ROW_HEIGHT)
        self.item_cb.setMaximumHeight(ROW_HEIGHT)

        for item in items_list:
            label = f"{item['part_number']} (Rev {item['revision']})"
            self.item_cb.addItem(label)
            index = self.item_cb.count() - 1
            self.item_cb.setItemData(index, item)

        self.item_cb.currentIndexChanged.connect(self._update_uom)

        # Quantity
        self.qty_sb = QDoubleSpinBox()
        self.qty_sb.setMinimum(0.0001)
        self.qty_sb.setMaximum(999999)
        self.qty_sb.setDecimals(4)
        self.qty_sb.setMinimumHeight(ROW_HEIGHT)
        self.qty_sb.setMaximumHeight(ROW_HEIGHT)
        self.qty_sb.setValue(1.0)

        # comments
        self.comments_le = QLineEdit()
        self.comments_le.setPlaceholderText("Comments")
        self.comments_le.setMinimumHeight(ROW_HEIGHT)
        self.comments_le.setMaximumHeight(ROW_HEIGHT)



        # UOM label
        self.uom_label = QLabel("")
        self.uom_label.setMinimumHeight(ROW_HEIGHT)
        self.uom_label.setMaximumHeight(ROW_HEIGHT)

        # Remove button
        self.remove_btn = QPushButton("Remove")
        self.remove_btn.setMinimumHeight(ROW_HEIGHT)
        self.remove_btn.setMaximumHeight(ROW_HEIGHT)
        self.remove_btn.clicked.connect(self._on_remove)

        # Layout
        layout = QHBoxLayout()
        layout.setSpacing(0)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.item_cb)
        layout.addWidget(self.qty_sb)
        layout.addWidget(self.uom_label)
        layout.addWidget(self.comments_le)
        layout.addWidget(self.remove_btn)

        self.setLayout(layout)

        self._update_uom()

    def sizeHint(self):
        return QSize(0, ROW_HEIGHT)

    def _update_uom(self):
        item = self.item_cb.currentData()
        if item:
            uom = item["uom"]
            self.uom_label.setText(uom)

            quantity_type = item["uom_quantity_type"]

            if quantity_type == "integer":
                self.qty_sb.setDecimals(0)
                self.qty_sb.setSingleStep(1)
                self.qty_sb.setMinimum(1)
                self.qty_sb.setValue(int(self.qty_sb.value()))
            else:
                self.qty_sb.setDecimals(4)
                self.qty_sb.setSingleStep(0.0001)
                self.qty_sb.setMinimum(0.0001)



    def _on_remove(self):
        self.remove_requested.emit(self)

    def get_data(self):
        item = self.item_cb.currentData()
        return {
            "component_part_number": item["part_number"],
            "component_revision": item["revision"],
            "quantity": self.qty_sb.value(),
            "uom": item["uom"],
            "comments": self.comments_le.text()
        }

