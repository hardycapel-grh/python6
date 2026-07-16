from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QComboBox,
    QPushButton, QScrollArea, QFrame, QSizePolicy
)
from PySide6.QtCore import Signal
from ui.widgets.bom_line_row import BOMLineRow


class BOMEditorWidget(QWidget):
    save_requested = Signal(dict)

    def __init__(self, items_list: list[dict], parent=None):
        super().__init__(parent)

        self.items_list = items_list

        # Internal revision tracking
        self.next_revision = None          # revision to save
        self.loaded_revision = None        # revision loaded from DB

        # Part Number selector
        self.assembly_cb = QComboBox()
        for item in items_list:
            label = f"{item['part_number']} (Rev {item['revision']})"
            self.assembly_cb.addItem(label)
            index = self.assembly_cb.count() - 1
            self.assembly_cb.setItemData(index, item)

        # Revision selector (UI shows next revision only)
        self.revision_cb = QComboBox()
        self.revision_cb.addItems(["A", "B", "C"])  # placeholder; overwritten by page logic

        # Buttons
        self.add_btn = QPushButton("Add Component")
        self.add_btn.clicked.connect(self._add_line)

        self.save_btn = QPushButton("Save BOM")
        self.save_btn.clicked.connect(self._save_bom)

        # Component rows container
        self.lines_container = QWidget()
        self.lines_container.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Maximum)

        self.lines_layout = QVBoxLayout()
        self.lines_layout.setSpacing(0)
        self.lines_layout.setContentsMargins(0, 0, 0, 0)
        self.lines_container.setLayout(self.lines_layout)

        # Scroll area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setWidget(self.lines_container)

        # Top controls
        top_layout = QHBoxLayout()
        top_layout.addWidget(QLabel("Part Number:"))
        top_layout.addWidget(self.assembly_cb)
        top_layout.addWidget(QLabel("Revision:"))
        top_layout.addWidget(self.revision_cb)
        top_layout.addWidget(self.add_btn)
        top_layout.addWidget(self.save_btn)

        # Main layout
        main_layout = QVBoxLayout()
        main_layout.addLayout(top_layout)
        main_layout.addWidget(scroll)
        main_layout.setSpacing(6)
        main_layout.setContentsMargins(6, 6, 6, 6)

        self.setLayout(main_layout)


    # ---------------------------------------------------------
    # Add a new blank BOM line
    # ---------------------------------------------------------
    def _add_line(self):
        row = BOMLineRow(self.items_list)
        row.remove_requested.connect(self._remove_line)

        frame = QFrame()
        frame.setFrameShape(QFrame.NoFrame)
        frame_layout = QVBoxLayout(frame)
        frame_layout.setSpacing(0)
        frame_layout.setContentsMargins(0, 0, 0, 0)
        frame_layout.addWidget(row)

        self.lines_layout.addWidget(frame)

    def _remove_line(self, row_widget):
        row_widget.setParent(None)
        row_widget.deleteLater()


    # ---------------------------------------------------------
    # Save BOM (uses next_revision if present)
    # ---------------------------------------------------------
    def _save_bom(self):
        assembly_item = self.assembly_cb.currentData()

        data = {
            "assembly_part_number": assembly_item["part_number"],
            "assembly_revision": assembly_item["revision"],

            # CRITICAL: use next_revision if set
            "revision": self.next_revision or self.revision_cb.currentText(),

            "lines": []
        }

        for i in range(self.lines_layout.count()):
            frame = self.lines_layout.itemAt(i).widget()
            row = frame.findChild(BOMLineRow)
            if row:
                data["lines"].append(row.get_data())

        self.save_requested.emit(data)

        # Reset next revision after save
        self.next_revision = None


    # ---------------------------------------------------------
    # Clear all BOM rows
    # ---------------------------------------------------------
    def clear_rows(self):
        while self.lines_layout.count() > 0:
            item = self.lines_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.setParent(None)
                widget.deleteLater()


    # ---------------------------------------------------------
    # Add a BOM line from loaded BOM data
    # ---------------------------------------------------------
    def add_row(self, component_part_number, component_revision, quantity, uom, comments):
        row = BOMLineRow(self.items_list)

        # Set component selector (this triggers _update_uom)
        for i in range(row.item_cb.count()):
            item = row.item_cb.itemData(i)
            if item["part_number"] == component_part_number and item["revision"] == component_revision:
                row.item_cb.setCurrentIndex(i)
                break

        # Set quantity
        row.qty_sb.setValue(float(quantity))

        # Set comments
        row.comments_le.setText(comments)

        # Add remove handler
        row.remove_requested.connect(self._remove_line)

        # Wrap in frame
        frame = QFrame()
        frame.setFrameShape(QFrame.NoFrame)
        frame_layout = QVBoxLayout(frame)
        frame_layout.setSpacing(0)
        frame_layout.setContentsMargins(0, 0, 0, 0)
        frame_layout.addWidget(row)

        self.lines_layout.addWidget(frame)
