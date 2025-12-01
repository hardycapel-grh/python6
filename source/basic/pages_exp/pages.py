import sys
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QPushButton,
    QVBoxLayout, QHBoxLayout, QStackedWidget, QLabel
)
from PySide6.QtCore import Qt

# Page class with optional label on Page 1
class Page(QWidget):
    def __init__(self, page_index, switch_function):
        super().__init__()
        self.page_index = page_index
        self.switch_function = switch_function

        layout = QVBoxLayout()

        # Add a label only to Page 1
        if page_index == 0:
            label = QLabel("Welcome to Page 1 — your starting point!")
            label.setAlignment(Qt.AlignCenter)
            layout.addWidget(label)

        # Add a label only to Page 2
        if page_index == 1:
            label = QLabel("Welcome to Page 2 — for further stuff!")
            label.setAlignment(Qt.AlignCenter)
            layout.addWidget(label) 

        # Add a label only to Page 3
        if page_index == 2:
            label = QLabel("Welcome to Page 3 — boring page!")
            label.setAlignment(Qt.AlignCenter)
            layout.addWidget(label)

        # Add a label only to Page 4
        if page_index == 3:
            label = QLabel("Welcome to Page 4 — the page no one needs!")
            label.setAlignment(Qt.AlignCenter)
            layout.addWidget(label)                        

        layout.addStretch()

        # Create 4 navigation buttons
        button_layout = QHBoxLayout()
        for i in range(4):
            btn = QPushButton(f"Go to Page {i + 1}")
            btn.clicked.connect(lambda _, target=i: self.switch_function(target))
            button_layout.addWidget(btn)

        layout.addLayout(button_layout)
        layout.addStretch()
        self.setLayout(layout)

# Main window with stacked pages
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.stack = QStackedWidget()

        # Create and add 4 pages
        for i in range(4):
            page = Page(i, self.switch_page)
            self.stack.addWidget(page)

        self.setCentralWidget(self.stack)
        self.switch_page(0)  # Start on Page 1

    def switch_page(self, index):
        self.stack.setCurrentIndex(index)
        self.setWindowTitle(f"Multi-Page Navigation — Page {index + 1}")

# Run the application
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.resize(400, 200)
    window.show()
    sys.exit(app.exec())