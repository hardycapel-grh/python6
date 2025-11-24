from pymongo import MongoClient

client = MongoClient("mongodb://localhost:27017/")
db = client["test"]
items_collection = db["items"]

# Update one document
result = items_collection.update_one(
    {"name": "Hammer"},              # filter
    {"$set": {"price": 12.99}}       # update
)
print("Matched:", result.matched_count, "Modified:", result.modified_count)

# Update many documents
result = items_collection.update_many(
    {"category": "tools"},           # filter
    {"$set": {"inStock": True}}      # update
)
print("Matched:", result.matched_count, "Modified:", result.modified_count)