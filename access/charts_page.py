from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QLineEdit, QTextEdit, QComboBox, QPushButton
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

    def set_read_only(self, ro: bool):
        """Enable or disable editing for all input widgets."""
        for widget in self.findChildren((QLineEdit, QTextEdit, QComboBox)):
            if isinstance(widget, QLineEdit):
                widget.setReadOnly(ro)
            elif isinstance(widget, QTextEdit):
                widget.setReadOnly(ro)
            elif isinstance(widget, QComboBox):
                widget.setEnabled(not ro)

        # Disable buttons that modify data
        for btn in self.findChildren(QPushButton):
            if btn.objectName() not in ("nav", "close", "back"):
                btn.setEnabled(not ro)
