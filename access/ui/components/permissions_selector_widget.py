from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QCheckBox, QLabel, QScrollArea,
    QLineEdit, QPushButton, QFrame
)
from PySide6.QtCore import Qt


class PermissionsSelectorWidget(QWidget):
    def __init__(self, mongo, selected=None, parent=None):
        super().__init__(parent)

        self.mongo = mongo
        self.selected = set(selected or [])

        layout = QVBoxLayout(self)

        # Title
        title = QLabel("User Permissions (Overrides)")
        title.setStyleSheet("font-weight: bold; margin-bottom: 6px;")
        layout.addWidget(title)

        # Search bar
        self.search = QLineEdit()
        self.search.setPlaceholderText("Search permissions…")
        self.search.textChanged.connect(self._apply_filter)
        layout.addWidget(self.search)

        # Scroll area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        layout.addWidget(scroll)

        container = QWidget()
        self.inner_layout = QVBoxLayout(container)

        # Load permissions
        all_perms = self.mongo.get_all_permissions()

        # Group by category
        self.categories = {}
        for perm in all_perms:
            cat = perm.get("category", "Other")
            self.categories.setdefault(cat, []).append(perm["name"])

        self.checkboxes = {}
        self.category_headers = {}
        self.category_frames = {}

        # Build collapsible sections
        for category, perms in sorted(self.categories.items()):
            # Header button
            header_btn = QPushButton(f"▼  {category}")
            header_btn.setCheckable(True)
            header_btn.setChecked(True)
            header_btn.setStyleSheet(
                "text-align: left; font-weight: bold; margin-top: 10px;"
            )
            self.inner_layout.addWidget(header_btn)
            self.category_headers[category] = header_btn

            # Frame containing the permissions
            frame = QFrame()
            frame_layout = QVBoxLayout(frame)
            frame_layout.setContentsMargins(20, 0, 0, 0)
            self.category_frames[category] = frame

            for name in sorted(perms):
                cb = QCheckBox(name)
                cb.setChecked(name in self.selected)
                self.checkboxes[name] = cb
                frame_layout.addWidget(cb)

            self.inner_layout.addWidget(frame)

            # Toggle collapse
            header_btn.toggled.connect(
                lambda checked, cat=category: self._toggle_category(cat, checked)
            )

            


        self.inner_layout.addStretch()
        scroll.setWidget(container)
        from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QCheckBox, QLabel, QScrollArea,
    QLineEdit, QPushButton, QFrame
)
from PySide6.QtCore import Qt


class PermissionsSelectorWidget(QWidget):
    def __init__(self, mongo, selected=None, parent=None):
        super().__init__(parent)

        self.mongo = mongo
        self.selected = set(selected or [])

        layout = QVBoxLayout(self)

        # Title
        title = QLabel("User Permissions (Overrides)")
        title.setStyleSheet("font-weight: bold; margin-bottom: 6px;")
        layout.addWidget(title)

        # Search bar
        self.search = QLineEdit()
        self.search.setPlaceholderText("Search permissions…")
        self.search.textChanged.connect(self._apply_filter)
        layout.addWidget(self.search)

        # Scroll area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        layout.addWidget(scroll)

        container = QWidget()
        self.inner_layout = QVBoxLayout(container)

        # Load permissions
        all_perms = self.mongo.get_all_permissions()

        # Group by category
        self.categories = {}
        for perm in all_perms:
            cat = perm.get("category", "Other")
            self.categories.setdefault(cat, []).append(perm["name"])

        self.checkboxes = {}
        self.category_headers = {}
        self.category_frames = {}

        # Build collapsible sections
        for category, perms in sorted(self.categories.items()):
            # Header button
            header_btn = QPushButton(f"▼  {category}")
            header_btn.setCheckable(True)
            header_btn.setChecked(True)
            header_btn.setStyleSheet(
                "text-align: left; font-weight: bold; margin-top: 10px;"
            )
            self.inner_layout.addWidget(header_btn)
            self.category_headers[category] = header_btn

            # Frame containing the permissions
            frame = QFrame()
            frame_layout = QVBoxLayout(frame)
            frame_layout.setContentsMargins(20, 0, 0, 0)
            self.category_frames[category] = frame

            for name in sorted(perms):
                cb = QCheckBox(name)
                cb.setChecked(name in self.selected)
                self.checkboxes[name] = cb
                frame_layout.addWidget(cb)

            self.inner_layout.addWidget(frame)

            # Toggle collapse
            header_btn.toggled.connect(
                lambda checked, cat=category: self._toggle_category(cat, checked)
            )

            


        self.inner_layout.addStretch()
        scroll.setWidget(container)
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QCheckBox, QLabel, QScrollArea,
    QLineEdit, QPushButton, QFrame
)
from PySide6.QtCore import Qt


