from pymongo import MongoClient

client = MongoClient("mongodb://localhost:27017")
db = client["test"]

items = db.inventory

count = 0
for item in items.find():
    if "uom" not in item or not item["uom"]:
        items.update_one(
            {"_id": item["_id"]},
            {"$set": {"uom": "EA"}}
        )
        count += 1

print(f"Updated {count} items with default UOM 'EA'")
