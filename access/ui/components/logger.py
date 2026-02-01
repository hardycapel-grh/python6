import logging
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Go up TWO levels now that logger.py is in ui/components
log_path = os.path.abspath(os.path.join(BASE_DIR, "..", "..", "logs", "app.log"))

os.makedirs(os.path.dirname(log_path), exist_ok=True)

file_handler = logging.FileHandler(log_path)
file_handler.setLevel(logging.INFO)
file_handler.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(message)s"))

logger = logging.getLogger("app")
logger.setLevel(logging.INFO)

if not logger.handlers:
    logger.addHandler(file_handler)

logger.info(f"Logger initialised. Writing to: {file_handler.baseFilename}")