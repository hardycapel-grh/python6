from PySide6.QtWidgets import QLabel
from PySide6.QtCore import Qt, QTimer

class Toast(QLabel):
    def __init__(self, parent, message, duration=2000):
        super().__init__(parent)
        self.setText(message)
        self.setStyleSheet("""
            background-color: #323232;
            color: white;
            padding: 10px 20px;
            border-radius: 6px;
        """)
        self.setWindowFlags(Qt.ToolTip | Qt.FramelessWindowHint)
        self.adjustSize()

        parent_rect = parent.geometry()
        self.move(
            parent_rect.center().x() - self.width() // 2,
            parent_rect.bottom() - self.height() - 40
        )

        self.show()
        QTimer.singleShot(duration, self.close)