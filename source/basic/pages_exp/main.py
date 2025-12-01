# Import system-specific parameters and functions
import sys

# Import necessary PySide6 widgets for GUI application
from PySide6.QtWidgets import QApplication, QMainWindow, QStackedWidget

# Import custom page classes from separate modules
from page1 import Page1
from page2 import Page2
from page3 import Page3
from page4 import Page4

# Define the main window class inheriting from QMainWindow
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()  # Initialize the base QMainWindow

        # Create a QStackedWidget to hold multiple pages
        self.stack = QStackedWidget()

        # Instantiate each page, passing the switch_page method for navigation
        self.pages = [
            Page1(self.switch_page),
            Page2(self.switch_page),
            Page3(self.switch_page),
            Page4(self.switch_page)
        ]

        # Add each page widget to the stacked layout
        for page in self.pages:
            self.stack.addWidget(page)

        # Set the stacked widget as the central widget of the main window
        self.setCentralWidget(self.stack)

        # Display the first page by default
        self.switch_page(0)

    # Method to switch between pages by index
    def switch_page(self, index):
        self.stack.setCurrentIndex(index)  # Change the visible page
        self.setWindowTitle(f"Multi-Page Navigation — Page {index + 1}")  # Update window title

# Entry point of the application
if __name__ == "__main__":
    app = QApplication(sys.argv)  # Create the application instance
    window = MainWindow()         # Instantiate the main window
    window.resize(400, 200)       # Set initial window size
    window.show()                 # Display the window
    sys.exit(app.exec())          # Start the event loop and exit when done