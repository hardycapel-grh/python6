from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel
from ui.components.logger import logger


class PermissionEditorPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Permission Editor Page"))

        logger.info("PermissionEditorPage loaded")