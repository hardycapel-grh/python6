from pymongo import MongoClient

# Connect to MongoDB (default localhost:27017)
client = MongoClient("mongodb://localhost:27017/")

# Select your database (replace 'test' with yours if different)
db = client["test"]

# Access the 'items' collection
items_collection = db["items"]

# Show all documents
for item in items_collection.find():
    print(item)