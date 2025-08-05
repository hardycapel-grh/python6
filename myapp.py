import sys

from PySide6.QtCore import QSize
from PySide6.QtWidgets import QApplication, QMainWindow, QPushButton


# Subclass QMainWindow to customize your application's main window
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("My App")

        button = QPushButton("Press Me!")

        # Set the size of the window
        # self.resize(400, 300)  # <1> Resize to specific dimensions
        # self.setFixedSize(QSize(400, 300))  # <1> fixed size
        # self.setMinimumSize(QSize(400, 300))  # <1> Minimum size
        self.setMaximumSize(QSize(400, 300))  # <1> Maximum size

        # Set the central widget of the Window.
        self.setCentralWidget(button)


app = QApplication(sys.argv)

window = MainWindow()
window.show()

app.exec()
