from PySide6.QtWidgets import QWidget, QVBoxLayout, QLineEdit, QListWidget, QListWidgetItem
from PySide6.QtCore import Signal


class AssemblySearchWidget(QWidget):
    assembly_selected = Signal(dict)

    def __init__(self, assemblies: list[dict], parent=None):
        super().__init__(parent)

        self.assemblies = assemblies

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(4)

        self.search_le = QLineEdit()
        self.search_le.setPlaceholderText("Search assemblies...")
        self.search_le.textChanged.connect(self._filter_results)
        layout.addWidget(self.search_le)

        self.results_list = QListWidget()
        self.results_list.itemClicked.connect(self._select_item)
        layout.addWidget(self.results_list)

        self._filter_results("")

    def _filter_results(self, text: str):
        text = text.lower().strip()
        self.results_list.clear()

        for item in self.assemblies:
            label = f"{item['part_number']} (Rev {item['revision']})"
            searchable = f"{item['part_number']} {item['revision']}".lower()

            if text in searchable:
                lw = QListWidgetItem(label)
                lw.setData(1000, item)
                self.results_list.addItem(lw)

    def _select_item(self, lw_item):
        item = lw_item.data(1000)
        self.assembly_selected.emit(item)
