from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QPushButton, QMessageBox
)


class ProfileDialog(QDialog):
    def __init__(self, mongo, user, parent=None):
        super().__init__(parent)
        self.mongo = mongo
        self.user = user
        self.setWindowTitle("My Profile")

        layout = QVBoxLayout(self)

        # Email
        layout.addWidget(QLabel("Email"))
        self.email = QLineEdit(user.get("email", ""))
        layout.addWidget(self.email)

        # Phone
        layout.addWidget(QLabel("Phone"))
        self.phone = QLineEdit(user.get("phone", ""))
        layout.addWidget(self.phone)

        # Theme
        layout.addWidget(QLabel("Theme"))
        self.theme = QLineEdit(user.get("theme", "light"))
        layout.addWidget(self.theme)

        # Buttons
        btns = QHBoxLayout()
        save = QPushButton("Save")
        cancel = QPushButton("Cancel")
        save.clicked.connect(self._save)
        cancel.clicked.connect(self.reject)
        btns.addWidget(save)
        btns.addWidget(cancel)
        layout.addLayout(btns)

    def _save(self):
        fields = {
            "email": self.email.text().strip(),
            "phone": self.phone.text().strip(),
            "theme": self.theme.text().strip()
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

        layout.addWidget(QLabel("Current Password"))
        self.old_pw = QLineEdit()
        self.old_pw.setEchoMode(QLineEdit.Password)
        layout.addWidget(self.old_pw)

        layout.addWidget(QLabel("New Password"))
        self.new_pw = QLineEdit()
        self.new_pw.setEchoMode(QLineEdit.Password)
        layout.addWidget(self.new_pw)

        layout.addWidget(QLabel("Confirm New Password"))
        self.confirm_pw = QLineEdit()
        self.confirm_pw.setEchoMode(QLineEdit.Password)
        layout.addWidget(self.confirm_pw)

        btns = QHBoxLayout()
        save = QPushButton("Change")
        cancel = QPushButton("Cancel")
        save.clicked.connect(self._change)
        cancel.clicked.connect(self.reject)
        btns.addWidget(save)
        btns.addWidget(cancel)
        layout.addLayout(btns)

    def _change(self):
        old_pw = self.old_pw.text().strip()
        new_pw = self.new_pw.text().strip()
        confirm = self.confirm_pw.text().strip()

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
