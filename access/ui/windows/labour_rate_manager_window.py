# ui/windows/labour_rate_manager_window.py

from PySide6.QtWidgets import QWidget, QVBoxLayout
from ui.pages.admin.labour_rate_manager_page import LabourRateManagerPage

class LabourRateManagerWindow(QWidget):
    def __init__(self, mongo, user, main_window):
        super().__init__()
        self.mongo = mongo
        self.user = user
        self.main_window = main_window

        layout = QVBoxLayout(self)
        self.page = LabourRateManagerPage(mongo, user, main_window)
        layout.addWidget(self.page)
