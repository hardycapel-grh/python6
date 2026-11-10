from PySide6.QtWidgets import QWidget, QVBoxLayout

from ui.pages.shop.shop_order_list_page import ShopOrderListPage


class ShopOrderWindow(QWidget):

    def __init__(self, user, mongo, window):
        super().__init__()

        self.user = user
        self.mongo = mongo
        self.window = window

        self.setWindowTitle("Shop Orders")

        self.resize(1400, 800)
        self.setMinimumSize(1200, 700)

        layout = QVBoxLayout(self)

        self.page = ShopOrderListPage(
            user=self.user,
            mongo=self.mongo,
            window=self.window
        )

        layout.addWidget(self.page)

    def refresh(self):
        self.page.refresh()