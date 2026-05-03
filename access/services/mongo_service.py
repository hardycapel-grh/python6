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

            # Collections
            self.users = self.db["users"]
            self.roles = self.db["roles"]
            self.permissions = self.db["permissions"]
            self.logs = self.db["logs"]

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
        
    def update_user_permissions(self, user_id, permissions, performed_by):
        self.users.update_one(
            {"_id": ObjectId(user_id)},
            {"$set": {"permissions": permissions}}
        )
        logger.info(f"Updated permissions for user {user_id} by {performed_by}")



    

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

    def get_all_roles(self):
        return list(self.db["roles"].find({}, {"_id": 0}))

    def get_role(self, name):
        return self.db["roles"].find_one({"name": name})
        
    def create_role(self, name, permissions, description, performed_by):
        if self.get_role(name):
            raise RuntimeError("Role already exists.")

        role_doc = {
            "name": name,
            "permissions": permissions,
            "description": description
        }

        self.db["roles"].insert_one(role_doc)

        log_event(
            "info",
            "Role created",
            by=performed_by,
            target=name,
            permissions=",".join(permissions)
        )

    def update_role(self, name, permissions, description, performed_by):
        if not self.get_role(name):
            raise RuntimeError("Role does not exist.")

        self.db["roles"].update_one(
            {"name": name},
            {"$set": {
                "permissions": permissions,
                "description": description
            }}
        )

        log_event(
            "info",
            "Role updated",
            by=performed_by,
            target=name,
            permissions=",".join(permissions)
        )

    def count_users_with_role(self, name):
        return self.users.count_documents({"role": name})

    def delete_role(self, name, performed_by):
        count = self.count_users_with_role(name)
        if count > 0:
            raise RuntimeError(f"Cannot delete role '{name}' because {count} users have it.")

        self.db["roles"].delete_one({"name": name})

        log_event(
            "warn",
            "Role deleted",
            by=performed_by,
            target=name
        )
    
    # -----------------------------
    # PERMISSIONS COLLECTION
    # -----------------------------

    def get_all_permissions(self):
        return list(self.permissions.find({}, {"_id": 0, "name": 1, "category": 1, "description": 1}))



    def get_permission(self, name):
        return self.db["permissions"].find_one({"name": name})


    def create_permission(self, name, category, description, performed_by):
        if self.get_permission(name):
            raise RuntimeError(f"Permission '{name}' already exists.")

        doc = {
            "name": name,
            "category": category,
            "description": description
        }

        self.db["permissions"].insert_one(doc)

        log_event(
            "info",
            "Permission created",
            by=performed_by,
            target=name
        )


    def update_permission(self, name, category, description, performed_by):
        if not self.get_permission(name):
            raise RuntimeError(f"Permission '{name}' does not exist.")

        self.db["permissions"].update_one(
            {"name": name},
            {"$set": {
                "category": category,
                "description": description
            }}
        )

        log_event(
            "info",
            "Permission updated",
            by=performed_by,
            target=name
        )


    def delete_permission(self, name, performed_by):
        # Safety check: ensure no roles use this permission
        count = self.count_roles_using_permission(name)
        if count > 0:
            raise RuntimeError(f"Cannot delete permission '{name}' because {count} roles use it.")

        self.db["permissions"].delete_one({"name": name})

        log_event(
            "warn",
            "Permission deleted",
            by=performed_by,
            target=name
        )

    def count_users_using_permission(self, permission_name):
        return self.users.count_documents({"permissions": permission_name})

    def count_roles_using_permission(self, permission_name):
        return self.roles.count_documents({"permissions": permission_name})

    def count_total_usage_of_permission(self, permission_name):
        users = self.count_users_using_permission(permission_name)
        roles = self.count_roles_using_permission(permission_name)
        return users + roles





