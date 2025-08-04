import sys

from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QPushButton,
)  # <1>


# Subclass QMainWindow to customize your application's main window
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()  # <2>

        self.setWindowTitle("My App")

        button = QPushButton("Press Me!")

        # Set the central widget of the Window.
        self.setCentralWidget(button)  # <3>


app = QApplication(sys.argv)

window = MainWindow()
window.show()

app.exec()

"""
① Common Qt widgets are always imported from the QtWidgets namespace. 
② We must always call the __init__ method of the super() class. 
③ Use .setCentralWidget to place a widget in the QMainWindow.
"""