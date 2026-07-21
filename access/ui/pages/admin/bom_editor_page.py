from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QMessageBox
from datetime import datetime

from ui.widgets.bom_editor_widget import BOMEditorWidget

from ui.components.logger_utils import log_event


class BOMEditorPage(QWidget):
    def __init__(self, mongo, user, parent=None):
        super().__init__(parent)

        self.mongo = mongo
        self.user = user

        self.is_dirty = False
        self.loading_bom = False

        # ---------------------------------------------------------
        # Title
        # ---------------------------------------------------------
        self.title = QLabel("Bill of Materials Editor")
        self.title.setStyleSheet("font-size: 20px; font-weight: bold;")

        # ---------------------------------------------------------
        # Load items list from DB
        # ---------------------------------------------------------
        items_list = list(self.mongo.inventory.find({}))

        # ---------------------------------------------------------
        # Editor widget
        # ---------------------------------------------------------
        self.editor = BOMEditorWidget(items_list)
        self.editor.dirty_changed.connect(self._on_dirty_changed)
        self.editor.save_requested.connect(self._save_bom_to_db)
        self.editor.assembly_cb.currentIndexChanged.connect(self._auto_increment_revision)


        # ---------------------------------------------------------
        # Layout
        # ---------------------------------------------------------
        layout = QVBoxLayout()
        layout.addWidget(self.title)
        layout.addWidget(self.editor)
        layout.setContentsMargins(6, 6, 6, 6)
        self.setLayout(layout)

    # ---------------------------------------------------------
    # SAVE BOM
    # ---------------------------------------------------------
    def _save_bom_to_db(self, bom_data):
        log_event(
            "info",
            "Saving BOM",
            user=self.user.username,
            assembly=bom_data.get("assembly_part_number"),
            assembly_revision=bom_data.get("assembly_revision"),
            revision=bom_data.get("revision"),
            line_count=len(bom_data.get("lines", []))
        )

        self.mongo.log_event(
            "bom.save",
            performed_by=self.user.username,
            details=(
                f"Saved BOM for assembly {bom_data.get('assembly_part_number')} "
                f"rev {bom_data.get('assembly_revision')} BOM rev {bom_data.get('revision')}"
            )
        )

        bom_data["created_by"] = self.user.username
        bom_data["created_at"] = datetime.utcnow()

        try:
            self.mongo.bom.insert_one(bom_data)

            QMessageBox.information(self, "Saved", "BOM saved successfully.")

            # Recalculate next revision after save
            self._auto_increment_revision()

            log_event(
                "info",
                "BOM saved successfully",
                user=self.user.username,
                assembly=bom_data.get("assembly_part_number"),
                revision=bom_data.get("revision")
            )

        except Exception as e:
            log_event(
                "error",
                "Failed to save BOM",
                user=self.user.username,
                error=str(e)
            )

            self.mongo.log_event(
                "bom.save.error",
                performed_by=self.user.username,
                details=f"Error saving BOM: {e}"
            )

            self.clear_dirty()
            QMessageBox.critical(self, "Error", f"Failed to save BOM:\n{e}")

    # ---------------------------------------------------------
    # AUTO-INCREMENT + LOAD EXISTING BOM
    # ---------------------------------------------------------


    def _auto_increment_revision(self):

        self.loading_bom = True   # <-- FIXED: moved above

        latest_bom = self.mongo.bom.find_one(
            {"assembly_part_number": self.editor.assembly_cb.currentData()["part_number"]},
            sort=[("revision", -1)]
        )

        if latest_bom:
            self._load_bom_into_editor(latest_bom)


        

        assembly = self.editor.assembly_cb.currentData()
        if not assembly:
            self.loading_bom = False
            return

        part_number = assembly.get("part_number")
        assembly_rev = assembly.get("revision")

        if not part_number or not assembly_rev:
            self.loading_bom = False
            return

        # Find existing BOMs
        existing_boms = list(self.mongo.bom.find({
            "assembly_part_number": part_number,
            "assembly_revision": assembly_rev
        }))

        numeric_boms = []
        for bom in existing_boms:
            try:
                numeric_boms.append((int(bom["revision"]), bom))
            except ValueError:
                pass

        # -----------------------------------------------------
        # CASE 1: Existing BOMs found → load latest BOM
        # -----------------------------------------------------
        if numeric_boms:
            numeric_boms.sort(key=lambda x: x[0])
            latest_rev, latest_bom = numeric_boms[-1]

            self.mongo.log_event(
                "bom.load",
                performed_by=self.user.username,
                details=f"Loaded BOM rev {latest_rev} for assembly {part_number} rev {assembly_rev}"
            )

            log_event(
                "info",
                "Loaded existing BOM",
                user=self.user.username,
                assembly=part_number,
                assembly_revision=assembly_rev,
                bom_revision=latest_rev
            )

            self._load_bom_into_editor(latest_bom)

            next_rev = str(latest_rev + 1)
            self.editor.next_revision = next_rev

            self.editor.revision_cb.clear()
            self.editor.revision_cb.addItem(next_rev)
            self.editor.revision_cb.setEnabled(False)

            self.loading_bom = False
            return

        # -----------------------------------------------------
        # CASE 2: No BOMs exist → start at revision 1
        # -----------------------------------------------------
        next_rev = "1"

        self.mongo.log_event(
            "bom.autoincrement",
            performed_by=self.user.username,
            details=f"No existing BOMs. Starting at revision {next_rev} for assembly {part_number} rev {assembly_rev}"
        )

        log_event(
            "info",
            "Auto-increment BOM revision",
            user=self.user.username,
            assembly=part_number,
            assembly_revision=assembly_rev,
            next_revision=next_rev
        )

        self.editor.next_revision = next_rev
        self.editor.revision_cb.clear()
        self.editor.revision_cb.addItem(next_rev)
        self.editor.revision_cb.setEnabled(False)

        self.loading_bom = False

    # ---------------------------------------------------------
    # Load BOM into editor
    # ---------------------------------------------------------
    def _load_bom_into_editor(self, bom_doc):

        # Prevent dirty flag during auto-load
        self.editor.block_dirty_signals = True

        self.editor.loaded_revision = bom_doc["revision"]
        self.editor.clear_rows()

        for line in bom_doc.get("lines", []):
            self.editor.add_row(
                component_part_number=line.get("component_part_number"),
                component_revision=line.get("component_revision"),
                quantity=line.get("quantity"),
                uom=line.get("uom"),
                comments=line.get("comments", ""),
                quantity_type=line.get("quantity_type", "Fixed")
            )

        # Re-enable dirty flag
        self.editor.block_dirty_signals = False

        # Loaded BOM is clean
        self._on_dirty_changed(False)

    # ---------------------------------------------------------
    # Dirty flag (manual use in error paths)
    # ---------------------------------------------------------
    def mark_dirty(self):
        if not self.is_dirty:
            self.is_dirty = True
            self.title.setText("Bill of Materials Editor *")

    def clear_dirty(self):
        if self.is_dirty:
            self.is_dirty = False
            self.title.setText("Bill of Materials Editor")

    # ---------------------------------------------------------
    # Dirty flag handler (from widget.dirty_changed)
    # ---------------------------------------------------------
    def _on_dirty_changed(self, is_dirty: bool):
        self.is_dirty = is_dirty
        if is_dirty:
            self.title.setText("Bill of Materials Editor *")
        else:
            self.title.setText("Bill of Materials Editor")
