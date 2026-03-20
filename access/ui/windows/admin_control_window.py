from ui.windows.window_with_sidebar import WindowWithSidebar
from ui.pages.user_manager_page import UserManagerPage
from ui.pages.permission_editor_page import PermissionEditorPage

class AdminControlWindow(WindowWithSidebar):
    REQUIRED_PERMISSION = "users.read"

    def __init__(self, current_user):
        self.current_user = current_user
        super().__init__("Admin Control Panel")

    def _setup_pages(self):
        self.add_page("Users", lambda: UserManagerPage())
        self.add_page("Permissions", lambda: PermissionEditorPage(self.current_user))
