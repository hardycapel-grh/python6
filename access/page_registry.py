from ui.pages.dashboard_page import DashboardPage
from ui.pages.data_table_page import DataTablePage
from ui.pages.charts_page import ChartsPage
from ui.pages.admin_page import AdminPage
# from log_viewer_page import LogViewerPage
from ui.pages.profile_page import ProfilePage
from AdminControlPanel import AdminControlPanel
from ui.pages.example_page import ExamplePage


# Central registry for all pages in the application.
# Each entry defines:
# - class: the page class
# - slug: stable internal identifier (safe for DB keys)
# - default_permission: permission new users get ("rw", "ro", None)
# - requires_admin: whether only admins can access it
# - category: used for sidebar grouping
# - visible: whether it appears in the sidebar
# - description: optional tooltip/help text



PAGE_REGISTRY = {
    "Dashboard": {
        "class": DashboardPage,
        "slug": "dashboard",
        "default_permission": "rw",
        "requires_admin": False,
        "category": "General",
        "visible": True,
        "description": "Overview of system activity and quick actions"
    },

    "Data Table": {
        "class": DataTablePage,
        "slug": "data_table",
        "default_permission": "ro",
        "requires_admin": False,
        "category": "Data",
        "visible": True,
        "description": "View and explore tabular data"
    },

    "Charts": {
        "class": ChartsPage,
        "slug": "charts",
        "default_permission": "ro",
        "requires_admin": False,
        "category": "Data",
        "visible": True,
        "description": "Visualize data using charts and graphs"
    },

    "Profile": {
        "class": ProfilePage,
        "slug": "profile",
        "default_permission": "rw",
        "requires_admin": False,
        "category": "User",
        "visible": True,
        "description": "Edit your personal profile and settings"
    },

    "Admin": {
        "class": AdminPage,
        "slug": "admin",
        "default_permission": None,
        "requires_admin": True,
        "category": "Admin Tools",
        "visible": True,
        "description": "Admin-only tools and system management"
    },

    # Log Viewer removed — now opened in its own window
    
    "Example Page": {
        "class": ExamplePage,
        "default_permission": "none"   # or "rw" if you want it visible by default
    },
    "Admin Control Panel": {
        "class": AdminControlPanel,
        "default_permission": "rw"
    }

}
