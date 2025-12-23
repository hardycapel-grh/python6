from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QLabel,
    QPushButton, QStackedWidget, QMessageBox
)
from PySide6.QtCore import Qt

from admin_page import AdminPage


class Page(QWidget):
    def __init__(self, text):
        super().__init__()
        layout = QVBoxLayout()
        label = QLabel(text)
        label.setAlignment(Qt.AlignCenter)
        layout.addWidget(label)
        self.setLayout(layout)


class MainApp(QMainWindow):
    def __init__(self, user):
        super().__init__()
        self.setWindowTitle("Main Application")

        try:
            self.username = user["username"]
            self.role = user["role"]
        except KeyError:
            print("[ERROR] Invalid user object passed to MainApp")
            self.username = "Unknown"
            self.role = "guest"

        print(f"[DEBUG] MainApp started for user: {self.username}")
        print(f"[DEBUG] User role: {self.role}")

        self.setup_ui()


    def setup_ui(self):
        print("[DEBUG] Setting up UI...")

        container = QWidget()
        container_layout = QVBoxLayout()

        header = QLabel(f"Logged in as: {self.username} ({self.role})")
        header.setAlignment(Qt.AlignCenter)
        container_layout.addWidget(header)

        # Create pages FIRST (so they always exist)
        self.stack = QStackedWidget()
        self.pages = [
            Page("Dashboard"),
            Page("Data Table"),
            Page("Charts"),
            AdminPage()  # REAL admin page
]


        for p in self.pages:
            self.stack.addWidget(p)

        # Add navigation buttons
        self.add_navigation_buttons(container_layout)

        container_layout.addWidget(self.stack)
        container.setLayout(container_layout)
        self.setCentralWidget(container)


    def add_navigation_buttons(self, layout):
        print("[DEBUG] Applying role-based access rules...")

        if self.role in ["admin", "staff", "viewer"]:
            print("[DEBUG] Enabling Dashboard")
            btn1 = QPushButton("Dashboard")
            btn1.clicked.connect(lambda: self.switch_page(0))
            layout.addWidget(btn1)

        if self.role in ["admin", "staff"]:
            print("[DEBUG] Enabling Datatable")
            btn2 = QPushButton("Datatable")
            btn2.clicked.connect(lambda: self.switch_page(1))
            layout.addWidget(btn2)

        if self.role == "admin":
            print("[DEBUG] Enabling Charts")
            btn3 = QPushButton("Charts")
            btn3.clicked.connect(lambda: self.switch_page(2))
            layout.addWidget(btn3)

        if self.role == "admin":
            print("[DEBUG] Enabling Admin page")
            btn4 = QPushButton("Admin")
            btn4.clicked.connect(lambda: self.switch_page(3))
            layout.addWidget(btn4)


    def switch_page(self, index):
        try:
            print(f"[DEBUG] Switching to page index: {index}")
            self.stack.setCurrentIndex(index)
        except Exception as e:
            print("[ERROR] Failed to switch page:", e)
            QMessageBox.critical(self, "Error", "Could not switch page")