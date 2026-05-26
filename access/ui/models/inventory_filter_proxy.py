from PySide6.QtCore import QSortFilterProxyModel, Qt

class InventoryFilterProxyModel(QSortFilterProxyModel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.search_text = ""
        self.type_filter = "All Types"
        self.status_filter = "All Status"
        self.makebuy_filter = "All"

    def set_filters(self, search_text, type_filter, status_filter, makebuy_filter):
        self.search_text = search_text.lower()
        self.type_filter = type_filter
        self.status_filter = status_filter
        self.makebuy_filter = makebuy_filter
        self.invalidateFilter()

    def filterAcceptsRow(self, row, parent):
        model = self.sourceModel()
        if model is None:
            return True

        # Extract row data
        row_data = [
            model.index(row, col).data()
            for col in range(model.columnCount())
        ]

        # Search filter
        if self.search_text:
            if not any(self.search_text in str(cell).lower() for cell in row_data):
                return False

        # Type filter
        if self.type_filter != "All Types":
            if row_data[2] != self.type_filter:
                return False

        # Status filter
        if self.status_filter != "All Status":
            if row_data[9] != self.status_filter:
                return False

        # Make/Buy filter
        if self.makebuy_filter != "All":
            if row_data[4] != self.makebuy_filter:
                return False

        return True
