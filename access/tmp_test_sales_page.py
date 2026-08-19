from PySide6.QtWidgets import QApplication
import sys

app = QApplication([])

from ui.pages.sales.sales_order_list_page import SalesOrderListPage

class DummyUser:
    def __init__(self):
        self.username = 'tester'
        self.permissions = ['*']

class DummyColl:
    def __init__(self, items):
        self._items = items
    def find(self, *a, **k):
        return self._items

class DummyMongo:
    def __init__(self):
        self.sales_orders = DummyColl([
            {"so_number": "SO-001", "customer": "Acme", "req_date": "2026-08-18", "status": "Active", "type": "Firm"},
            {"so_number": "SO-002", "customer": "Beta", "req_date": "2026-08-19", "status": "Disabled", "type": "Enquiry"},
        ])

user = DummyUser()
mongo = DummyMongo()

w = SalesOrderListPage(user, mongo)

model = w.proxy.sourceModel()
print('source model rows:', model.rowCount())
print('proxy row count:', w.proxy.rowCount())

# Print first row data
for col in range(model.columnCount()):
    print('col', col, model.item(0, col).text())

# Exit
app.quit()
