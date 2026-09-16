# ui/pages/workbench/works_order_window.py

from PySide6.QtWidgets import QWidget, QVBoxLayout
from ui.pages.works.works_order_list_page import WorksOrderListPage

class WorkOrderWindow(QWidget):
    def __init__(self, mongo, user, main_window):
        super().__init__()

        self.mongo = mongo
        self.user = user
        self.main_window = main_window

        layout = QVBoxLayout(self)

        self.page = WorksOrderListPage(mongo, user, main_window)
        layout.addWidget(self.page)
