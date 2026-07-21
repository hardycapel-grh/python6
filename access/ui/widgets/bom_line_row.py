from PySide6.QtWidgets import (
    QWidget, QHBoxLayout, QLineEdit, QCompleter, QDoubleSpinBox,
    QPushButton, QLabel, QSizePolicy, QComboBox
)
from PySide6.QtCore import Signal, QSize, Qt

ROW_HEIGHT = 26

class BOMLineRow(QWidget):
    changed = Signal()                     # NEW
    remove_requested = Signal(QWidget)

    def __init__(self, items_list: list[dict], parent=None):
        super().__init__(parent)

        self.items_list = items_list

        self.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
        self.setFixedHeight(ROW_HEIGHT)

        # ---------------------------------------------------------
        # AUTOCOMPLETE COMPONENT SELECTOR
        # ---------------------------------------------------------
        self.item_le = QLineEdit()
        self.item_le.setPlaceholderText("Search component...")
        self.item_le.setMinimumHeight(ROW_HEIGHT)
        self.item_le.setMaximumHeight(ROW_HEIGHT)

        self.labels = []
        self.item_map = {}

        for item in items_list:
            label = f"{item['part_number']} (Rev {item['revision']})"
            self.labels.append(label)
            self.item_map[label] = item

        self.completer = QCompleter(self.labels)
        self.completer.setCaseSensitivity(Qt.CaseInsensitive)
        self.item_le.setCompleter(self.completer)

        self.item_le.textChanged.connect(self._update_uom)
        self.item_le.textChanged.connect(self.changed)      # NEW

        # ---------------------------------------------------------
        # Quantity
        # ---------------------------------------------------------
        self.qty_sb = QDoubleSpinBox()
        self.qty_sb.setMinimum(0.0001)
        self.qty_sb.setMaximum(999999)
        self.qty_sb.setDecimals(4)
        self.qty_sb.setMinimumHeight(ROW_HEIGHT)
        self.qty_sb.setMaximumHeight(ROW_HEIGHT)
        self.qty_sb.setValue(1.0)
        self.qty_sb.valueChanged.connect(self.changed)      # NEW

        # ---------------------------------------------------------
        # Quantity Type
        # ---------------------------------------------------------
        self.qty_type_cb = QComboBox()
        self.qty_type_cb.addItems(["Fixed", "As Required", "Provisioned"])
        self.qty_type_cb.setMinimumHeight(ROW_HEIGHT)
        self.qty_type_cb.setMaximumHeight(ROW_HEIGHT)
        self.qty_type_cb.currentIndexChanged.connect(self.changed)  # NEW

        # ---------------------------------------------------------
        # Comments
        # ---------------------------------------------------------
        self.comments_le = QLineEdit()
        self.comments_le.setPlaceholderText("Comments")
        self.comments_le.setMinimumHeight(ROW_HEIGHT)
        self.comments_le.setMaximumHeight(ROW_HEIGHT)
        self.comments_le.textChanged.connect(self.changed)  # NEW

        # ---------------------------------------------------------
        # UOM label
        # ---------------------------------------------------------
        self.uom_label = QLabel("")
        self.uom_label.setMinimumHeight(ROW_HEIGHT)
        self.uom_label.setMaximumHeight(ROW_HEIGHT)

        # ---------------------------------------------------------
        # Remove button
        # ---------------------------------------------------------
        self.remove_btn = QPushButton("Remove")
        self.remove_btn.setMinimumHeight(ROW_HEIGHT)
        self.remove_btn.setMaximumHeight(ROW_HEIGHT)
        self.remove_btn.clicked.connect(self._on_remove)

        # ---------------------------------------------------------
        # Layout
        # ---------------------------------------------------------
        layout = QHBoxLayout()
        layout.setSpacing(0)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.item_le)
        layout.addWidget(self.qty_sb)
        layout.addWidget(self.uom_label)
        layout.addWidget(self.qty_type_cb)
        layout.addWidget(self.comments_le)
        layout.addWidget(self.remove_btn)

        self.setLayout(layout)

    def sizeHint(self):
        return QSize(0, ROW_HEIGHT)

    def _update_uom(self):
        label = self.item_le.text().strip()
        item = self.item_map.get(label)
        if not item:
            self.uom_label.setText("")
            return

        self.uom_label.setText(item["uom"])

        quantity_type = item.get("uom_quantity_type") or item.get("quantity_type") or "Fixed"

        if quantity_type == "integer":
            self.qty_sb.setDecimals(0)
            self.qty_sb.setSingleStep(1)
            self.qty_sb.setMinimum(1)
            self.qty_sb.setValue(int(self.qty_sb.value()))
        else:
            self.qty_sb.setDecimals(4)
            self.qty_sb.setSingleStep(0.0001)
            self.qty_sb.setMinimum(0.0001)

        # ⭐ REQUIRED for dirty flag
        self.changed.emit()


    def _on_remove(self):
        self.remove_requested.emit(self)
        self.changed.emit()  # NEW — removing a row marks dirty

    def get_data(self):
        label = self.item_le.text().strip()
        item = self.item_map.get(label)

        if not item:
            return None

        return {
            "component_part_number": item["part_number"],
            "component_revision": item["revision"],
            "quantity": self.qty_sb.value(),
            "uom": item["uom"],
            "quantity_type": self.qty_type_cb.currentText(),
            "comments": self.comments_le.text()
        }
