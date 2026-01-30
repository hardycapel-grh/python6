from pymongo import MongoClient
from ui.logger import logger

# -----------------------------------
#  CONNECT TO MONGODB
# -----------------------------------
client = MongoClient("mongodb://localhost:27017/")
db = client["test"]
users = db["users"]


# -----------------------------------
#  USER CREATION
# -----------------------------------
def create_user(username, hashed_pw, role, permissions, email):
    """
    Create a new user with hashed password and default fields.
    """
    try:
        if users.find_one({"username": username}):
            logger.warning(f"Registration failed: username '{username}' already exists")
            return False

        user_doc = {
            "username": username,
            "email": email,
            "password": hashed_pw,      # raw bytes → MongoDB Binary (correct)
            "role": role,
            "permissions": permissions,
            "phone": "",
            "theme": ""
        }

        users.insert_one(user_doc)
        logger.info(f"User '{username}' created successfully")
        return True

    except Exception as e:
        logger.error(f"Database error during create_user('{username}'): {e}")
        return False


# -----------------------------------
#  FETCH USER
# -----------------------------------
def get_user(username):
    """
    Return full MongoDB user document or None.
    """
    try:
        return users.find_one({"username": username})
    except Exception as e:
        logger.error(f"Database error during get_user('{username}'): {e}")
        return None


# -----------------------------------
#  GET ALL USERS
# -----------------------------------
def get_all_users():
    """
    Return all users except _id.
    """
    try:
        return list(users.find({}, {"_id": 0}))
    except Exception as e:
        logger.error(f"Failed to fetch all users: {e}")
        return []


# -----------------------------------
#  UPDATE PERMISSIONS
# -----------------------------------
def update_permissions(username, new_permissions):
    """
    Update a user's permissions dictionary.
    """
    try:
        result = users.update_one(
            {"username": username},
            {"$set": {"permissions": new_permissions}}
        )

        if result.matched_count == 0:
            logger.error(f"update_permissions: No user found with username '{username}'")
            return False

        if result.modified_count == 0:
            logger.warning(f"update_permissions: No changes applied for '{username}'")
            return False

        logger.info(f"Permissions updated for user '{username}'")
        return True

    except Exception as e:
        logger.error(f"Failed to update permissions for '{username}': {e}")
        return False


# -----------------------------------
#  DELETE USER
# -----------------------------------
def delete_user(username):
    """
    Delete a user by username.
    """
    try:
        result = users.delete_one({"username": username})

        if result.deleted_count == 0:
            logger.warning(f"Attempted to delete non-existent user '{username}'")
            return False

        logger.info(f"User '{username}' deleted successfully")
        return True

    except Exception as e:
        logger.error(f"Database error during delete_user('{username}'): {e}")
        return False


# -----------------------------------
#  UPDATE PASSWORD
# -----------------------------------
def update_password(username, new_hashed_pw):
    """
    Update a user's password. Returns True only if the update succeeded.
    """
    try:
        result = users.update_one(
            {"username": username},
            {"$set": {"password": new_hashed_pw}}
        )

        if result.matched_count == 0:
            logger.error(f"update_password: No user found with username '{username}'")
            return False

        if result.modified_count == 0:
            logger.warning(f"update_password: Password for '{username}' was not modified")
            return False

        logger.info(f"Password updated for user '{username}'")
        return True

    except Exception as e:
        logger.error(f"Failed to update password for '{username}': {e}")
        return False


# -----------------------------------
#  UPDATE GENERIC USER FIELDS
# -----------------------------------
def update_user_fields(username, fields):
    """
    Update any set of fields on a user document.
    """
    try:
        result = users.update_one(
            {"username": username},
            {"$set": fields}
        )

        if result.matched_count == 0:
            logger.error(f"update_user_fields: No user found with username '{username}'")
            return False

        logger.info(f"Fields updated for user '{username}'")
        return True

    except Exception as e:
        logger.error(f"Failed to update fields for '{username}': {e}")
        return False