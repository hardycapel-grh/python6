import sys
import random
import qrc_resources  # Registers the resource paths
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QApplication, QMainWindow
from ui_random import Ui_MainWindow  # This is your converted UI file



class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.ui.generateButton.setIcon(QIcon(":/icons/home_24dp_E3E3E3_FILL0_wght400_GRAD0_opsz24.png"))
        self.ui.generateButton.clicked.connect(self.generate_number)

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
