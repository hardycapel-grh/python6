from pymongo import MongoClient

# Connect to MongoDB (default localhost:27017)
client = MongoClient("mongodb://localhost:27017/")

# Select your database (replace 'test' if yours is different)
db = client["test"]

# Access the 'items' collection
items_collection = db["items"]

# --- Search Examples ---

# 1. Find all documents
for item in items_collection.find():
    print(item)

# 2. Find with a filter (like WHERE in SQL)
for item in items_collection.find({"category": "tools"}):
    print(item)

# 3. Find one document
item = items_collection.find_one({"name": "Hammer"})
print(item)

# 4. Find with comparison operator
for item in items_collection.find({"price": {"$gt": 5}}):
    print(item)

# 5. Regex search (case-insensitive match)
for item in items_collection.find({"name": {"$regex": "ham", "$options": "i"}}):
    print(item)