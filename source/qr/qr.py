# Import system module for application control
import sys

# Import qrcode library to generate QR codes
import qrcode

# Import necessary PySide6 widgets and image handling classes
from PySide6.QtWidgets import QApplication, QLabel, QLineEdit, QPushButton, QVBoxLayout, QWidget
from PySide6.QtGui import QPixmap, QImage

# Import BytesIO to handle image data in memory
from io import BytesIO

# Function to generate a QR code from input text
def generate_qr(data):
    qr = qrcode.make(data)  # Create QR code image from the input string
    buffer = BytesIO()      # Create an in-memory buffer to hold image data
    qr.save(buffer, format='PNG')  # Save QR image to buffer in PNG format
    buffer.seek(0)          # Reset buffer pointer to the beginning
    image = QImage.fromData(buffer.read())  # Convert buffer data to QImage
    return QPixmap.fromImage(image)         # Convert QImage to QPixmap for display

# Main application class for the QR code GUI
class QRApp(QWidget):
    def __init__(self):
        super().__init__()  # Initialize the QWidget base class
        self.setWindowTitle("QR Code Generator")  # Set window title

        # Create a text input field
        self.input = QLineEdit()
        self.input.setPlaceholderText("Enter text or URL")  # Hint text

        # Create a button to trigger QR code generation
        self.button = QPushButton("Generate QR Code")
        self.button.clicked.connect(self.update_qr)  # Connect button click to handler

        # Create a label to display the QR code image
        self.qr_label = QLabel()
        self.qr_label.setFixedSize(200, 200)  # Set fixed size for QR display

        # Arrange widgets vertically
        layout = QVBoxLayout()
        layout.addWidget(self.input)     # Add input field to layout
        layout.addWidget(self.button)    # Add button to layout
        layout.addWidget(self.qr_label)  # Add QR image label to layout
        self.setLayout(layout)           # Apply layout to the main window

    # Function to update the QR code image when button is clicked
    def update_qr(self):
        text = self.input.text()  # Get text from input field
        if text:                  # If text is not empty
            pixmap = generate_qr(text)  # Generate QR code image
            self.qr_label.setPixmap(pixmap.scaled(200, 200))  # Display scaled image

# Entry point of the application
if __name__ == "__main__":
    app = QApplication(sys.argv)  # Create the Qt application
    window = QRApp()              # Instantiate the main window
    window.show()                 # Show the window
    sys.exit(app.exec())          # Run the application event loop