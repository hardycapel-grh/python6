from ui.windows.window_with_sidebar import WindowWithSidebar
from ui.pages.log_viewer_page import LogViewerPage


class LogViewerWindow(WindowWithSidebar):
    def __init__(self):
        super().__init__("Log Viewer")

        # Only one page for now
        self.add_page("Viewer", LogViewerPage())