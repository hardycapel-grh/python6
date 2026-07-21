from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QComboBox,
    QPushButton, QScrollArea, QFrame, QSizePolicy
)
from PySide6.QtCore import Signal
from ui.widgets.bom_line_row import BOMLineRow


class BOMEditorWidget(QWidget):
    save_requested = Signal(dict)
    dirty_changed = Signal(bool)     # NEW — page listens to this

    def __init__(self, items_list: list[dict], parent=None):
        super().__init__(parent)

        self.items_list = items_list

        self.next_revision = None
        self.loaded_revision = None

        self.is_dirty = False              # NEW
        self.block_dirty_signals = False   # NEW — prevents dirty during auto-load

        # ---------------------------------------------------------
        # Assembly selector
        # ---------------------------------------------------------
        self.assembly_cb = QComboBox()
        for item in items_list:
            label = f"{item['part_number']} (Rev {item['revision']})"
            self.assembly_cb.addItem(label)
            index = self.assembly_cb.count() - 1
            self.assembly_cb.setItemData(index, item)

        # User changing assembly = dirty
        self.assembly_cb.currentIndexChanged.connect(
            lambda: self._set_dirty(True)
        )

        # ---------------------------------------------------------
        # Revision selector
        # ---------------------------------------------------------
        self.revision_cb = QComboBox()
        self.revision_cb.addItems(["A", "B", "C"])

        # ---------------------------------------------------------
        # Buttons
        # ---------------------------------------------------------
        self.add_btn = QPushButton("Add Component")
        self.add_btn.clicked.connect(self._add_line)

        self.save_btn = QPushButton("Save BOM")
        self.save_btn.clicked.connect(self._save_bom)

        # ---------------------------------------------------------
        # Component rows container
        # ---------------------------------------------------------
        self.lines_container = QWidget()
        self.lines_container.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Maximum)

        self.lines_layout = QVBoxLayout()
        self.lines_layout.setSpacing(0)
        self.lines_layout.setContentsMargins(0, 0, 0, 0)
        self.lines_container.setLayout(self.lines_layout)

        # ---------------------------------------------------------
        # Scroll area
        # ---------------------------------------------------------
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setWidget(self.lines_container)

        # ---------------------------------------------------------
        # Top controls
        # ---------------------------------------------------------
        top_layout = QHBoxLayout()
        top_layout.addWidget(QLabel("Part Number:"))
        top_layout.addWidget(self.assembly_cb)
        top_layout.addWidget(QLabel("Revision:"))
        top_layout.addWidget(self.revision_cb)
        top_layout.addWidget(self.add_btn)
        top_layout.addWidget(self.save_btn)

        # ---------------------------------------------------------
        # Main layout
        # ---------------------------------------------------------
        main_layout = QVBoxLayout()
        main_layout.addLayout(top_layout)
        main_layout.addWidget(scroll)
        main_layout.setSpacing(6)
        main_layout.setContentsMargins(6, 6, 6, 6)
        

        self.setLayout(main_layout)

    # ---------------------------------------------------------
    # Dirty flag handling
    # ---------------------------------------------------------
    def _set_dirty(self, value: bool):
        if self.block_dirty_signals:
            return

        self.is_dirty = value
        self.dirty_changed.emit(value)


    def _clear_dirty(self):
        self._set_dirty(False)

    # ---------------------------------------------------------
    # Add a new row (user action)
    # ---------------------------------------------------------
    def _add_line(self):
        row = BOMLineRow(self.items_list)
        row.remove_requested.connect(self._remove_line)
        row.changed.connect(lambda: self._set_dirty(True))   # NEW

        frame = QFrame()
        frame.setFrameShape(QFrame.NoFrame)
        frame_layout = QVBoxLayout(frame)
        frame_layout.setSpacing(0)
        frame_layout.setContentsMargins(0, 0, 0, 0)
        frame_layout.addWidget(row)

        self.lines_layout.addWidget(frame)
        self._set_dirty(True)

    # ---------------------------------------------------------
    # Remove row
    # ---------------------------------------------------------
    def _remove_line(self, row_widget):
        row_widget.setParent(None)
        row_widget.deleteLater()
        self._set_dirty(True)

    # ---------------------------------------------------------
    # Save BOM
    # ---------------------------------------------------------
    def _save_bom(self):
        assembly_item = self.assembly_cb.currentData()

        data = {
            "assembly_part_number": assembly_item["part_number"],
            "assembly_revision": assembly_item["revision"],
            "revision": self.next_revision or self.revision_cb.currentText(),
            "lines": []
        }

        for i in range(self.lines_layout.count()):
            frame = self.lines_layout.itemAt(i).widget()
            row = frame.findChild(BOMLineRow)
            if row:
                row_data = row.get_data()
                if row_data:
                    data["lines"].append(row_data)

        self.save_requested.emit(data)
        self.next_revision = None
        self._clear_dirty()

    # ---------------------------------------------------------
    # Clear all rows
    # ---------------------------------------------------------
    def clear_rows(self):
        while self.lines_layout.count() > 0:
            item = self.lines_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.setParent(None)
                widget.deleteLater()

    # ---------------------------------------------------------
    # Add row from DB (auto-load)
    # ---------------------------------------------------------
    def add_row(self, component_part_number, component_revision, quantity, uom, comments, quantity_type):
        row = BOMLineRow(self.items_list)

        label = f"{component_part_number} (Rev {component_revision})"
        row.item_le.setText(label)

        row.qty_sb.setValue(float(quantity))
        row.comments_le.setText(comments)
        row.qty_type_cb.setCurrentText(quantity_type)

        row.remove_requested.connect(self._remove_line)
        row.changed.connect(lambda: self._set_dirty(True))   # NEW

        frame = QFrame()
        frame.setFrameShape(QFrame.NoFrame)
        frame_layout = QVBoxLayout(frame)
        frame_layout.setSpacing(0)
        frame_layout.setContentsMargins(0, 0, 0, 0)
        frame_layout.addWidget(row)

        self.lines_layout.addWidget(frame)
