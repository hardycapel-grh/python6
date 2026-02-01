from PySide6.QtWidgets import QApplication
from ui.pages.login_page import LoginWindow

app = QApplication([])
window = LoginWindow()
window.show()
app.exec()