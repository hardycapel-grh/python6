from ui.windows.window_with_sidebar import WindowWithSidebar
from ui.pages.admin.users_page import UsersPage
from ui.pages.admin.roles_page import RolesPage
from ui.pages.admin.permissions_page import PermissionsPage
from ui.pages.admin.audit_log_page import AuditLogPage
from ui.components.logger_utils import log_event


class AdminControlWindow(WindowWithSidebar):
    def __init__(self, user, mongo, parent=None):

        # Assign attributes BEFORE WindowWithSidebar runs _setup_pages()
        self.user = user
        self.mongo = mongo
        self.app = parent

        # Now call base constructor
        super().__init__("Admin Control Panel", parent)

    def has_permission(self, perm_name: str) -> bool:
        return self.app.has_permission(perm_name)


    
    def _setup_pages(self):
        log_event("debug", "AdminControlWindow: setting up pages",
                  user=self.user.username)

        self.add_page("Users",
                      lambda: UsersPage(self.user, self.mongo, parent=self),
                      required_permission="users.read")

        self.add_page("Roles", 
                      lambda: RolesPage(self.mongo, parent=self))

        self.add_page("Permissions", 
                      lambda: PermissionsPage(self.mongo, parent=self))
        self.add_page("Audit Log",
                      AuditLogPage,
                      required_permission="logs.read")
