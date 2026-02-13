from pymongo import MongoClient

class UserService:
    def __init__(self):
        self.client = MongoClient("mongodb://localhost:27017")
        self.db = self.client["test"]
        self.users = self.db["users"]
        self.roles = self.db["roles"]

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