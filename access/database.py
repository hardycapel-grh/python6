from pymongo import MongoClient
from logger import logger

# Connect to MongoDB
client = MongoClient("mongodb://localhost:27017/")
db = client["test"]
users = db["users"]


# -----------------------------
#  USER CREATION
# -----------------------------
def create_user(username, hashed_pw, role, permissions, email):
    try:
        if users.find_one({"username": username}):
            logger.warning(f"Registration failed: username '{username}' already exists")
            return False

        users.insert_one({
            "username": username,
            "email": email,
            "password": hashed_pw,
            "role": role,
            "permissions": permissions
        })

        logger.info(f"User '{username}' created successfully")
        return True

    except Exception as e:
        logger.error(f"Database error during create_user for '{username}': {e}")
        return False



# -----------------------------
#  FETCH USER
# -----------------------------
def get_user(username):
    try:
        user = users.find_one({"username": username})
        if user:
            return user
        return None
    except Exception as e:
        logger.error(f"Database error during get_user('{username}'): {e}")
        return None


# -----------------------------
#  GET ALL USERS
# -----------------------------
def get_all_users():
    try:
        return list(users.find({}, {"_id": 0}))
    except Exception as e:
        logger.error(f"Failed to fetch all users: {e}")
        return []


# -----------------------------
#  UPDATE PERMISSIONS
# -----------------------------
def update_permissions(username, new_permissions):
    try:
        result = users.update_one(
            {"username": username},
            {"$set": {"permissions": new_permissions}}
        )

        if result.modified_count > 0:
            logger.info(f"Permissions updated for user '{username}'")
        else:
            logger.warning(f"No permission changes applied for '{username}'")

        return True

    except Exception as e:
        logger.error(f"Failed to update permissions for '{username}': {e}")
        return False


# -----------------------------
#  DELETE USER
# -----------------------------
def delete_user(username):
    try:
        result = users.delete_one({"username": username})

        if result.deleted_count > 0:
            logger.info(f"User '{username}' deleted successfully")
            return True
        else:
            logger.warning(f"Attempted to delete non-existent user '{username}'")
            return False

    except Exception as e:
        logger.error(f"Database error during delete_user('{username}'): {e}")
        return False


# -----------------------------
#  RESET PASSWORD
# -----------------------------
def update_password(username, new_hashed_pw):
    try:
        result = users.update_one(
            {"username": username},
            {"$set": {"password": new_hashed_pw}}
        )

        if result.modified_count > 0:
            logger.info(f"Password updated for user '{username}'")
        else:
            logger.warning(f"No password change applied for '{username}'")

        return True

    except Exception as e:
        logger.error(f"Failed to update password for '{username}': {e}")
        return False
    
def update_user_fields(username, fields):
    try:
        users.update_one(
            {"username": username},
            {"$set": fields}
        )
        return True
    except Exception as e:
        logger.error(f"Failed to update fields for '{username}': {e}")
        return False
