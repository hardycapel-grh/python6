import logging
import os

from PySide6.QtWidgets import QWidget

# Ensure logs directory exists
LOG_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "logs")
os.makedirs(LOG_DIR, exist_ok=True)

# Main application log
APP_LOG_PATH = os.path.join(LOG_DIR, "app.log")

# UI tree log (separate file)
UI_TREE_LOG_PATH = os.path.join(LOG_DIR, "ui_tree.log")

# Configure main logger
logger = logging.getLogger("app")
logger.setLevel(logging.DEBUG)

# File handler for main log
file_handler = logging.FileHandler(APP_LOG_PATH, encoding="utf-8")
file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(logging.Formatter(
    "%(asctime)s [%(levelname)s] %(message)s"
))

# Avoid duplicate handlers
if not logger.handlers:
    logger.addHandler(file_handler)

# UI tree logger (separate)
ui_tree_logger = logging.getLogger("ui_tree")
ui_tree_logger.setLevel(logging.DEBUG)

ui_tree_handler = logging.FileHandler(UI_TREE_LOG_PATH, encoding="utf-8")
ui_tree_handler.setLevel(logging.DEBUG)
ui_tree_handler.setFormatter(logging.Formatter("%(message)s"))

if not ui_tree_logger.handlers:
    ui_tree_logger.addHandler(ui_tree_handler)

def dump_widget_tree(widget: QWidget, indent: int = 0):
    """Recursively logs the widget tree to ui_tree.log."""
    ui_tree_logger.debug(" " * indent + f"{widget.__class__.__name__}")

    for child in widget.findChildren(QWidget, options=widget.FindDirectChildrenOnly):
        dump_widget_tree(child, indent + 2)