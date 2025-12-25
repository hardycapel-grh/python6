from pymongo import MongoClient
from logger import logger



# Connect to MongoDB
client = MongoClient("mongodb://localhost:27017/")
db = client["test"]
users = db["users"]


def create_user(username, hashed_pw, role, permissions):
    """Insert a new user into MongoDB."""
    try:
        # Check if username already exists
        if users.find_one({"username": username}):
            logger.warning(f"Registration failed: username '{username}' already exists")

            
            return False

        user_doc = {
            "username": username,
            "password": hashed_pw,
            "role": role,
            "permissions": permissions
        }

        users.insert_one(user_doc)
        logger.info(f"User '{username}' created successfully")
        return True

    except Exception as e:
        logger.error(f"Database error during create_user: {e}")

        return False


def get_user(username):
    """Retrieve a user document from MongoDB."""
    try:
        user = users.find_one({"username": username})
        
        return user
    except Exception as e:
        
        return None