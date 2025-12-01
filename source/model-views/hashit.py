import sys
import hashlib
from PySide6.QtWidgets import (
    QApplication, QWidget, QLabel, QLineEdit,
    QPushButton, QGridLayout
)

class HashApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Hash Generator")

        # Widgets
        self.input_md5 = QLineEdit()
        self.input_sha256 = QLineEdit()
        self.btn_md5 = QPushButton("MD5 Input 1")
        self.btn_sha256 = QPushButton("SHA256 Input 2")
        self.result_label = QLabel("Result will appear here")

        # Layout
        layout = QGridLayout()
        layout.addWidget(QLabel("Input 1:"), 0, 0)
        layout.addWidget(self.input_md5, 0, 1)
        layout.addWidget(self.btn_md5, 0, 2)

        layout.addWidget(QLabel("Input 2:"), 1, 0)
        layout.addWidget(self.input_sha256, 1, 1)
        layout.addWidget(self.btn_sha256, 1, 2)

        layout.addWidget(self.result_label, 2, 0, 1, 3)
        self.setLayout(layout)

        # Connections
        self.btn_md5.clicked.connect(self.hash_md5)
        self.btn_sha256.clicked.connect(self.hash_sha256)

    def hash_md5(self):
        text = self.input_md5.text()
        hashed = hashlib.md5(text.encode()).hexdigest()
        self.result_label.setText(f"MD5: {hashed}")

    def hash_sha256(self):
        text = self.input_sha256.text()
        hashed = hashlib.sha256(text.encode()).hexdigest()
        self.result_label.setText(f"SHA256: {hashed}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = HashApp()
    window.show()
    sys.exit(app.exec())