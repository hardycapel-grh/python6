from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QMessageBox, QComboBox
)
from bson.objectid import ObjectId
from ui.components.permissions_selector_widget import PermissionsSelectorWidget



class AddUserDialog(QDialog):
    def __init__(self, mongo, current_user, parent=None):
        super().__init__(parent)
        self.mongo = mongo
        self.current_user = current_user

        self.setWindowTitle("Add User")

        layout = QVBoxLayout(self)

        # Username
        layout.addWidget(QLabel("Username"))
        self.username = QLineEdit()
        layout.addWidget(self.username)



        # Password
        layout.addWidget(QLabel("Password"))
        self.password = QLineEdit()
        self.password.setEchoMode(QLineEdit.Password)
        layout.addWidget(self.password)

        # Email
        layout.addWidget(QLabel("Email"))
        self.email = QLineEdit()
        layout.addWidget(self.email)

        # Role
        layout.addWidget(QLabel("Role"))
        self.role = QComboBox()
        self.role.addItems(["viewer", "user", "manager", "admin"])
        layout.addWidget(self.role)

        # Buttons
        btns = QHBoxLayout()
        save = QPushButton("Create")
        cancel = QPushButton("Cancel")
        save.clicked.connect(self._create_user)
        cancel.clicked.connect(self.reject)
        btns.addWidget(save)
        btns.addWidget(cancel)
        layout.addLayout(btns)

    def _create_user(self):
        username = self.username.text().strip()
        email = self.email.text().strip()
        password = self.password.text().strip()
        role = self.role.currentText()

        if not username or not email or not password:
            QMessageBox.warning(self, "Missing Data", "All fields are required.")
            return

        try:
            user_doc = {
                "username": username,
                "email": email,
                "password_hash": self.mongo.hash_password(password),
                "role": role,
                "status": "Active",
                "created_at": "now",
                "last_login": None,
                "theme": "light"
            }

            self.mongo.create_user(user_doc, performed_by=self.current_user.username)
            self.accept()

        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))


class EditUserDialog(QDialog):
    def __init__(self, mongo, user_data, current_user, parent=None):
        super().__init__(parent)
        self.mongo = mongo
        self.user_data = user_data
        self.current_user = current_user

        self.setWindowTitle(f"Edit User: {user_data.get('username')}")

        layout = QVBoxLayout(self)

        # Email
        layout.addWidget(QLabel("Email"))
        self.email = QLineEdit(user_data.get("email", ""))
        layout.addWidget(self.email)

        # Role
        layout.addWidget(QLabel("Role"))
        self.role = QComboBox()
        self.role.addItems(["viewer", "user", "manager", "admin"])
        self.role.setCurrentText(user_data.get("role", "viewer"))
        layout.addWidget(self.role)

        # Status
        layout.addWidget(QLabel("Status"))
        self.status = QComboBox()
        self.status.addItems(["Active", "Disabled"])
        self.status.setCurrentText(user_data.get("status", "Active"))
        layout.addWidget(self.status)

        self.permissions_widget = PermissionsSelectorWidget(
            self.mongo,
            selected=self.user_data.get("permissions", [])
        )
        layout.addWidget(self.permissions_widget)


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
        update_doc = {
            "email": self.email.text().strip(),
            "role": self.role.currentText(),
            "status": self.status.currentText()
        }

        # NEW: collect selected permissions from the widget
        updated_permissions = self.permissions_widget.get_selected_permissions()

        try:
            # Update basic fields
            self.mongo.update_user(
                self.user_data["_id"],
                update_doc,
                performed_by=self.current_user.username
            )

            # NEW: update permissions override
            self.mongo.update_user_permissions(
                self.user_data["_id"],
                updated_permissions,
                performed_by=self.current_user.username
            )

            self.accept()

        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))



class DeleteUserDialog(QDialog):
    def __init__(self, mongo, user_data, current_user, parent=None):
        super().__init__(parent)
        self.mongo = mongo
        self.user_data = user_data
        self.current_user = current_user

        self.setWindowTitle("Delete User")

        layout = QVBoxLayout(self)
        layout.addWidget(QLabel(f"Delete user '{user_data.get('username')}'?"))

        btns = QHBoxLayout()
        yes = QPushButton("Delete")
        no = QPushButton("Cancel")
        yes.clicked.connect(self._delete)
        no.clicked.connect(self.reject)
        btns.addWidget(yes)
        btns.addWidget(no)
        layout.addLayout(btns)

    def _delete(self):
        try:
            self.mongo.delete_user(
                self.user_data["_id"],
                performed_by=self.current_user.username
            )
            self.accept()

        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))


class ResetPasswordDialog(QDialog):
    def __init__(self, mongo, user_data, current_user, parent=None):
        super().__init__(parent)
        self.mongo = mongo
        self.user_data = user_data
        self.current_user = current_user

        self.setWindowTitle("Reset Password")

        layout = QVBoxLayout(self)

        layout.addWidget(QLabel(f"Reset password for '{user_data.get('username')}'"))
        layout.addWidget(QLabel("New Password"))
        self.new_pw = QLineEdit()
        self.new_pw.setEchoMode(QLineEdit.Password)
        layout.addWidget(self.new_pw)

        btns = QHBoxLayout()
        save = QPushButton("Reset")
        cancel = QPushButton("Cancel")
        save.clicked.connect(self._reset)
        cancel.clicked.connect(self.reject)
        btns.addWidget(save)
        btns.addWidget(cancel)
        layout.addLayout(btns)

    def _reset(self):
        new_pw = self.new_pw.text().strip()

        if len(new_pw) < 6:
            QMessageBox.warning(self, "Error", "Password must be at least 6 characters.")
            return

        try:
            self.mongo.reset_password(
                self.user_data["_id"],
                new_pw,
                performed_by=self.current_user.username
            )
            self.accept()

        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))
