from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton
)

from ui.widgets.bom_editor_widget import BOMEditorWidget


class EditShopOrderBomDialog(QDialog):

    def __init__(self, mongo, items_list, shop_bom, parent=None):
        super().__init__(parent)

        self.mongo = mongo
        self.items_list = items_list
        self.shop_bom = shop_bom or []

        self.lines = []

        self.setWindowTitle("Edit Shop Order BOM")
        self.resize(1200, 700)

        layout = QVBoxLayout(self)

        # ---------------------------------------------------------
        # BOM Editor Widget
        # ---------------------------------------------------------
        self.editor = BOMEditorWidget(
            self.items_list
        )

        # Hide master-BOM controls
        self.editor.assembly_cb.hide()
        self.editor.revision_cb.hide()

        self.editor.save_btn.setText(
            "Save Shop Order BOM"
        )

        layout.addWidget(self.editor)

        # ---------------------------------------------------------
        # Buttons
        # ---------------------------------------------------------
        button_row = QHBoxLayout()

        self.btn_cancel = QPushButton(
            "Cancel"
        )

        self.btn_cancel.clicked.connect(
            self.reject
        )

        button_row.addStretch()
        button_row.addWidget(
            self.btn_cancel
        )

        layout.addLayout(
            button_row
        )

        # ---------------------------------------------------------
        # Save handler from BOMEditorWidget
        # ---------------------------------------------------------
        self.editor.save_requested.connect(
            self._shop_bom_saved
        )

        # ---------------------------------------------------------
        # Load existing BOM
        # ---------------------------------------------------------
        self._load_shop_bom()

    # ---------------------------------------------------------
    # Load existing BOM lines
    # ---------------------------------------------------------
    def _load_shop_bom(self):

        self.editor.block_dirty_signals = True

        self.editor.clear_rows()

        for line in self.shop_bom:

            self.editor.add_row(
                component_part_number=line.get(
                    "component_part_number"
                ),
                component_revision=line.get(
                    "component_revision"
                ),
                quantity=line.get(
                    "quantity"
                ),
                uom=line.get(
                    "uom"
                ),
                comments=line.get(
                    "comments",
                    ""
                ),
                quantity_type=line.get(
                    "quantity_type",
                    "Fixed"
                )
            )

        self.editor.block_dirty_signals = False

    # ---------------------------------------------------------
    # Save BOM
    # ---------------------------------------------------------
    def _shop_bom_saved(self, bom_data):

        self.lines = bom_data.get(
            "lines",
            []
        )

        self.accept()