class PermissionsSelectorWidget(QWidget):
    def __init__(self, mongo, selected=None, parent=None):
        super().__init__(parent)

        self.mongo = mongo
        self.selected = set(selected or [])

        layout = QVBoxLayout(self)

        # Title
        title = QLabel("User Permissions (Overrides)")
        title.setStyleSheet("font-weight: bold; margin-bottom: 6px;")
        layout.addWidget(title)

        # Search bar
        self.search = QLineEdit()
        self.search.setPlaceholderText("Search permissions…")
        self.search.textChanged.connect(self._apply_filter)
        layout.addWidget(self.search)

        # Scroll area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        layout.addWidget(scroll)

        container = QWidget()
        self.inner_layout = QVBoxLayout(container)

        # Load permissions
        all_perms = self.mongo.get_all_permissions()

        # Group by category
        self.categories = {}
        for perm in all_perms:
            cat = perm.get("category", "Other")
            self.categories.setdefault(cat, []).append(perm["name"])

        self.checkboxes = {}
        self.category_headers = {}
        self.category_frames = {}

        # Build collapsible sections
        for category, perms in sorted(self.categories.items()):
            # Header button
            header_btn = QPushButton(f"▼  {category}")
            header_btn.setCheckable(True)
            header_btn.setChecked(True)
            header_btn.setStyleSheet(
                "text-align: left; font-weight: bold; margin-top: 10px;"
            )
            self.inner_layout.addWidget(header_btn)
            self.category_headers[category] = header_btn

            # Frame containing the permissions
            frame = QFrame()
            frame_layout = QVBoxLayout(frame)
            frame_layout.setContentsMargins(20, 0, 0, 0)
            self.category_frames[category] = frame

            for name in sorted(perms):
                cb = QCheckBox(name)
                cb.setChecked(name in self.selected)
                self.checkboxes[name] = cb
                frame_layout.addWidget(cb)

            self.inner_layout.addWidget(frame)

            # Toggle collapse
            header_btn.toggled.connect(
                lambda checked, cat=category: self._toggle_category(cat, checked)
            )

            


        self.inner_layout.addStretch()
        scroll.setWidget(container)
        # SAFE: all categories, headers, frames, and checkboxes now exist
        self.expand_categories_with_selected()

    # ---------------------------------------------------------
    # Collapse / expand category
    # ---------------------------------------------------------
    def _toggle_category(self, category, expanded):
        header = self.category_headers[category]
        frame = self.category_frames[category]

        if expanded:
            header.setText(f"▼  {category}")
            frame.show()
        else:
            header.setText(f"►  {category}")
            frame.hide()

    # ---------------------------------------------------------
    # Filtering logic (within each category)
    # ---------------------------------------------------------
    def _apply_filter(self, text):
        text = text.strip().lower()

        for category, perms in self.categories.items():
            any_visible = False

            for name in perms:
                cb = self.checkboxes[name]

                if not text or text in name.lower():
                    cb.show()
                    cb.setEnabled(True)
                    cb.setStyleSheet("")
                    any_visible = True
                else:
                    cb.show()
                    cb.setEnabled(False)
                    cb.setStyleSheet("color: gray;")

            header = self.category_headers[category]
            frame = self.category_frames[category]

            # Dim header if nothing matches
            if any_visible:
                header.setStyleSheet(
                    "text-align: left; font-weight: bold; margin-top: 10px;"
                )
            else:
                header.setStyleSheet(
                    "text-align: left; font-weight: bold; margin-top: 10px; color: gray;"
                )

            # Auto-expand categories with matches
            if text:
                if any_visible:
                    header.setChecked(True)   # expand
                    frame.show()
                else:
                    header.setChecked(False)  # collapse
                    frame.hide()
            else:
                # Reset to default (all expanded)
                header.setChecked(True)
                frame.show()


    def get_selected_permissions(self):
        return [
            name for name, cb in self.checkboxes.items()
            if cb.isChecked()
        ]

    def expand_categories_with_selected(self):
        for category, perms in self.categories.items():
            # Check if any permission in this category is selected
            if any(p in self.selected for p in perms):
                header = self.category_headers[category]
                frame = self.category_frames[category]

                header.setChecked(True)
                frame.show()
