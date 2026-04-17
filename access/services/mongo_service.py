from pymongo import MongoClient
from bson.objectid import ObjectId
from ui.components.logger import logger
from ui.components.logger_utils import log_event
from datetime import datetime
import bcrypt
import re


class MongoService:

    EMAIL_REGEX = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")

    DEFAULT_ROLE_PERMISSIONS = {
        "viewer": ["basic.view"],
        "user": ["basic.view", "basic.edit"],
        "manager": ["basic.view", "basic.edit", "users.read", "users.write"],
        "admin": ["*"]
    }

    def __init__(self, uri="mongodb://localhost:27017", db_name="test"):
        try:
            self.client = MongoClient(uri)
            self.db = self.client[db_name]
            self.users = self.db["users"]
            logger.info("Connected to MongoDB")
        except Exception as e:
            logger.error(f"MongoDB connection failed: {e}")
            raise

    # -------------------------------------------------
    # Helpers
    # -------------------------------------------------
    def validate_email_format(self, email: str) -> bool:
        return bool(self.EMAIL_REGEX.match(email))

    def email_exists(self, email: str, exclude_user_id=None) -> bool:
        query = {"email": email}
        if exclude_user_id:
            query["_id"] = {"$ne": ObjectId(exclude_user_id)}
        return self.users.find_one(query) is not None

    def username_exists(self, username: str, exclude_user_id=None) -> bool:
        query = {"username": username}
        if exclude_user_id:
            query["_id"] = {"$ne": ObjectId(exclude_user_id)}
        return self.users.find_one(query) is not None

    def hash_password(self, password: str) -> str:
        return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
    
    def build_user_document(self, username, email, password, role="viewer", status="Active"):
        return {
            "username": username,
            "email": email,
            "password_hash": self.hash_password(password),
            "role": role,
            "permissions": self.DEFAULT_ROLE_PERMISSIONS.get(role, []),
            "status": status,
            "created_at": datetime.utcnow(),
            "last_login": None,
            "theme": "light"
        }


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

            if bcrypt.checkpw(password.encode(), stored_hash.encode()):
                logger.info(f"User '{username}' authenticated successfully")
                return user

            logger.info(f"Login failed: incorrect password for '{username}'")
            return None

        except Exception as e:
            logger.error(f"Authentication error: {e}")
            return None

    # -------------------------------------------------
    # Create user
    # -------------------------------------------------
    def create_user(self, user_doc, performed_by):
        # Email validation
        if not self.validate_email_format(user_doc["email"]):
            raise RuntimeError("Invalid email format.")

        if self.email_exists(user_doc["email"]):
            raise RuntimeError("Email already in use.")

        # Ensure role exists
        role = user_doc.setdefault("role", "viewer")

        # Assign default permissions
        default_perms = self.DEFAULT_ROLE_PERMISSIONS.get(role, [])
        user_doc.setdefault("permissions", default_perms.copy())

        try:
            self.users.insert_one(user_doc)

            log_event(
                "info",
                "User created",
                by=performed_by,
                target=user_doc.get("username"),
                role=role,
                permissions=",".join(user_doc.get("permissions", []))
            )

        except Exception as e:
            log_event(
                "error",
                "User creation failed",
                by=performed_by,
                target=user_doc.get("username"),
                error=str(e)
            )
            raise RuntimeError(f"Failed to create user: {e}")

    # -------------------------------------------------
    # Update user (admin)
    # -------------------------------------------------
    def update_user(self, user_id, update_doc, performed_by):

        # Email validation
        if "email" in update_doc:
            if not self.validate_email_format(update_doc["email"]):
                raise RuntimeError("Invalid email format.")

            if self.email_exists(update_doc["email"], exclude_user_id=user_id):
                raise RuntimeError("Email already in use.")

        try:
            self.users.update_one(
                {"_id": ObjectId(user_id)},
                {"$set": update_doc}
            )

            changed_fields = ", ".join(update_doc.keys())

            user = self.users.find_one({"_id": ObjectId(user_id)})
            username = user.get("username") if user else user_id

            log_event(
                "info",
                "User updated",
                by=performed_by,
                target=username,
                fields=changed_fields
            )

        except Exception as e:
            log_event(
                "error",
                "User update failed",
                by=performed_by,
                target=user_id,
                error=str(e)
            )
            raise RuntimeError(f"Failed to update user: {e}")

    # -------------------------------------------------
    # Delete user (admin)
    # -------------------------------------------------
    def delete_user(self, user_id, performed_by):
        try:
            user = self.users.find_one({"_id": ObjectId(user_id)})
            username = user.get("username") if user else user_id

            self.users.delete_one({"_id": ObjectId(user_id)})

            log_event(
                "warn",
                "User deleted",
                by=performed_by,
                target=username
            )

        except Exception as e:
            log_event(
                "error",
                "User deletion failed",
                by=performed_by,
                target=user_id,
                error=str(e)
            )
            raise RuntimeError(f"Failed to delete user: {e}")

    # -------------------------------------------------
    # Update permissions (admin)
    # -------------------------------------------------
    def update_permissions(self, user_id, new_permissions, performed_by):
        try:
            user = self.users.find_one({"_id": ObjectId(user_id)})
            username = user.get("username") if user else user_id

            old = set(user.get("permissions", []))
            new = set(new_permissions)

            added = new - old
            removed = old - new

            self.users.update_one(
                {"_id": ObjectId(user_id)},
                {"$set": {"permissions": list(new)}}
            )

            log_event(
                "info",
                "Permissions updated",
                by=performed_by,
                target=username,
                added=",".join(added),
                removed=",".join(removed)
            )

        except Exception as e:
            log_event(
                "error",
                "Permission update failed",
                by=performed_by,
                target=user_id,
                error=str(e)
            )
            raise RuntimeError(f"Failed to update permissions: {e}")

    # -------------------------------------------------
    # Update role (admin)
    # -------------------------------------------------
    def update_role(self, user_id, new_role, performed_by):
        try:
            user = self.users.find_one({"_id": ObjectId(user_id)})
            username = user.get("username") if user else user_id

            new_permissions = self.DEFAULT_ROLE_PERMISSIONS.get(new_role, [])

            self.users.update_one(
                {"_id": ObjectId(user_id)},
                {"$set": {
                    "role": new_role,
                    "permissions": new_permissions
                }}
            )

            log_event(
                "info",
                "Role updated",
                by=performed_by,
                target=username,
                role=new_role,
                permissions=",".join(new_permissions)
            )

        except Exception as e:
            log_event(
                "error",
                "Role update failed",
                by=performed_by,
                target=user_id,
                error=str(e)
            )
            raise RuntimeError(f"Failed to update role: {e}")

    # -------------------------------------------------
    # Admin password reset
    # -------------------------------------------------
    def reset_password(self, user_id, new_password, performed_by):
        try:
            user = self.users.find_one({"_id": ObjectId(user_id)})
            username = user.get("username") if user else user_id

            new_hash = self.hash_password(new_password)

            self.users.update_one(
                {"_id": ObjectId(user_id)},
                {"$set": {"password_hash": new_hash}}
            )

            log_event(
                "warn",
                "Password reset",
                by=performed_by,
                target=username
            )

        except Exception as e:
            log_event(
                "error",
                "Password reset failed",
                by=performed_by,
                target=user_id,
                error=str(e)
            )
            raise RuntimeError(f"Failed to reset password: {e}")

    # -------------------------------------------------
    # User self-service: update profile
    # -------------------------------------------------
    def update_profile(self, user_id, fields, performed_by):

        if "email" in fields:
            if not self.validate_email_format(fields["email"]):
                raise RuntimeError("Invalid email format.")

            if self.email_exists(fields["email"], exclude_user_id=user_id):
                raise RuntimeError("Email already in use.")

        try:
            self.users.update_one(
                {"_id": ObjectId(user_id)},
                {"$set": fields}
            )

            changed = ", ".join(fields.keys())

            log_event(
                "info",
                "Profile updated",
                by=performed_by,
                target=performed_by,
                fields=changed
            )

        except Exception as e:
            log_event(
                "error",
                "Profile update failed",
                by=performed_by,
                target=performed_by,
                error=str(e)
            )
            raise

    # -------------------------------------------------
    # User self-service: change password
    # -------------------------------------------------
    def change_password(self, user_id, old_pw, new_pw, performed_by):
        try:
            user = self.users.find_one({"_id": ObjectId(user_id)})
            if not user:
                raise RuntimeError("User not found.")

            stored_hash = user.get("password_hash")
            if not bcrypt.checkpw(old_pw.encode(), stored_hash.encode()):
                raise RuntimeError("Current password is incorrect.")

            new_hash = self.hash_password(new_pw)

            self.users.update_one(
                {"_id": ObjectId(user_id)},
                {"$set": {"password_hash": new_hash}}
            )

            log_event(
                "info",
                "Password changed",
                by=performed_by,
                target=performed_by
            )

        except Exception as e:
            log_event(
                "error",
                "Password change failed",
                by=performed_by,
                target=performed_by,
                error=str(e)
            )
            raise
