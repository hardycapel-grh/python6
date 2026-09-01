# File: ui/models/workbench_filter_proxy.py

from xml.parsers.expat import model

from PySide6.QtCore import QSortFilterProxyModel, Qt


class WorkbenchFilterProxyModel(QSortFilterProxyModel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._type_filter = "All"
        self._status_filter = "All"
        self._search_filter = ""
        self._held_filter = "All"


        self.setFilterCaseSensitivity(Qt.CaseInsensitive)
        self.setSortCaseSensitivity(Qt.CaseInsensitive)

    # -----------------------------
    # Public setters
    # -----------------------------
    def set_type_filter(self, value: str):
        self._type_filter = value or "All"
        self.invalidateFilter()

    def set_status_filter(self, value: str):
        self._status_filter = value or "All"
        self.invalidateFilter()

    def set_search_filter(self, value: str):
        self._search_filter = value or ""
        self.invalidateFilter()

    # -----------------------------
    # Core filter logic
    # -----------------------------
    def filterAcceptsRow(self, source_row, source_parent):
        model = self.sourceModel()
        if model is None:
            return False

        idx_type = model.index(source_row, 0, source_parent)
        idx_number = model.index(source_row, 1, source_parent)
        idx_customer = model.index(source_row, 2, source_parent)
        idx_req_date = model.index(source_row, 3, source_parent)
        idx_status = model.index(source_row, 4, source_parent)
        idx_held = model.index(source_row, 6, source_parent)  # new column
        held_value = model.data(idx_held) == "Yes"


        order_type = model.data(idx_type) or ""
        order_number = model.data(idx_number) or ""
        customer = model.data(idx_customer) or ""
        req_date = model.data(idx_req_date) or ""
        status = model.data(idx_status) or ""

        # Type filter
        if self._type_filter != "All" and order_type != self._type_filter:
            return False

        # Status filter
        if self._status_filter != "All" and status != self._status_filter:
            return False

        # Search filter (number, customer, date, status)
        if self._search_filter:
            text = f"{order_number} {customer} {req_date} {status}".lower()
            if self._search_filter.lower() not in text:
                return False

        # Held filter
        if self._held_filter == "Held Only" and not held_value:
            return False

        if self._held_filter == "Not Held" and held_value:
            return False

        return True

    def set_held_filter(self, value: str):
        self._held_filter = value or "All"
        self.invalidateFilter()
