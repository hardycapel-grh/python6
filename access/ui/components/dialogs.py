from PySide6.QtWidgets import QMessageBox

def show_access_denied(parent=None):
    QMessageBox.warning(parent, "Access Denied",
                        "You do not have permission to access this feature.")

