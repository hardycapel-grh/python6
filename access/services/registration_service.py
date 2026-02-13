import re
import bcrypt
from datetime import datetime
from ui.components.logger import logger
from services.user_service import UserService


class RegistrationService:
    def __init__(self):
        self.user_service = UserService()

    # -------------------------
    # VALIDATION
    # -------------------------
    def validate(self, username, email, password, confirm_password):
        if not username or not email or not password or not confirm_password:
            return False, "All fields are required."

        if password != confirm_password:
            return False, "Passwords do not match."

        # Password strength rules
        if len(password) < 8:
            return False, "Password must be at least 8 characters."

        if not re.search(r"[A-Z]", password):
            return False, "Password must contain an uppercase letter."

        if not re.search(r"[a-z]", password):
            return False, "Password must contain a lowercase letter."

        if not re.search(r"[0-9]", password):
            return False, "Password must contain a number."

        if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
            return False, "Password must contain a symbol."

        # Email format
        if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            return False, "Invalid email format."

        # Duplicate username
        if self.user_service.get_user_by_username(username):
            logger.warning(f"Registration failed: duplicate username '{username}'")
            return False, "Username already exists."

        return True, None

    # -------------------------
    # REGISTRATION
    # -------------------------
    def register_user(self, username, email, password):
        # Hash password
        password_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

        # Load default permissions for role "User"
        permissions = self.user_service.get_role_permissions("User")

        user_doc = {
            "username": username,
            "email": email,
            "password_hash": password_hash,
            "role": "User",
            "permissions": permissions,
            "status": "Active",
            "created_at": datetime.utcnow().isoformat()
        }

        self.user_service.users.insert_one(user_doc)
        logger.info(f"User '{username}' registered successfully")

        return True