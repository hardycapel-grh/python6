import sys

from PySide6.QtWidgets import QApplication, QMainWindow
from PySide6 import QtCore

import pyqtgraph as pg  # import PyQtGraph after PySide6


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.graphWidget = pg.PlotWidget()
        self.setCentralWidget(self.graphWidget)

        hour = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
        temperature = [30, 32, 34, 32, 33, 31, 29, 32, 35, 45]

        # self.graphWidget.setBackground("w")
        self.graphWidget.setBackground("beige") # Change background color to beige

        # pen = pg.mkPen(color=(255, 0, 0))
        pen = pg.mkPen(color=(255, 0, 0), width=15, style=QtCore.Qt.DashLine)  # Make the line thicker
        self.graphWidget.plot(hour, temperature, pen=pen)


app = QApplication(sys.argv)
main = MainWindow()
main.show()
app.exec()
