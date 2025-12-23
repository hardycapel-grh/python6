from pymongo import MongoClient, errors

# Try connecting to MongoDB
try:
    client = MongoClient("mongodb://localhost:27017/", serverSelectionTimeoutMS=2000)
    client.server_info()  # Force connection test
    print("[DEBUG] Connected to MongoDB")
except errors.ServerSelectionTimeoutError as e:
    print("[ERROR] Could not connect to MongoDB:", e)
    client = None

# Only assign db if client exists
db = client["test"] if client is not None else None

# Only assign users collection if db exists
users = db["users"] if db is not None else None


def create_user(username, password, role):
    if users is None:
        print("[ERROR] Cannot create user — database not available")
        return False

    try:
        print(f"[DEBUG] Creating user: {username}, role: {role}")
        users.insert_one({
            "username": username,
            "password": password,
            "role": role
        })
        print("[DEBUG] User successfully inserted")
        return True
    except Exception as e:
        print("[ERROR] Failed to insert user:", e)
        return False


def get_user(username):
    if users is None:
        print("[ERROR] Cannot fetch user — database not available")
        return None

    try:
        print(f"[DEBUG] Fetching user: {username}")
        user = users.find_one({"username": username})
        print(f"[DEBUG] User found: {user is not None}")
        return user
    except Exception as e:
        print("[ERROR] Failed to fetch user:", e)
        return None

def get_all_users():
    if users is None:
        print("[ERROR] Cannot fetch users — database not available")
        return []

    try:
        print("[DEBUG] Fetching all users")
        return list(users.find({}, {"_id": 0}))  # hide MongoDB _id
    except Exception as e:
        print("[ERROR] Failed to fetch all users:", e)
        return []


def update_user_role(username, new_role):
    if users is None:
        print("[ERROR] Cannot update user — database not available")
        return False

    try:
        print(f"[DEBUG] Updating role for {username} → {new_role}")
        result = users.update_one(
            {"username": username},
            {"$set": {"role": new_role}}
        )
        return result.modified_count > 0
    except Exception as e:
        print("[ERROR] Failed to update user role:", e)
        return False