# Import necessary PySide6 widgets and layout classes
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QHBoxLayout

# Import Qt alignment constants
from PySide6.QtCore import Qt

# Define Page1 class, inheriting from QWidget
class Page1(QWidget):
    def __init__(self, switch_function):  # Accepts a function to switch pages
        super().__init__()  # Initialize the base QWidget

        # Create a vertical layout to stack widgets top-to-bottom
        layout = QVBoxLayout()

        # Create a centered label as the page header
        label = QLabel("Welcome to Page 1 — your starting point!")
        label.setAlignment(Qt.AlignCenter)  # Center-align the label text
        layout.addWidget(label)             # Add label to the vertical layout
        layout.addStretch()                 # Add flexible space below the label

        # Create a horizontal layout to hold navigation buttons
        button_layout = QHBoxLayout()

        # Generate four navigation buttons dynamically
        for i in range(4):
            btn = QPushButton(f"Go to Page {i + 1}")  # Label each button
            # Connect button click to switch_function with the correct page index
            btn.clicked.connect(lambda _, target=i: switch_function(target))
            button_layout.addWidget(btn)  # Add button to the horizontal layout

        # Add the button row to the main vertical layout
        layout.addLayout(button_layout)
        layout.addStretch()  # Add flexible space below the buttons

        # Apply the layout to this widget
        self.setLayout(layout)