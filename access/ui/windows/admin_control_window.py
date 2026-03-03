from ui.windows.window_with_sidebar import WindowWithSidebar
from ui.pages.user_manager_page import UserManagerPage
from ui.pages.permission_editor_page import PermissionEditorPage


class AdminControlWindow(WindowWithSidebar):
    def __init__(self):
        super().__init__("Admin Control Panel")

        # Register pages
        self.add_page("Users", UserManagerPage())
        self.add_page("Permissions", PermissionEditorPage())