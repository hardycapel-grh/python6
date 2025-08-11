import sys

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication, QCheckBox, QMainWindow


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("My App")

        widget = QCheckBox("This is a checkbox")
        widget.setTristate(True)  # ✅ Enable tristate
        widget.setCheckState(Qt.CheckState.PartiallyChecked)  # Optional: set initial state

        widget.stateChanged.connect(self.show_state)

        self.setCentralWidget(widget)

    def show_state(self, s):
        state = Qt.CheckState(s)
        print("Checked:", state == Qt.CheckState.Checked)
        print("Partially Checked:", state == Qt.CheckState.PartiallyChecked)
        print("Unchecked:", state == Qt.CheckState.Unchecked)
        print("Raw value:", s)


app = QApplication(sys.argv)

window = MainWindow()
window.show()

app.exec()


