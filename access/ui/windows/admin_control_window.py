from ui.windows.window_with_sidebar import WindowWithSidebar
from ui.pages.admin.users_page import UsersPage
from ui.pages.admin.roles_page import RolesPage
from ui.pages.admin.permissions_page import PermissionsPage
from ui.pages.admin.audit_log_page import AuditLogPage
from ui.components.logger_utils import log_event


class AdminControlWindow(WindowWithSidebar):
    def __init__(self, user):
        self.user = user
        self.current_user = user  # required by WindowWithSidebar

        log_event("info", "AdminControlWindow opened",
                  user=self.user.username)

        super().__init__("Admin Control Panel")

    def _setup_pages(self):
        log_event("debug", "AdminControlWindow: setting up pages",
                  user=self.user.username)

        self.add_page("Users",
                      lambda: UsersPage(self.user),
                      required_permission="users.read")

        self.add_page("Roles",
                      RolesPage,
                      required_permission="permissions.read")

        self.add_page("Permissions",
                      PermissionsPage,
                      required_permission="permissions.write")

        self.add_page("Audit Log",
                      AuditLogPage,
                      required_permission="logs.read")
