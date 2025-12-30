from dashboard_page import DashboardPage
from data_table_page import DataTablePage
from charts_page import ChartsPage
from admin_page import AdminPage
from log_viewer_page import LogViewerPage

# Central registry for all pages in the application.
# Each entry defines:
# - The page class
# - The default permission for new users
# - The title (taken from the page class itself)

PAGE_REGISTRY = {
    "Dashboard": {
        "class": DashboardPage,
        "default_permission": "rw"
    },
    "Data Table": {
        "class": DataTablePage,
        "default_permission": "ro"
    },
    "Charts": {
        "class": ChartsPage,
        "default_permission": "ro"
    },
    "Admin": {
        "class": AdminPage,
        "default_permission": None
    },
        "Log Viewer": {
        "class": LogViewerPage,
        "default_permission": None   # Only admins see it
    }
}


