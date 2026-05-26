# ui/windows/inventory_window.py

from ui.windows.window_with_sidebar import WindowWithSidebar
from ui.components.logger_utils import log_event

class InventoryWindow(WindowWithSidebar):
    def __init__(self, user, mongo, parent=None):
        super().__init__("Inventory", parent)

        self.user = user
        self.mongo = mongo
        self.current_user = user   # IMPORTANT: WindowWithSidebar expects this
        self.app = parent

        log_event("info", "InventoryWindow initialized", user=user.username)

        # Audit log
        try:
            self.mongo.log_event(
                event="inventory.window.open",
                performed_by=self.user.username,
                details="Opened Inventory module"
            )
        except Exception as e:
            log_event("error", "Failed to write audit log", error=str(e))

        self._setup_pages()

    def _setup_pages(self):
        # Add the Inventory List page
        self.add_page(
            "Inventory List",
            lambda: self._open_inventory_list(),
            required_permission="inventory.read"
        )

    def _open_inventory_list(self):
        log_event("info", "Opening Inventory List Page", user=self.user.username)

        from ui.pages.inventory.inventory_list_page import InventoryListPage
        return InventoryListPage(self.user, self.mongo, parent=self)
