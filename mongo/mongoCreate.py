from pymongo import MongoClient

# Connect to MongoDB
client = MongoClient("mongodb://localhost:27017/")

# Select your database (replace 'test' if yours is different)
db = client["test"]

# Access the 'items' collection
items_collection = db["items"]

# Insert a new item
new_item = {"name": "Hammer", "category": "tools", "price": 9.99}
result = items_collection.insert_one(new_item)

print("Inserted item with _id:", result.inserted_id)

# Verify it was added
for item in items_collection.find():
    print(item)