

from PySide6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLineEdit, QLabel, QPushButton, QMessageBox


class ProfileDialog(QDialog):
    def __init__(self, mongo, user, parent=None):
        super().__init__(parent)
        self.mongo = mongo
        self.user = user
        self.setWindowTitle("My Profile")

        layout = QVBoxLayout(self)

        self.email = QLineEdit(user.get("email", ""))
        self.phone = QLineEdit(user.get("phone", ""))
        self.theme = QLineEdit(user.get("theme", "light"))

        layout.addWidget(QLabel("Email"))
        layout.addWidget(self.email)

        layout.addWidget(QLabel("Phone"))
        layout.addWidget(self.phone)

        layout.addWidget(QLabel("Theme"))
        layout.addWidget(self.theme)

        btns = QHBoxLayout()
        save = QPushButton("Save")
        cancel = QPushButton("Cancel")

        save.clicked.connect(self.save_profile)
        cancel.clicked.connect(self.reject)

        btns.addWidget(save)
        btns.addWidget(cancel)
        layout.addLayout(btns)

    def save_profile(self):
        fields = {
            "email": self.email.text(),
            "phone": self.phone.text(),
            "theme": self.theme.text()
        }

        try:
            self.mongo.update_profile(
                self.user["_id"],
                fields,
                performed_by=self.user["username"]
            )
            self.accept()

        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

class ChangePasswordDialog(QDialog):
    def __init__(self, mongo, user, parent=None):
        super().__init__(parent)
        self.mongo = mongo
        self.user = user
        self.setWindowTitle("Change Password")

        layout = QVBoxLayout(self)

        self.old_pw = QLineEdit()
        self.old_pw.setEchoMode(QLineEdit.Password)

        self.new_pw = QLineEdit()
        self.new_pw.setEchoMode(QLineEdit.Password)

        self.confirm_pw = QLineEdit()
        self.confirm_pw.setEchoMode(QLineEdit.Password)

        layout.addWidget(QLabel("Current Password"))
        layout.addWidget(self.old_pw)

        layout.addWidget(QLabel("New Password"))
        layout.addWidget(self.new_pw)

        layout.addWidget(QLabel("Confirm New Password"))
        layout.addWidget(self.confirm_pw)

        btns = QHBoxLayout()
        save = QPushButton("Change")
        cancel = QPushButton("Cancel")

        save.clicked.connect(self.change_pw)
        cancel.clicked.connect(self.reject)

        btns.addWidget(save)
        btns.addWidget(cancel)
        layout.addLayout(btns)

    def change_pw(self):
        old_pw = self.old_pw.text()
        new_pw = self.new_pw.text()
        confirm = self.confirm_pw.text()

        if new_pw != confirm:
            QMessageBox.warning(self, "Error", "Passwords do not match.")
            return

        if len(new_pw) < 6:
            QMessageBox.warning(self, "Error", "Password must be at least 6 characters.")
            return

        try:
            self.mongo.change_password(
                self.user["_id"],
                old_pw,
                new_pw,
                performed_by=self.user["username"]
            )
            self.accept()

        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))
