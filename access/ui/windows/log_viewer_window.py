from ui.windows.window_with_sidebar import WindowWithSidebar
from ui.pages.log_viewer_page import LogViewerPage   # or whatever your page is called

class LogViewerWindow(WindowWithSidebar):
    def __init__(self, user):
        self.current_user = user      # <-- REQUIRED
        super().__init__("Log Viewer")

    def _setup_pages(self):
        self.add_page("Viewer", LogViewerPage)
