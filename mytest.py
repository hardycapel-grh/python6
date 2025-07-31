import sys
from PySide6.QtWidgets import QApplication, QLabel, QMainWindow, QPushButton, QVBoxLayout, QWidget

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PySide6 + Button")

        # Create widgets
        label = QLabel("👋 Welcome, Graham! Your GUI is ready.")
        ok_button = QPushButton("OK")
        ok_button.clicked.connect(self.on_ok_clicked)

        # Layout setup
        layout = QVBoxLayout()
        layout.addWidget(label)
        layout.addWidget(ok_button)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

    def on_ok_clicked(self):
        print("OK button was clicked!")

app = QApplication(sys.argv)
window = MainWindow()
window.resize(400, 200)
window.show()
app.exec()