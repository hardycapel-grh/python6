from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QLineEdit, QLabel,
    QPushButton, QHBoxLayout, QMessageBox
)

from PySide6.QtGui import QPalette, QColor
from PySide6.QtCore import Qt

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

        ok, err = self.mongo.create_user(
            username=self.username.text(),
            password=self.password.text(),
            permissions=None,          # triggers default permissions
            email=self.email.text(),
            role="user",               # default role
            phone=self.phone.text(),
            must_change_password=False
        )

        if not ok:
            QMessageBox.warning(self, "Error", err)
            return

        self.accept()


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

        fields = {
            "email": self.email.text(),
            "phone": self.phone.text()
        }

        self.mongo.update_user_fields(self.user_data["username"], fields)
        self.accept()

class DeleteUserDialog(QDialog):
    def __init__(self, mongo, username, parent=None):
        super().__init__(parent)
        self.mongo = mongo
        self.username = username
        self.setWindowTitle("Delete User")

        layout = QVBoxLayout(self)
        layout.addWidget(QLabel(f"Are you sure you want to delete '{username}'?"))

        btns = QHBoxLayout()
        yes = QPushButton("Delete")
        no = QPushButton("Cancel")
        yes.clicked.connect(self.delete_user)
        no.clicked.connect(self.reject)
        btns.addWidget(yes)
        btns.addWidget(no)
        layout.addLayout(btns)

    def delete_user(self):
        self.mongo.db.users.delete_one({"username": self.username})
        self.accept()

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QLineEdit, QLabel,
    QPushButton, QHBoxLayout, QMessageBox
)
from PySide6.QtCore import Qt


class ResetPasswordDialog(QDialog):
    def __init__(self, mongo, username, parent=None):
        super().__init__(parent)
        self.mongo = mongo
        self.username = username
        self.setWindowTitle(f"Reset Password: {username}")

        layout = QVBoxLayout(self)

        # -------------------------
        # Input field
        # -------------------------
        self.new_pw = QLineEdit()
        self.new_pw.setEchoMode(QLineEdit.Password)

        # Strength indicator
        self.pw_strength = QLabel("")
        self.pw_strength.setStyleSheet("font-weight: bold;")

        layout.addWidget(QLabel("New Password"))
        layout.addWidget(self.new_pw)
        layout.addWidget(self.pw_strength)

        # -------------------------
        # Buttons
        # -------------------------
        btns = QHBoxLayout()
        save = QPushButton("Reset")
        cancel = QPushButton("Cancel")

        save.clicked.connect(self.reset_pw)
        cancel.clicked.connect(self.reject)

        btns.addWidget(save)
        btns.addWidget(cancel)
        layout.addLayout(btns)

        # -------------------------
        # Behaviour enhancements
        # -------------------------
        self.new_pw.setFocus()  # Autofocus

        # Live strength indicator
        self.new_pw.textChanged.connect(self.update_pw_strength)

        # Enter submits
        self.new_pw.returnPressed.connect(self.reset_pw)

    # -------------------------------------------------
    # Password strength indicator
    # -------------------------------------------------
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

    # -------------------------------------------------
    # Validation
    # -------------------------------------------------
    def validate_inputs(self):
        pw = self.new_pw.text().strip()

        if not pw:
            return False, "Password is required."

        if len(pw) < 6:
            return False, "Password must be at least 6 characters."

        return True, None

    # -------------------------------------------------
    # Reset password (calls MongoService)
    # -------------------------------------------------
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QLineEdit, QLabel,
    QPushButton, QHBoxLayout, QMessageBox
)
from PySide6.QtCore import Qt


from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QLineEdit, QLabel,
    QPushButton, QHBoxLayout, QMessageBox
)
from PySide6.QtCore import Qt


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
        # print("DEBUG: mongo is", type(self.mongo))
        # print("DEBUG: mongo class:", self.mongo.__class__, "module:", self.mongo.__class__.__module__)
        valid, err = self.validate_inputs()
        if not valid:
            QMessageBox.warning(self, "Invalid Input", err)
            return

        ok, err = self.mongo.reset_password(
            username=self.username,
            new_password=self.new_pw.text(),
            force_change=False
        )

        if not ok:
            QMessageBox.warning(self, "Error", err)
            return

        self.accept()

        # Show toast on parent window
        from ui.components.toast import Toast
        Toast(self.parent(), "Password reset successfully")