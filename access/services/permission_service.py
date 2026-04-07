from functools import wraps
from PySide6.QtWidgets import QMessageBox

def requires_permission(permission):
    def decorator(func):
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            user = getattr(self, "current_user", None)
            if not user or permission not in user.permissions:
                QMessageBox.warning(self, "Access Denied",
                                    "You do not have permission to access this feature.")
                return
            return func(self, *args, **kwargs)
        return wrapper
    return decorator

def has_permission(user, permission: str) -> bool:
    if not user:
        return False
    return permission in user.permissions
