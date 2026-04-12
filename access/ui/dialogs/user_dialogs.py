from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QLineEdit, QLabel,
    QPushButton, QHBoxLayout, QMessageBox
)

from PySide6.QtGui import QPalette, QColor
from PySide6.QtCore import Qt
from datetime import datetime

class AddUserDialog(QDialog):
    def __init__(self, mongo, parent=None):
        super().__init__(parent)
        self.mongo = mongo
        self.setWindowTitle("Add User")

        layout = QVBoxLayout(self)

        # -------------------------
        # Input fields
        # -------------------------
        self.username = QLineEdit()
        self.password = QLineEdit()
        self.password.setEchoMode(QLineEdit.Password)
        self.email = QLineEdit()
        self.phone = QLineEdit()

        # Password strength label
        self.pw_strength = QLabel("")
        self.pw_strength.setStyleSheet("font-weight: bold;")

        layout.addWidget(QLabel("Username"))
        layout.addWidget(self.username)

        layout.addWidget(QLabel("Password"))
        layout.addWidget(self.password)
        layout.addWidget(self.pw_strength)

        layout.addWidget(QLabel("Email"))
        layout.addWidget(self.email)

        layout.addWidget(QLabel("Phone"))
        layout.addWidget(self.phone)

        # -------------------------
        # Buttons
        # -------------------------
        btns = QHBoxLayout()
        save = QPushButton("Create")
        cancel = QPushButton("Cancel")

        save.clicked.connect(self.create_user)
        cancel.clicked.connect(self.reject)

        btns.addWidget(save)
        btns.addWidget(cancel)
        layout.addLayout(btns)

        # -------------------------
        # Behaviour enhancements
        # -------------------------
        self.username.setFocus()                 # Autofocus
        self.password.textChanged.connect(self.update_pw_strength)

        # Enter submits the form
        self.username.returnPressed.connect(self.create_user)
        self.password.returnPressed.connect(self.create_user)
        self.email.returnPressed.connect(self.create_user)
        self.phone.returnPressed.connect(self.create_user)

    # -------------------------------------------------
    # Password strength indicator
    # -------------------------------------------------
    def update_pw_strength(self):
        pw = self.password.text()

        if len(pw) < 6:
            self.pw_strength.setText("Weak")
            self.pw_strength.setStyleSheet("color: red; font-weight: bold;")
            return

        score = 0
        if any(c.islower() for c in pw): score += 1
        if any(c.isupper() for c in pw): score += 1
        if any(c.isdigit() for c in pw): score += 1
        if any(not c.isalnum() for c in pw): score += 1

        if score <= 1:
            self.pw_strength.setText("Weak")
            self.pw_strength.setStyleSheet("color: red; font-weight: bold;")
        elif score == 2:
            self.pw_strength.setText("Medium")
            self.pw_strength.setStyleSheet("color: orange; font-weight: bold;")
        else:
            self.pw_strength.setText("Strong")
            self.pw_strength.setStyleSheet("color: green; font-weight: bold;")

    # -------------------------------------------------
    # Validation
    # -------------------------------------------------
    def validate_inputs(self):
        if not self.username.text().strip():
            return False, "Username is required."

        if not self.password.text().strip():
            return False, "Password is required."

        email = self.email.text().strip()
        if not email:
            return False, "Email is required."

        if "@" not in email or "." not in email:
            return False, "Email format looks invalid."

        return True, None

    # -------------------------------------------------
    # Create user (calls MongoService)
    # -------------------------------------------------
    def create_user(self):
        valid, err = self.validate_inputs()
        if not valid:
            QMessageBox.warning(self, "Invalid Input", err)
            return

        user_doc = {
            "username": self.username.text(),
            "email": self.email.text(),
            "phone": self.phone.text(),
            "password_hash": self.mongo.hash_password(self.password.text()),
            "role": "user",
            "status": "Active",
            "created_at": datetime.utcnow().isoformat(),
            "last_login": None,
            "theme": "light"
        }

        try:
            self.mongo.create_user(
                user_doc,
                performed_by=self.parent().current_user.username
            )
            self.accept()

        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))




