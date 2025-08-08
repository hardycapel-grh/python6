import sys
from PySide6.QtWidgets import QApplication, QMainWindow

# Create the application instance
app = QApplication(sys.argv)

# Create the main window
window = QMainWindow()
window.setWindowTitle("My First PySide6 Window")
window.setGeometry(100, 100, 600, 400)  # x, y, width, height

# Show the window
window.show()

# Run the application's event loop
sys.exit(app.exec())