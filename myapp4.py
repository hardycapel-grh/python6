import sys

from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QPushButton,
)  # <1>


# Subclass QMainWindow to customize your application's main window
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()  # <2>

        self.setWindowTitle("My App")

        button = QPushButton("Press Me!")

        # Set the central widget of the Window.
        self.setCentralWidget(button)  # <3>


app = QApplication(sys.argv)

window = MainWindow()
window.show()

app.exec()

"""
① Common Qt widgets are always imported from the QtWidgets namespace. 
② We must always call the __init__ method of the super() class. 
③ Use .setCentralWidget to place a widget in the QMainWindow.
"""

# Explanation of the code:
# - Imports
# - The code imports necessary classes from PySide6 for creating a GUI application.
# - sys is used to pass command-line arguments to the Qt application.
# - QApplication manages the GUI application lifecycle.
# - QMainWindow is the base class for main windows with features like toolbars and status bars.
# - QPushButton creates an interactive button widget.

# 🏗️ Custom Main Window Class
# class MainWindow(QMainWindow):
#     def __init__(self):
#         super().__init__()


# - You’re subclassing QMainWindow to customize its behavior.
# - super().__init__() ensures the base class is initialized properly.

# 🪟 Window Setup
# self.setWindowTitle("My App")
# button = QPushButton("Press Me!")
# self.setCentralWidget(button)


# - Sets the window title.
# - Creates a button widget.
# - setCentralWidget(button) places the button in the central area of the window — the main content area.
# You could later swap this out for a layout or container widget to hold multiple items.

# 🚀 Application Execution
# app = QApplication(sys.argv)
# window = MainWindow()
# window.show()
# app.exec()


# - QApplication initializes the Qt system.
# - You create your custom window and display it using show().
# - app.exec() starts the main event loop, keeping the app responsive to user interactions.
