from pymongo import MongoClient

client = MongoClient("mongodb://localhost:27017/")
db = client["test"]
items_collection = db["items"]

# Delete one document
result = items_collection.delete_one({"name": "Hammer"})
print("Deleted count:", result.deleted_count)

# Delete many documents
# result = items_collection.delete_many({"category": "tools"})
# print("Deleted count:", result.deleted_count)

# Delete all documents
# result = items_collection.delete_many({})
# print("Deleted count:", result.deleted_count)