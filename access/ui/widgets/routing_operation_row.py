from PySide6.QtWidgets import (
    QWidget,
    QHBoxLayout,
    QLineEdit,
    QDoubleSpinBox,
    QPushButton,
    QSizePolicy
)

from PySide6.QtCore import Signal, QSize


ROW_HEIGHT = 26


class RoutingOperationRow(QWidget):

    changed = Signal()
    remove_requested = Signal(QWidget)

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setSizePolicy(
            QSizePolicy.Preferred,
            QSizePolicy.Fixed
        )

        self.setFixedHeight(
            ROW_HEIGHT
        )

        # ---------------------------------------------------------
        # Operation Number
        # ---------------------------------------------------------
        self.operation_le = QLineEdit()
        self.operation_le.setPlaceholderText("Op")
        self.operation_le.setMaximumWidth(60)

        self.operation_le.textChanged.connect(
            self.changed
        )

        # ---------------------------------------------------------
        # Description
        # ---------------------------------------------------------
        self.description_le = QLineEdit()
        self.description_le.setPlaceholderText(
            "Operation Description"
        )

        self.description_le.textChanged.connect(
            self.changed
        )

        # ---------------------------------------------------------
        # Work Centre
        # ---------------------------------------------------------
        self.work_centre_le = QLineEdit()
        self.work_centre_le.setPlaceholderText(
            "Work Centre"
        )

        self.work_centre_le.setMaximumWidth(
            120
        )

        self.work_centre_le.textChanged.connect(
            self.changed
        )

        # ---------------------------------------------------------
        # Setup Hours
        # ---------------------------------------------------------
        self.setup_hours_sb = QDoubleSpinBox()

        self.setup_hours_sb.setDecimals(2)
        self.setup_hours_sb.setMaximum(9999)
        self.setup_hours_sb.setMinimum(0)

        self.setup_hours_sb.setMaximumWidth(
            90
        )

        self.setup_hours_sb.valueChanged.connect(
            self.changed
        )

        # ---------------------------------------------------------
        # Run Hours
        # ---------------------------------------------------------
        self.run_hours_sb = QDoubleSpinBox()

        self.run_hours_sb.setDecimals(2)
        self.run_hours_sb.setMaximum(9999)
        self.run_hours_sb.setMinimum(0)

        self.run_hours_sb.setMaximumWidth(
            90
        )

        self.run_hours_sb.valueChanged.connect(
            self.changed
        )

        # ---------------------------------------------------------
        # Operation Instruction
        # ---------------------------------------------------------
        self.operation_instruction_le = QLineEdit()

        self.operation_instruction_le.setPlaceholderText(
            "Operation Instruction"
        )

        self.operation_instruction_le.textChanged.connect(
            self.changed
        )

        # ---------------------------------------------------------
        # Notes
        # ---------------------------------------------------------
        self.notes_le = QLineEdit()

        self.notes_le.setPlaceholderText(
            "Notes"
        )

        self.notes_le.textChanged.connect(
            self.changed
        )

        # ---------------------------------------------------------
        # Remove
        # ---------------------------------------------------------
        self.remove_btn = QPushButton(
            "Remove"
        )

        self.remove_btn.clicked.connect(
            self._on_remove
        )

        # ---------------------------------------------------------
        # Layout
        # ---------------------------------------------------------
        layout = QHBoxLayout()

        layout.setContentsMargins(
            0, 0, 0, 0
        )

        layout.setSpacing(4)

        layout.addWidget(
            self.operation_le
        )

        layout.addWidget(
            self.description_le,
            stretch=1
        )

        layout.addWidget(
            self.work_centre_le
        )

        layout.addWidget(
            self.setup_hours_sb
        )

        layout.addWidget(
            self.run_hours_sb
        )

        layout.addWidget(
            self.operation_instruction_le,
            stretch=2
        )

        layout.addWidget(
            self.notes_le,
            stretch=1
        )

        layout.addWidget(
            self.remove_btn
        )

        self.setLayout(layout)

    def sizeHint(self):
        return QSize(
            0,
            ROW_HEIGHT
        )

    def _on_remove(self):

        self.remove_requested.emit(
            self
        )

        self.changed.emit()

    def get_data(self):

        operation = (
            self.operation_le.text()
            .strip()
        )

        if not operation:
            return None

        return {
            "operation": int(operation),
            "description":
                self.description_le.text()
                .strip(),

            "work_centre":
                self.work_centre_le.text()
                .strip(),

            "setup_hours":
                self.setup_hours_sb.value(),

            "run_hours":
                self.run_hours_sb.value(),

            "operation_instruction":
                self.operation_instruction_le.text()
                .strip(),

            "notes":
                self.notes_le.text()
                .strip()
        }
    
    def set_data(
        self,
        operation,
        description,
        work_centre,
        setup_hours,
        run_hours,
        operation_instruction,
        notes
    ):

        self.operation_le.setText(
            str(operation)
        )

        self.description_le.setText(
            description
        )

        self.work_centre_le.setText(
            work_centre
        )

        self.setup_hours_sb.setValue(
            float(setup_hours)
        )

        self.run_hours_sb.setValue(
            float(run_hours)
        )

        self.operation_instruction_le.setText(
            operation_instruction
        )

        self.notes_le.setText(
            notes
        )