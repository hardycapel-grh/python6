# ui/windows/admin_control_window.py

from ui.windows.window_with_sidebar import WindowWithSidebar
from ui.pages.admin.users_page import UsersPage
from ui.pages.admin.roles_page import RolesPage
from ui.pages.admin.permissions_page import PermissionsPage
from ui.pages.admin.audit_log_page import AuditLogPage


class AdminControlWindow(WindowWithSidebar):
    REQUIRED_PERMISSION = "admin.access"

    def __init__(self, user):
        self.user = user
        super().__init__("Admin Control Panel")

    def _setup_pages(self):
        # Only UsersPage needs the user
        self.add_page("Users", lambda: UsersPage(self.user))

        # These pages do NOT take a user argument
        self.add_page("Roles", RolesPage)
        self.add_page("Permissions", PermissionsPage)
        self.add_page("Audit Log", AuditLogPage)
