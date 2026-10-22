from PySide6.QtWidgets import QHBoxLayout, QListWidget, QTextBrowser, QWidget
import os

class HelpPage(QWidget):
    def __init__(self, mongo, user):
        super().__init__()

        layout = QHBoxLayout(self)
        self.setMinimumSize(900, 600)

        # Left list
        self.list = QListWidget()
        self.list.addItems([
            "Introduction",
            "My Profile",
            "Log Viewer",
            "Admin",
            "Admin: Users",
            "Admin: Roles",
            "Admin: Stores",
            "Admin: UOMs",
            "Admin: Store Locations",
            "Admin: Permissions",
            "Admin: Audit Log",
            "Admin: Suppliers",
            "Admin: BOM editor",
            "Labour Rates",
            "Inventory",
            "Sales Orders",
            "Work Orders",
            
        ])
        self.list.currentItemChanged.connect(self.load_topic)
        layout.addWidget(self.list, 1)

        # Markdown viewer
        self.browser = QTextBrowser()
        self.browser.setStyleSheet("""
            QTextBrowser {
                font-size: 14px;
                padding: 12px;
            }
            h1 { font-size: 22px; margin-top: 12px; }
            h2 { font-size: 18px; margin-top: 10px; }
            h3 { font-size: 16px; margin-top: 8px; }
            p  { margin: 6px 0; }
            li { margin: 4px 0; }
        """)
        layout.addWidget(self.browser, 3)

        # Load first item
        self.list.setCurrentRow(0)

    def load_topic(self, item):
        if not item:
            return

        # Convert "Admin: Users" → "admin_users.md"
        name = item.text().lower().replace(" ", "_").replace(":", "")

        filename = os.path.join("docs", f"{name}.md")

        if os.path.exists(filename):
            with open(filename, "r", encoding="utf-8") as f:
                self.browser.setMarkdown(f.read())
        else:
            self.browser.setText(f"Help file not found:\n{filename}")
        
