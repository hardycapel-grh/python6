from PySide6.QtCore import Qt
from ui.windows.window_with_sidebar import WindowWithSidebar
from ui.pages.admin.users_page import UsersPage
from ui.pages.admin.roles_page import RolesPage
from ui.pages.admin.permissions_page import PermissionsPage
from ui.pages.admin.uom_management_page import UomManagementPage
from ui.pages.admin.audit_log_page import AuditLogPage
from ui.pages.admin.supplier_management_page import SupplierManagementPage
from ui.pages.stores.stores_list_page import StoresListPage
from ui.components.logger_utils import log_event

class AdminControlWindow(WindowWithSidebar):
    def __init__(self, user, mongo, parent=None):

        super().__init__("Admin Control Panel", parent)
        self.user = user
        self.current_user = user

        self.mongo = mongo

        # parent here is your MainApp – give AdminControlWindow an .app
        self.app = parent

        self._setup_pages()


    def has_permission(self, perm_name: str) -> bool:
        # print("CHECKING PERMISSION:", perm_name)
        result = self.app.has_permission(perm_name)
        # print("RESULT:", result)
        return result



    def _setup_pages(self):
        log_event("debug", "AdminControlWindow: setting up pages",
                user=self.user.username)
        
        self.add_page("Users",
                    lambda: UsersPage(self.user, self.mongo, parent=self),
                    required_permission="users.read")

        self.add_page("Roles",
                    lambda: RolesPage(self.mongo, parent=self))
        
        self.add_page("Stores",
            lambda: StoresListPage(self.mongo, self.current_user, parent=self),
            required_permission="stores.read"
        )
        self.add_page(
            "UOMs",
            lambda: UomManagementPage(self.mongo, self.user, parent=self),
            required_permission="uom.manage"
        )




        self.add_page("Permissions",
                    lambda: PermissionsPage(self.mongo, parent=self))

        self.add_page("Audit Log",
                    lambda: AuditLogPage(self.mongo))

        self.add_page(
            "Suppliers",
            lambda: SupplierManagementPage(self.mongo, self.user),
            required_permission="supplier.manage"
        )

