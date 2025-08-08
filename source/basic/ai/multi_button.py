import sys
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget,
    QVBoxLayout, QPushButton
)

app = QApplication(sys.argv)

# Create the main window
window = QMainWindow()
window.setWindowTitle("Multiple Buttons")
window.setGeometry(100, 100, 400, 300)

# Create a central widget and layout
central_widget = QWidget()
layout = QVBoxLayout()

# Create multiple buttons
button1 = QPushButton("Button 1")
button2 = QPushButton("Button 2")
button3 = QPushButton("Button 3")

# Add buttons to the layout
layout.addWidget(button1)
layout.addWidget(button2)
layout.addWidget(button3)

# Set the layout on the central widget
central_widget.setLayout(layout)

# Set the central widget on the window
window.setCentralWidget(central_widget)

window.show()
sys.exit(app.exec())