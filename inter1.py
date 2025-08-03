from PySide6.QtWidgets import (
    QApplication, QWidget, QLabel, QLineEdit,
    QHBoxLayout, QVBoxLayout
)
import sys

class InputForm(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Registration Form")

        # Row 1 – Name
        name_label = QLabel("Name:")
        name_input = QLineEdit()
        name_input.setFixedWidth(200)
        row1 = QHBoxLayout()
        row1.addWidget(name_label)
        row1.addWidget(name_input)

        # Row 2 – Email
        email_label = QLabel("Email:")
        email_input = QLineEdit()
        email_input.setFixedWidth(200)
        row2 = QHBoxLayout()
        row2.addWidget(email_label)
        row2.addWidget(email_input)

        # Row 3 – Age
        age_label = QLabel("Age:")
        age_input = QLineEdit()
        age_input.setFixedWidth(100)
        row3 = QHBoxLayout()
        row3.addWidget(age_label)
        row3.addWidget(age_input)

        # Stack all rows vertically
        main_layout = QVBoxLayout()
        main_layout.addLayout(row1)
        main_layout.addLayout(row2)
        main_layout.addLayout(row3)

        self.setLayout(main_layout)
        self.resize(350, 160)

app = QApplication(sys.argv)
form = InputForm()
form.show()
app.exec()
