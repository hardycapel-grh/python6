from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel
from PySide6.QtCore import Qt

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

from logger import logger


class ChartsPage(QWidget):
    def __init__(self):
        super().__init__()
        self.title = "Charts"
        self.read_only = True
        self.build_ui()

    def build_ui(self):
        layout = QVBoxLayout()

        label = QLabel("Charts Page")
        label.setAlignment(Qt.AlignCenter)
        layout.addWidget(label)

        # Matplotlib Figure + Canvas
        self.figure = Figure(figsize=(5, 4))
        self.canvas = FigureCanvas(self.figure)
        layout.addWidget(self.canvas)

        self.setLayout(layout)

        # Draw initial chart
        self.draw_sample_chart()

    def draw_sample_chart(self):
        """
        Draws a simple example chart so you can confirm matplotlib is working.
        Replace this with real data later.
        """
        try:
            ax = self.figure.add_subplot(111)
            ax.clear()

            # Example data
            x = [1, 2, 3, 4, 5]
            y = [10, 20, 15, 30, 25]

            ax.plot(x, y, marker="o", label="Sample Data")
            ax.set_title("Example Chart")
            ax.set_xlabel("X Axis")
            ax.set_ylabel("Y Axis")
            ax.legend()

            self.canvas.draw()

            logger.info("ChartsPage: Sample chart drawn successfully")

        except Exception as e:
            logger.error(f"ChartsPage: Failed to draw chart: {e}")

    def set_read_only(self, readonly: bool):
        """
        Charts are currently view-only, but this method is required for permission control.
        """
        self.read_only = readonly

        if readonly:
            logger.info("ChartsPage set to read-only mode")
        else:
            logger.info("ChartsPage set to read-write mode (future editable features)")
