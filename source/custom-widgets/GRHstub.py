import sys

from PySide6.QtWidgets import (
    QApplication,
    QDial,
    QVBoxLayout,
    QWidget,
)
from PySide6.QtGui import QPainter, QBrush, QColor
from PySide6.QtCore import Qt


class _Bar(QWidget):
    pass


class PowerBar(QWidget):
    """
    Custom Qt Widget to show a power bar and dial.
    Demonstrating compound and custom-drawn widget.
    """

    def __init__(self, parent=None, steps=5):
        super().__init__(parent)

        layout = QVBoxLayout()
        self._bar = _Bar()
        layout.addWidget(self._bar)

        self._dial = QDial()
        layout.addWidget(self._dial)

        self.setLayout(layout)
    def paintEvent(self, e):
        painter = QPainter(self)
        brush = QBrush()
        brush.setColor(QColor("black"))
        brush.setStyle(Qt.SolidPattern)
        rect = self.rect()
        painter.fillRect(rect, brush)
        painter.fillRect(rect, brush)

app = QApplication(sys.argv)
window = PowerBar()
window.show()
app.exec()
