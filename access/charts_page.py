from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel
from PySide6.QtCore import Qt


class ChartsPage(QWidget):
    def __init__(self):
        super().__init__()
        self.title = "Charts"
        self.build_ui()

    def build_ui(self):
        layout = QVBoxLayout()
        label = QLabel("Charts Page (placeholder)")
        label.setAlignment(Qt.AlignCenter)
        layout.addWidget(label)
        self.setLayout(layout)

    def set_read_only(self, readonly: bool):
        for widget in self.findChildren(QWidget):
            if hasattr(widget, "setReadOnly"):
                widget.setReadOnly(readonly)
            elif hasattr(widget, "setEnabled"):
                widget.setEnabled(not readonly)