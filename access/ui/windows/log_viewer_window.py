from ui.windows.window_with_sidebar import WindowWithSidebar
from ui.pages.log_viewer_page import LogViewerPage


class LogViewerWindow(WindowWithSidebar):
    REQUIRED_PERMISSION = "logs.read"

    def __init__(self):
        super().__init__("Log Viewer")

    def _setup_pages(self):
        self.add_page("Viewer", LogViewerPage)