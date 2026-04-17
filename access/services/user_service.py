import email

from pymongo import MongoClient
from bson import ObjectId
from services.mongo_service import MongoService
from ui.components.logger_utils import log_event
import bcrypt

class UserService:
    def __init__(self):
        self.mongo = MongoService()
        self.users = self.mongo.db.users
        self.client = MongoClient("mongodb://localhost:27017")
        self.db = self.client["test"]
        self.users = self.db["users"]
        self.roles = self.db["roles"]

    def hash_password(self, password):
        return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

    def create_user(self, username, password, role, status):
        # Check if user exists
        if self.get_user(username):
            raise ValueError("User already exists")

        # Hash password using bcrypt
        hashed_password = self.hash_password(password)

        # Load role permissions
        permissions = self.get_role_permissions(role)

        # Build user document
        # user_doc = {
        #     "username": username,
        #     "password_hash": hashed_password,   # <-- FIXED
        #     "role": role,
        #     "status": status,
        #     "permissions": permissions,
        #     "must_change_password": False       # <-- NEW FIELD
        # }

        user_doc = self.mongo.build_user_document(
            username,
            email,
            password,
            role,
            status
        )


        # Insert into DB
        self.add_user(user_doc)


    def get_user_by_username(self, username):
        return self.users.find_one({"username": username})

    def get_role_permissions(self, role_name):
        role = self.roles.find_one({"role": role_name})
        return role["permissions"] if role else {}

    def get_all_users(self):
        return list(self.users.find({}, {"_id": 0}))

    def get_user(self, username):
        return self.users.find_one({"username": username}, {"_id": 0})

    def add_user(self, data):
        self.users.insert_one(data)

    def delete_user(self, username):
        self.users.delete_one({"username": username})

    def update_user(self, username, updates):
        self.users.update_one({"username": username}, {"$set": updates})

    def has_permission(self, perm: str) -> bool:
        user = self.current_user
        if not user:
            return False

        # Admin wildcard
        if "*" in user.get("permissions", []):
            return True

        return perm in user.get("permissions", [])
    
    def update_profile(self, user_id, fields, performed_by):
        try:
            # Email validation
            if "email" in fields:
                if not self.validate_email_format(fields["email"]):
                    raise RuntimeError("Invalid email format.")

                if self.email_exists(fields["email"], exclude_user_id=user_id):
                    raise RuntimeError("Email already in use.")

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


