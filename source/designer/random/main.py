import sys
import random
from PySide6.QtWidgets import QApplication, QMainWindow
from PySide6.QtGui import QFont
from ui_random import Ui_MainWindow  # This is your converted UI file

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        # Optional: make label font larger
        self.ui.numberLabel.setFont(QFont("Arial", 24))

        # Connect button to function
        self.ui.generateButton.clicked.connect(self.generate_number)

        # Optional reset button
        if hasattr(self.ui, 'resetButton'):
            self.ui.resetButton.clicked.connect(self.reset_label)

    def generate_number(self):
        number = random.randint(1, 100)
        self.ui.numberLabel.setText(str(number))

    def reset_label(self):
        self.ui.numberLabel.setText("0")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())