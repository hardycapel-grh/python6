from services.mongo_service import MongoService

mongo = MongoService()

initial_roles = [
    {"name": "viewer", "permissions": ["basic.view"], "description": "Read-only access"},
    {"name": "user", "permissions": ["basic.view", "basic.edit"], "description": "Standard user"},
    {"name": "manager", "permissions": [], "description": "Manager role"},
    {"name": "admin", "permissions": ["*"], "description": "Full access"}
]

for r in initial_roles:
    if not mongo.get_role(r["name"]):
        mongo.create_role(
            r["name"],
            r["permissions"],
            r["description"],
            performed_by="system"
        )

print("Roles migrated successfully.")
