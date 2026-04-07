from pymongo import MongoClient
from bson.objectid import ObjectId
from ui.components.logger import logger
import bcrypt
from datetime import datetime


class MongoService:

    DEFAULT_ROLE_PERMISSIONS = {
        "viewer": [
            "basic.view"
        ],

        "user": [
            "basic.view",
            "basic.edit"
        ],

        "admin": [
            "*"   # full access
        ]
    }


    def __init__(self, uri="mongodb://localhost:27017", db_name="test"):
        try:
            self.client = MongoClient(uri)
            self.db = self.client[db_name]

            # FIX: define users collection
            self.users = self.db["users"]

            logger.info("Connected to MongoDB")
        except Exception as e:
            logger.error(f"MongoDB connection failed: {e}")
            raise

    # -------------------------------------------------
    # Authentication
    # -------------------------------------------------
    def authenticate(self, username, password):
        try:
            user = self.users.find_one({"username": username})
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
    # Create user (Add User dialog)
    # -------------------------------------------------
        
    def create_user(self, user_doc):
        # Ensure a role exists
        role = user_doc.setdefault("role", "viewer")

        # Assign default permissions from the central template
        default_perms = self.DEFAULT_ROLE_PERMISSIONS.get(role, [])
        user_doc.setdefault("permissions", default_perms.copy())

        try:
            self.users.insert_one(user_doc)
            logger.info(f"User '{user_doc['username']}' created")
        except Exception as e:
            raise RuntimeError(f"Failed to create user: {e}")




    # -------------------------------------------------
    # Update user (Edit User dialog)
    # -------------------------------------------------
    def update_user(self, user_id, update_doc):
        try:
            self.users.update_one(
                {"_id": ObjectId(user_id)},
                {"$set": update_doc}
            )
            logger.info(f"User '{user_id}' updated")
        except Exception as e:
            raise RuntimeError(f"Failed to update user: {e}")

    # -------------------------------------------------
    # Get user by ID
    # -------------------------------------------------
    def get_user_by_id(self, user_id):
        try:
            return self.users.find_one({"_id": ObjectId(user_id)})
        except Exception as e:
            raise RuntimeError(f"Failed to fetch user: {e}")

    # -------------------------------------------------
    # Get all users (Users page)
    # -------------------------------------------------
    def get_all_users(self):
        try:
            users = list(self.users.find({}, {
                "_id": 1,
                "username": 1,
                "email": 1,
                "role": 1,
                "status": 1,
                "permissions": 1,
                "created_at": 1,
                "last_login": 1
            }))

            # Convert ObjectId to string for UI
            for u in users:
                u["_id"] = str(u["_id"])

            return users

        except Exception as e:
            raise RuntimeError(f"Failed to fetch users: {e}")

    def delete_user(self, user_id):
        try:
            self.users.delete_one({"_id": ObjectId(user_id)})
        except Exception as e:
            raise RuntimeError(f"Failed to delete user: {e}")
        
    def build_user_document(self, username, email, password, role="viewer", status="Active"):
        return {
            "username": username,
            "email": email,
            "password_hash": self.hash_password(password),
            "role": role,
            "permissions": [],  # assigned later in create_user()
            "status": status,
            "created_at": datetime.utcnow().isoformat(),
            "last_login": None,
            "theme": "light"
        }


    def hash_password(self, password: str) -> str:
        return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

    def email_exists(self, email: str) -> bool:
        return self.users.find_one({"email": email}) is not None

    def username_exists(self, username: str) -> bool:
        return self.users.find_one({"username": username}) is not None
