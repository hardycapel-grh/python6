from datetime import datetime

from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QComboBox
)

from ui.widgets.routing_editor_widget import (
    RoutingEditorWidget
)

from ui.widgets.assembly_search_widget import (
    AssemblySearchWidget
)

from ui.components.logger_utils import (
    log_event
)


class RoutingEditorPage(QWidget):

    def __init__(
        self,
        mongo,
        user,
        parent=None
    ):
        super().__init__(parent)

        self.mongo = mongo
        self.user = user

        self.is_dirty = False
        self.loading_routing = False

        self.work_centres = list(
            self.mongo.work_centres.find(
                {"active": True}
            )
        )

        # ---------------------------------------------------------
        # Title
        # ---------------------------------------------------------
        self.title = QLabel(
            "Routing Editor"
        )

        self.title.setStyleSheet(
            "font-size: 20px; font-weight: bold;"
        )

        # ---------------------------------------------------------
        # Inventory items
        # ---------------------------------------------------------
        self.items_list = list(
            self.mongo.inventory.find({})
        )

        # ---------------------------------------------------------
        # Search
        # ---------------------------------------------------------
        self.search_widget = (
            AssemblySearchWidget(
                self.items_list
            )
        )

        self.search_widget.selected_item_changed.connect(
            self._on_item_selected
        )

        self.search_widget.setFixedWidth(
            240
        )

        # ---------------------------------------------------------
        # Routing Editor
        # ---------------------------------------------------------
        self.editor = RoutingEditorWidget(
            self.work_centres
        )

        self.editor.dirty_changed.connect(
            self._on_dirty_changed
        )

        self.editor.save_requested.connect(
            self._save_routing_to_db
        )

        # ---------------------------------------------------------
        # Assembly Selector
        # ---------------------------------------------------------
        self.editor.assembly_cb = QComboBox()

        for item in self.items_list:

            label = (
                f"{item['part_number']} "
                f"(Rev {item['revision']})"
            )

            self.editor.assembly_cb.addItem(
                label
            )

            index = (
                self.editor.assembly_cb.count()
                - 1
            )

            self.editor.assembly_cb.setItemData(
                index,
                item
            )

        self.editor.assembly_cb.currentIndexChanged.connect(
            self._auto_increment_revision
        )

        # ---------------------------------------------------------
        # Routing Revision Selector
        # ---------------------------------------------------------
        self.editor.revision_cb = QComboBox()

        self.editor.revision_cb.addItems(
            ["1"]
        )

        # ---------------------------------------------------------
        # Insert controls above editor
        # ---------------------------------------------------------
        controls = QHBoxLayout()

        controls.addWidget(
            QLabel("Assembly:")
        )

        controls.addWidget(
            self.editor.assembly_cb
        )

        controls.addSpacing(20)

        controls.addWidget(
            QLabel("Routing Revision:")
        )

        controls.addWidget(
            self.editor.revision_cb
        )

        controls.addStretch()

        # ---------------------------------------------------------
        # Layout
        # ---------------------------------------------------------
        main_layout = QVBoxLayout()

        main_layout.addWidget(
            self.title
        )

        content_layout = QHBoxLayout()

        content_layout.addWidget(
            self.search_widget,
            stretch=0
        )

        editor_container = QVBoxLayout()

        editor_container.addLayout(
            controls
        )

        editor_container.addWidget(
            self.editor
        )

        content_layout.addLayout(
            editor_container,
            stretch=1
        )

        main_layout.addLayout(
            content_layout
        )

        self.setLayout(
            main_layout
        )





    # ---------------------------------------------------------
    # Save Routing
    # ---------------------------------------------------------
    def _save_routing_to_db(
        self,
        routing_data
    ):

        assembly = (
            self.editor.assembly_cb.currentData()
        )

        if not assembly:

            QMessageBox.warning(
                self,
                "No Assembly",
                "Please select an assembly."
            )

            return

        routing_doc = {

            "assembly_part_number":
                assembly["part_number"],

            "assembly_revision":
                assembly["revision"],

            "revision":
                self.editor.revision_cb.currentText(),

            "operations":
                routing_data.get(
                    "operations",
                    []
                ),

            "created_by":
                self.user.username,

            "created_at":
                datetime.utcnow()
        }

        try:

            self.mongo.routing.insert_one(
                routing_doc
            )

            QMessageBox.information(
                self,
                "Saved",
                "Routing saved successfully."
            )

            self._auto_increment_revision()

        except Exception as e:

            QMessageBox.critical(
                self,
                "Error",
                f"Failed to save routing:\n{e}"
            )

    # ---------------------------------------------------------
    # Auto Increment Revision
    # ---------------------------------------------------------
    def _auto_increment_revision(self):

        if self.loading_routing:
            return

        assembly = (
            self.editor.assembly_cb.currentData()
        )

        if not assembly:
            return

        part_number = (
            assembly["part_number"]
        )

        assembly_revision = (
            assembly["revision"]
        )

        routings = list(
            self.mongo.routing.find({
                "assembly_part_number":
                    part_number,

                "assembly_revision":
                    assembly_revision
            })
        )

        numeric_revs = []

        for routing in routings:

            try:

                numeric_revs.append(
                    int(
                        routing.get(
                            "revision",
                            0
                        )
                    )
                )

            except Exception:
                pass

        if numeric_revs:

            latest_rev = max(
                numeric_revs
            )

            self.editor.revision_cb.clear()

            self.editor.revision_cb.addItem(
                str(latest_rev + 1)
            )

        else:

            self.editor.revision_cb.clear()

            self.editor.revision_cb.addItem(
                "1"
            )

        self.editor.revision_cb.setEnabled(
            False
        )

        latest_routing = self.mongo.routing.find_one(
            {
                "assembly_part_number":
                    part_number,

                "assembly_revision":
                    assembly_revision
            },
            sort=[("created_at", -1)]
        )

        if latest_routing:

            self._load_routing_into_editor(
                latest_routing
            )

        else:

            self._clear_routing_editor()

    # ---------------------------------------------------------
    # Load Routing
    # ---------------------------------------------------------
    def _load_routing_into_editor(
        self,
        routing_doc
    ):

        self.editor.block_dirty_signals = True

        self.editor.clear_operations()

        for op in routing_doc.get(
            "operations",
            []
        ):

            self.editor.add_operation(
                operation=op.get(
                    "operation",
                    ""
                ),

                description=op.get(
                    "description",
                    ""
                ),

                work_centre=op.get(
                    "work_centre",
                    ""
                ),

                setup_hours=op.get(
                    "setup_hours",
                    0
                ),

                run_hours=op.get(
                    "run_hours",
                    0
                ),

                operation_instruction=op.get(
                    "operation_instruction",
                    ""
                ),

                notes=op.get(
                    "notes",
                    ""
                )
            )

        self.editor.block_dirty_signals = False

        self._on_dirty_changed(
            False
        )

    # ---------------------------------------------------------
    # Dirty Handling
    # ---------------------------------------------------------
    def _on_dirty_changed(
        self,
        is_dirty
    ):

        self.is_dirty = is_dirty

        if is_dirty:

            self.title.setText(
                "Routing Editor *"
            )

        else:

            self.title.setText(
                "Routing Editor"
            )

    # ---------------------------------------------------------
    # Search Selection
    # ---------------------------------------------------------
    def _on_item_selected(
        self,
        item_dict
    ):

        cb = self.editor.assembly_cb

        target_part = item_dict.get(
            "part_number"
        )

        target_rev = item_dict.get(
            "revision"
        )

        for i in range(cb.count()):

            data = cb.itemData(i)

            if not data:
                continue

            if (
                data.get("part_number")
                == target_part
                and
                data.get("revision")
                == target_rev
            ):

                current = cb.currentIndex()

                if current == i:
                    self._auto_increment_revision()
                else:
                    cb.setCurrentIndex(i)


    def _clear_routing_editor(self):
        self.editor.block_dirty_signals = True
        self.editor.clear_operations()
        self.editor.block_dirty_signals = False
        self._on_dirty_changed(False)            