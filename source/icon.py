from PySide6.QtWidgets import QApplication, QPushButton
from PySide6.QtGui import QIcon
import sys

app = QApplication(sys.argv)

button = QPushButton("Click Me")
button.setIcon(QIcon("basic/fugue-icons-3.5.6/icons/open-source.png"))  # Use absolute or relative path
button.setIconSize(button.sizeHint())  # Optional: scale icon to button size

button.show()
sys.exit(app.exec())