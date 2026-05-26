from PySide6.QtCore import Qt
from ui.windows.window_with_sidebar import WindowWithSidebar
from ui.pages.admin.users_page import UsersPage
from ui.pages.admin.roles_page import RolesPage
from ui.pages.admin.permissions_page import PermissionsPage
from ui.pages.admin.audit_log_page import AuditLogPage
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

        self.add_page("Permissions",
                    lambda: PermissionsPage(self.mongo, parent=self))

        self.add_page("Audit Log",
                    lambda: AuditLogPage(self.mongo))

    
    # def _setup_pages(self):
    #     # print(">>> SETUP_PAGES SOURCE:", __file__)

    #     log_event("debug", "AdminControlWindow: setting up pages",
    #             user=self.user.username)

    #     self.add_page("Users",
    #                 lambda: UsersPage(self.user, self.mongo, parent=self),
    #                 required_permission="users.read")
        
    #     item = self.sidebar_list.item(self.sidebar_list.count() - 1)
    #     # print(">>> USERS ITEM FLAGS:", hex(int(item.flags())))
    #     # print(">>> USERS ITEM ENABLED:", bool(item.flags() & Qt.ItemIsEnabled))
    #     # print(">>> USERS ITEM SELECTABLE:", bool(item.flags() & Qt.ItemIsSelectable))
    #     # print(">>> USERS ITEM EDITABLE:", bool(item.flags() & Qt.ItemIsEditable))
    #     # print(">>> USERS ITEM CHECKABLE:", bool(item.flags() & Qt.ItemIsUserCheckable))

        
    #     # print("FACTORY FOR USERS:", self.pages["Users"])
    #     # try:
    #     #     page = self.pages["Users"]()
    #     #     print("USERS PAGE INSTANTIATED OK:", page)
    #     # except Exception as e:
    #     #     print("USERS PAGE FAILED:", e)


    #     self.add_page("Roles",
    #                 lambda: RolesPage(self.mongo, parent=self))

    #     self.add_page("Permissions",
    #                 lambda: PermissionsPage(self.mongo, parent=self))

    #     # FIX: create one persistent instance
    #     self.audit_page = AuditLogPage(self.mongo, parent=self)
    #     # self.add_page("Audit Log", lambda: self.audit_page)
    #     self.add_page("Audit Log", lambda: AuditLogPage(self.mongo))
    #     print(">>> SETUP_PAGES CALLED")



        
