import sys
import qrc_resources  # Registers the resource paths
from PySide6.QtWidgets import QApplication, QMainWindow
from ui_main import Ui_MainWindow  # Adjust this to match your filename



from PySide6.QtWidgets import QPushButton
from PySide6.QtGui import QIcon

button = QPushButton("Click Me")
button.setIcon(QIcon(":/icons/my_icon.png"))  # Use the :/ prefix

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
