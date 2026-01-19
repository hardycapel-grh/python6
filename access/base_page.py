# base_page.py
from PySide6.QtWidgets import (
    QWidget, QLineEdit, QTextEdit, QPlainTextEdit,
    QComboBox, QPushButton
)
from logger import logger


class BasePage(QWidget):
    title = "Untitled Page"

    def set_read_only(self, ro: bool):
        """Enable or disable editing for all widgets on the page."""

        logger.info(f"[BasePage] Applying read_only={ro} on page '{self.title}'")

        line_edits = self.findChildren(QLineEdit)
        text_edits = self.findChildren(QTextEdit)
        plain_edits = self.findChildren(QPlainTextEdit)
        combos = self.findChildren(QComboBox)
        buttons = self.findChildren(QPushButton)

        logger.info(
            f"[BasePage] Found widgets on '{self.title}': "
            f"{len(line_edits)} QLineEdit, "
            f"{len(text_edits)} QTextEdit, "
            f"{len(plain_edits)} QPlainTextEdit, "
            f"{len(combos)} QComboBox, "
            f"{len(buttons)} QPushButton"
        )

        # Text inputs
        for widget in line_edits:
            widget.setReadOnly(ro)

        for widget in text_edits:
            widget.setReadOnly(ro)

        for widget in plain_edits:
            widget.setReadOnly(ro)

        # Combo boxes
        for widget in combos:
            widget.setEnabled(not ro)

        # Buttons (disable all except navigation/safe ones)
        disabled_buttons = []
        for btn in buttons:
            if btn.objectName() not in ("nav", "safe", "back"):
                btn.setEnabled(not ro)
                disabled_buttons.append(btn.text())

        logger.info(
            f"[BasePage] Disabled buttons on '{self.title}': {disabled_buttons}"
        )