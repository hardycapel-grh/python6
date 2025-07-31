import sys
from PySide6.QtWidgets import (
    QApplication, QLabel, QLineEdit, QPushButton,
    QVBoxLayout, QHBoxLayout, QWidget, QMessageBox
)

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Input Form")

        # Create input labels and fields
        self.input1 = QLineEdit()
        self.input2 = QLineEdit()
        self.input3 = QLineEdit()

        layout_inputs = QVBoxLayout()
        layout_inputs.addWidget(QLabel("Input 1:"))
        layout_inputs.addWidget(self.input1)
        layout_inputs.addWidget(QLabel("Input 2:"))
        layout_inputs.addWidget(self.input2)
        layout_inputs.addWidget(QLabel("Input 3:"))
        layout_inputs.addWidget(self.input3)

        # Create buttons
        ok_button = QPushButton("OK")
        cancel_button = QPushButton("Cancel")
        ok_button.clicked.connect(self.on_ok)
        cancel_button.clicked.connect(self.on_cancel)

        layout_buttons = QHBoxLayout()
        layout_buttons.addWidget(ok_button)
        layout_buttons.addWidget(cancel_button)

        # Combine layouts
        main_layout = QVBoxLayout()
        main_layout.addLayout(layout_inputs)
        main_layout.addLayout(layout_buttons)

        self.setLayout(main_layout)
        self.resize(400, 300)

    def on_ok(self):
        data = (
            f"Input 1: {self.input1.text()}\n"
            f"Input 2: {self.input2.text()}\n"
            f"Input 3: {self.input3.text()}"
        )
        QMessageBox.information(self, "Submitted Data", data)

    def on_cancel(self):
        self.input1.clear()
        self.input2.clear()
        self.input3.clear()

app = QApplication(sys.argv)
window = MainWindow()
window.show()
app.exec()