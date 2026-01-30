import logging
import os

# Determine the folder this file lives in
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Build the correct log path
log_path = os.path.abspath(os.path.join(BASE_DIR,"..", "logs", "app.log"))

# Ensure the logs folder exists
os.makedirs(os.path.dirname(log_path), exist_ok=True)

logging.basicConfig(
    filename=log_path,
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

logger = logging.getLogger("app")