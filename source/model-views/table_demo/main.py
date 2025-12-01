import sys
from PySide6.QtWidgets import QApplication, QTableView
from table_model import TableModel

if __name__ == "__main__":
    app = QApplication(sys.argv)

    # Sample data: list of rows, each row is a list of columns
    data = [
        ["Alice", 24, "Engineer"],
        ["Bob", 30, "Designer"],
        ["Charlie", 28, "Writer"]
    ]

    model = TableModel(data)
    table = QTableView()
    table.setModel(model)
    table.setWindowTitle("Simple Table Model")
    table.resize(400, 200)
    table.show()

    sys.exit(app.exec())