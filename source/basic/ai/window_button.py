import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QPushButton

# Create the application instance
app = QApplication(sys.argv)

# Create the main window
window = QMainWindow()
window.setWindowTitle("Window with a Button")
window.setGeometry(100, 100, 600, 400)

# Create a button
button = QPushButton("Click Me")
button.setFixedSize(200, 50)  # Optional: set button size

# Set the button as the central widget
window.setCentralWidget(button)

# Show the window
window.show()

# Run the application's event loop
sys.exit(app.exec())