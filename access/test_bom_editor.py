import sys
from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout
from ui.widgets.bom_editor_widget import BOMEditorWidget


class TestWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("BOM Editor Test")
        self.resize(900, 600)

        items_list = [
            {"part_number": "Widget A", "revision": "A", "uom": "pcs"},
            {"part_number": "Widget B", "revision": "B", "uom": "pcs"},
            {"part_number": "Screw M4", "revision": "A", "uom": "pcs"},
            {"part_number": "Bracket Steel", "revision": "C", "uom": "pcs"},
            {"part_number": "Motor 12V", "revision": "A", "uom": "pcs"},
        ]

        self.editor = BOMEditorWidget(items_list)
        self.editor.setMinimumHeight(200)   # ⭐ THIS FIXES THE SPACING ⭐

        layout = QVBoxLayout()
        layout.addWidget(self.editor)
        self.setLayout(layout)




if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = TestWindow()
    window.show()
    sys.exit(app.exec())


