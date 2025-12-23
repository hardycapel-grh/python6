from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QHBoxLayout,
    QComboBox, QPushButton, QMessageBox
)
from database import get_all_users, update_user_role


class AdminPage(QWidget):
    def __init__(self):
        super().__init__()

        layout = QVBoxLayout()
        layout.addWidget(QLabel("Admin Panel – Manage User Roles"))

        self.user_rows = []  # store row widgets for refresh

        self.layout = layout
        self.refresh_user_list()

        self.setLayout(layout)

    def refresh_user_list(self):
        # Clear old rows
        for row in self.user_rows:
            for widget in row:
                widget.setParent(None)
        self.user_rows.clear()

        users = get_all_users()

        for user in users:
            username = user["username"]
            role = user["role"]

            row_layout = QHBoxLayout()

            # Username label
            label = QLabel(username)
            row_layout.addWidget(label)

            # Role dropdown
            role_box = QComboBox()
            role_box.addItems(["admin", "staff", "viewer", "guest"])
            role_box.setCurrentText(role)
            row_layout.addWidget(role_box)

            # Save button
            save_btn = QPushButton("Save")
            save_btn.clicked.connect(
                lambda _, u=username, box=role_box: self.save_role(u, box)
            )
            row_layout.addWidget(save_btn)

            self.layout.addLayout(row_layout)
            self.user_rows.append((label, role_box, save_btn))

    def save_role(self, username, role_box):
        new_role = role_box.currentText()

        if update_user_role(username, new_role):
            QMessageBox.information(self, "Success", f"Updated {username} to {new_role}")
            print(f"[DEBUG] Updated {username} → {new_role}")
        else:
            QMessageBox.critical(self, "Error", "Failed to update role")
            print("[ERROR] Role update failed")
            