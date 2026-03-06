from pymongo import MongoClient
from ui.components.logger import logger
import bcrypt


class MongoService:
    def __init__(self, uri="mongodb://localhost:27017", db_name="test"):
        try:
            self.client = MongoClient(uri)
            self.db = self.client[db_name]
            logger.info("Connected to MongoDB")
        except Exception as e:
            logger.error(f"MongoDB connection failed: {e}")
            raise

    # -------------------------------------------------
    # Authentication (login)
    # -------------------------------------------------
    def authenticate(self, username, password):
        try:
            user = self.db.users.find_one({"username": username})
            if not user:
                logger.info(f"Login failed: user '{username}' not found")
                return None

            stored_hash = user.get("password_hash")
            if not stored_hash:
                logger.error(f"User '{username}' has no password_hash field")
                return None

            if bcrypt.checkpw(password.encode("utf-8"), stored_hash.encode("utf-8")):
                logger.info(f"User '{username}' authenticated successfully")
                return user

            logger.info(f"Login failed: incorrect password for '{username}'")
            return None

        except Exception as e:
            logger.error(f"Authentication error: {e}")
            return None

    # -------------------------------------------------
    # User creation (registration + admin add user)
    # -------------------------------------------------
    def create_user(self, username, password, permissions=None, email="", must_change_password=False):
        try:
            if self.db.users.find_one({"username": username}):
                logger.warning(f"User '{username}' already exists")
                return False, "User already exists"

            hashed = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

            user_doc = {
                "username": username,
                "password_hash": hashed,
                "permissions": permissions or {},
                "email": email,
                "must_change_password": must_change_password,
                "theme": "light",
                "last_login": None
            }

            self.db.users.insert_one(user_doc)
            logger.info(f"User '{username}' created")
            return True, None

        except Exception as e:
            logger.error(f"Failed to create user '{username}': {e}")
            return False, str(e)

    # -------------------------------------------------
    # Password reset (admin)
    # -------------------------------------------------
    def reset_password(self, username, new_password, force_change=True):
        try:
            hashed = bcrypt.hashpw(new_password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

            self.db.users.update_one(
                {"username": username},
                {"$set": {
                    "password_hash": hashed,
                    "must_change_password": force_change
                }}
            )
            logger.info(f"Password reset for '{username}'")
            return True

        except Exception as e:
            logger.error(f"Failed to reset password for '{username}': {e}")
            return False

    # -------------------------------------------------
    # Clear force-password-change flag
    # -------------------------------------------------
    def clear_force_password_change(self, username):
        try:
            self.db.users.update_one(
                {"username": username},
                {"$set": {"must_change_password": False}}
            )
            logger.info(f"Force-password-change cleared for '{username}'")
            return True

        except Exception as e:
            logger.error(f"Failed to clear force-password-change for '{username}': {e}")
            return False

    # -------------------------------------------------
    # Update permissions
    # -------------------------------------------------
    def update_permissions(self, username, permissions):
        try:
            self.db.users.update_one(
                {"username": username},
                {"$set": {"permissions": permissions}}
            )
            logger.info(f"Permissions updated for '{username}'")
            return True

        except Exception as e:
            logger.error(f"Failed to update permissions for '{username}': {e}")
            return False

    # -------------------------------------------------
    # Update arbitrary user fields
    # -------------------------------------------------
    def update_user_fields(self, username, fields):
        try:
            self.db.users.update_one(
                {"username": username},
                {"$set": fields}
            )
            logger.info(f"Updated fields for '{username}': {list(fields.keys())}")
            return True

        except Exception as e:
            logger.error(f"Failed to update fields for '{username}': {e}")
            return False

    # -------------------------------------------------
    # Retrieve all users (Admin Users page)
    # -------------------------------------------------
    def get_users(self):
        try:
            users = list(self.db.users.find({}, {"_id": 0}))
            logger.info(f"Loaded {len(users)} users from MongoDB")
            return users
        except Exception as e:
            logger.error(f"Failed to load users: {e}")
            return []