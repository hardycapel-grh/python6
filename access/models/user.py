class User:
    def __init__(self, username, role, permissions):
        self.username = username
        self.role = role
        self.permissions = permissions or []

    def has_permission(self, permission: str) -> bool:
        return permission in self.permissions