class EditUserDialog(QDialog):
    def __init__(self, mongo, user_data, parent=None):
        super().__init__(parent)
        self.mongo = mongo
        self.user_data = user_data
        self.setWindowTitle(f"Edit User: {user_data['username']}")

        layout = QVBoxLayout(self)

        # -------------------------
        # Input fields
        # -------------------------
        self.email = QLineEdit(user_data.get("email", ""))
        self.phone = QLineEdit(user_data.get("phone", ""))

        layout.addWidget(QLabel("Email"))
        layout.addWidget(self.email)

        layout.addWidget(QLabel("Phone"))
        layout.addWidget(self.phone)

        # -------------------------
        # Buttons
        # -------------------------
        btns = QHBoxLayout()
        save = QPushButton("Save")
        cancel = QPushButton("Cancel")

        save.clicked.connect(self.save_changes)
        cancel.clicked.connect(self.reject)

        btns.addWidget(save)
        btns.addWidget(cancel)
        layout.addLayout(btns)

        # -------------------------
        # Behaviour enhancements
        # -------------------------
        self.email.setFocus()  # Autofocus on first editable field

        # Enter submits the form
        self.email.returnPressed.connect(self.save_changes)
        self.phone.returnPressed.connect(self.save_changes)

    # -------------------------------------------------
    # Validation
    # -------------------------------------------------
    def validate_inputs(self):
        email = self.email.text().strip()

        if not email:
            return False, "Email is required."

        if "@" not in email or "." not in email:
            return False, "Email format looks invalid."

        return True, None

    # -------------------------------------------------
    # Save changes (calls MongoService)
    # -------------------------------------------------
    def save_changes(self):
        valid, err = self.validate_inputs()
        if not valid:
            QMessageBox.warning(self, "Invalid Input", err)
            return

        update_doc = {
            "email": self.email.text(),
            "phone": self.phone.text()
        }

        try:
            self.mongo.update_user(
                self.user_data["_id"],
                update_doc,
                performed_by=self.parent().current_user.username
            )
            self.accept()

        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))



class DeleteUserDialog(QDialog):
    def __init__(self, mongo, user_data, parent=None):
        super().__init__(parent)
        self.mongo = mongo
        self.user_data = user_data
        self.setWindowTitle("Delete User")

        layout = QVBoxLayout(self)
        layout.addWidget(QLabel(f"Are you sure you want to delete '{user_data['username']}'?"))

        btns = QHBoxLayout()
        yes = QPushButton("Delete")
        no = QPushButton("Cancel")
        yes.clicked.connect(self.delete_user)
        no.clicked.connect(self.reject)
        btns.addWidget(yes)
        btns.addWidget(no)
        layout.addLayout(btns)

    def delete_user(self):
        try:
            self.mongo.delete_user(
                self.user_data["_id"],
                performed_by=self.parent().current_user.username
            )
            self.accept()

        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))


class ResetPasswordDialog(QDialog):
    def __init__(self, mongo, username, parent=None):
        super().__init__(parent)
        self.mongo = mongo
        self.username = username
        self.setWindowTitle(f"Reset Password: {username}")

        layout = QVBoxLayout(self)

        self.new_pw = QLineEdit()
        self.new_pw.setEchoMode(QLineEdit.Password)

        self.pw_strength = QLabel("")
        self.pw_strength.setStyleSheet("font-weight: bold;")

        layout.addWidget(QLabel("New Password"))
        layout.addWidget(self.new_pw)
        layout.addWidget(self.pw_strength)

        btns = QHBoxLayout()
        save = QPushButton("Reset")
        cancel = QPushButton("Cancel")

        save.clicked.connect(self.reset_pw)      # ← important
        cancel.clicked.connect(self.reject)

        btns.addWidget(save)
        btns.addWidget(cancel)
        layout.addLayout(btns)

        self.new_pw.setFocus()
        self.new_pw.textChanged.connect(self.update_pw_strength)
        self.new_pw.returnPressed.connect(self.reset_pw)

    def update_pw_strength(self):
        pw = self.new_pw.text()
        if len(pw) < 6:
            self.pw_strength.setText("Weak")
            self.pw_strength.setStyleSheet("color: red; font-weight: bold;")
            return

        score = 0
        if any(c.islower() for c in pw): score += 1
        if any(c.isupper() for c in pw): score += 1
        if any(c.isdigit() for c in pw): score += 1
        if any(not c.isalnum() for c in pw): score += 1

        if score <= 1:
            self.pw_strength.setText("Weak")
            self.pw_strength.setStyleSheet("color: red; font-weight: bold;")
        elif score == 2:
            self.pw_strength.setText("Medium")
            self.pw_strength.setStyleSheet("color: orange; font-weight: bold;")
        else:
            self.pw_strength.setText("Strong")
            self.pw_strength.setStyleSheet("color: green; font-weight: bold;")

    def validate_inputs(self):
        pw = self.new_pw.text().strip()
        if not pw:
            return False, "Password is required."
        if len(pw) < 6:
            return False, "Password must be at least 6 characters."
        return True, None

    def reset_pw(self):
        valid, err = self.validate_inputs()
        if not valid:
            QMessageBox.warning(self, "Invalid Input", err)
            return

        try:
            self.mongo.reset_password(
                self.user_data["_id"],
                self.new_pw.text(),
                performed_by=self.parent().current_user.username
            )
            self.accept()

            from ui.components.toast import Toast
            Toast(self.parent(), "Password reset successfully")

        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

