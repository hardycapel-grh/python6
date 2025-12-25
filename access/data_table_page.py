from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QTableWidget, QTableWidgetItem
from PySide6.QtCore import Qt


class DataTablePage(QWidget):
    def __init__(self):
        super().__init__()
        self.title = "Data Table"
        self.build_ui()

    def build_ui(self):
        layout = QVBoxLayout()

        label = QLabel("Data Table Page")
        label.setAlignment(Qt.AlignCenter)
        layout.addWidget(label)

        # Example table
        self.table = QTableWidget(3, 3)
        self.table.setHorizontalHeaderLabels(["A", "B", "C"])

        for r in range(3):
            for c in range(3):
                self.table.setItem(r, c, QTableWidgetItem(f"Item {r},{c}"))

        layout.addWidget(self.table)
        self.setLayout(layout)

    def set_read_only(self, readonly: bool):
        # Tables need special handling
        self.table.setEditTriggers(
            self.table.NoEditTriggers if readonly else self.table.AllEditTriggers
        )

        # Disable other widgets if needed
        for widget in self.findChildren(QWidget):
            if widget is not self.table:
                if hasattr(widget, "setEnabled"):
                    widget.setEnabled(not readonly)