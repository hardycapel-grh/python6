from pymongo import MongoClient

# Connect to the running mongod server
client = MongoClient("mongodb://localhost:27017/")

# Select the database
db = client["test"]

# Explicitly create a new collection
db.create_collection("pythonCollection")

# Verify by listing collections
print(db.list_collection_names())