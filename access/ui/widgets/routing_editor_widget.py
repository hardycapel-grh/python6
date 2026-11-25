from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QScrollArea,
    QFrame,
    QSizePolicy
)

from PySide6.QtCore import Signal

from ui.widgets.routing_operation_row import (
    RoutingOperationRow
)


class RoutingEditorWidget(QWidget):

    save_requested = Signal(dict)

    dirty_changed = Signal(bool)

    def __init__(self, parent=None):
        super().__init__(parent)

        self.is_dirty = False
        self.block_dirty_signals = False

        # ---------------------------------------------------------
        # Buttons
        # ---------------------------------------------------------
        self.add_btn = QPushButton(
            "Add Operation"
        )

        self.save_btn = QPushButton(
            "Save Routing"
        )

        self.add_btn.clicked.connect(
            self._add_operation
        )

        self.save_btn.clicked.connect(
            self._save_routing
        )

        # ---------------------------------------------------------
        # Operations Container
        # ---------------------------------------------------------
        self.operations_container = QWidget()

        self.operations_container.setSizePolicy(
            QSizePolicy.Preferred,
            QSizePolicy.Maximum
        )

        self.operations_layout = QVBoxLayout()

        self.operations_layout.setSpacing(0)

        self.operations_layout.setContentsMargins(
            0,
            0,
            0,
            0
        )

        self.operations_container.setLayout(
            self.operations_layout
        )

        # ---------------------------------------------------------
        # Scroll Area
        # ---------------------------------------------------------
        scroll = QScrollArea()

        scroll.setWidgetResizable(True)

        scroll.setWidget(
            self.operations_container
        )

        # ---------------------------------------------------------
        # Toolbar
        # ---------------------------------------------------------
        toolbar = QHBoxLayout()

        toolbar.setContentsMargins(
            0,
            0,
            0,
            0
        )

        toolbar.addWidget(
            self.add_btn
        )

        toolbar.addWidget(
            self.save_btn
        )

        toolbar.addStretch()

        # ---------------------------------------------------------
        # Main Layout
        # ---------------------------------------------------------
        layout = QVBoxLayout()

        layout.addLayout(
            toolbar
        )

        layout.addWidget(
            scroll
        )

        layout.setContentsMargins(
            6,
            6,
            6,
            6
        )

        self.setLayout(layout)

    # ---------------------------------------------------------
    # Dirty Handling
    # ---------------------------------------------------------
    def _set_dirty(self, value):

        if self.block_dirty_signals:
            return

        self.is_dirty = value

        self.dirty_changed.emit(value)

    def _clear_dirty(self):

        self._set_dirty(False)

    # ---------------------------------------------------------
    # Add Operation
    # ---------------------------------------------------------
    def _add_operation(self):

        row = RoutingOperationRow()

        row.remove_requested.connect(
            self._remove_operation
        )

        row.changed.connect(
            lambda: self._set_dirty(True)
        )

        frame = QFrame()

        frame_layout = QVBoxLayout(frame)

        frame_layout.setContentsMargins(
            0,
            0,
            0,
            0
        )

        frame_layout.setSpacing(0)

        frame_layout.addWidget(row)

        self.operations_layout.addWidget(
            frame
        )

        self._set_dirty(True)

    # ---------------------------------------------------------
    # Remove Operation
    # ---------------------------------------------------------
    def _remove_operation(
        self,
        row_widget
    ):

        row_widget.setParent(None)

        row_widget.deleteLater()

        self._set_dirty(True)

    # ---------------------------------------------------------
    # Clear Operations
    # ---------------------------------------------------------
    def clear_operations(self):

        while self.operations_layout.count() > 0:

            item = self.operations_layout.takeAt(0)

            widget = item.widget()

            if widget:

                widget.setParent(None)

                widget.deleteLater()

    # ---------------------------------------------------------
    # Load Existing Operation
    # ---------------------------------------------------------
    def add_operation(
        self,
        operation,
        description,
        work_centre,
        setup_hours,
        run_hours,
        operation_instruction,
        notes
    ):

        row = RoutingOperationRow()

        row.set_data(
            operation=operation,
            description=description,
            work_centre=work_centre,
            setup_hours=setup_hours,
            run_hours=run_hours,
            operation_instruction=operation_instruction,
            notes=notes
        )

        row.remove_requested.connect(
            self._remove_operation
        )

        row.changed.connect(
            lambda: self._set_dirty(True)
        )

        frame = QFrame()

        frame_layout = QVBoxLayout(frame)

        frame_layout.setContentsMargins(
            0,
            0,
            0,
            0
        )

        frame_layout.setSpacing(0)

        frame_layout.addWidget(row)

        self.operations_layout.addWidget(
            frame
        )

    # ---------------------------------------------------------
    # Extract Routing Data
    # ---------------------------------------------------------
    def get_routing_data(self):

        operations = []

        for i in range(
            self.operations_layout.count()
        ):

            frame = (
                self.operations_layout
                .itemAt(i)
                .widget()
            )

            if not frame:
                continue

            row = frame.findChild(
                RoutingOperationRow
            )

            if not row:
                continue

            data = row.get_data()

            if data:
                operations.append(data)

        # ---------------------------------------------------------
        # Sort by operation number before saving
        # ---------------------------------------------------------
        operations.sort(
            key=lambda op: int(op.get("operation", 0))
        )

        return operations

    # ---------------------------------------------------------
    # Save
    # ---------------------------------------------------------
    def _save_routing(self):

        self.save_requested.emit({
            "operations":
                self.get_routing_data()
        })

        self._clear_dirty()