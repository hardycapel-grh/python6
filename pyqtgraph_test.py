import sys
import numpy as np
from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout
import pyqtgraph as pg

class PlotApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PySide6 + pyqtgraph Example")

        layout = QVBoxLayout()

        # Create a PlotWidget
        self.plot_widget = pg.PlotWidget()
        layout.addWidget(self.plot_widget)

        # Generate data
        x = np.linspace(0, 2*np.pi, 100)
        y = np.sin(x)

        # Plot data
        self.plot_widget.plot(x, y, pen=pg.mkPen(color="b", width=2))

        self.setLayout(layout)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = PlotApp()
    window.show()
    sys.exit(app.exec())