# ui/pages/admin/bom_editor_page.py

from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QMessageBox
from ui.widgets.bom_editor_widget import BOMEditorWidget
from datetime import datetime
from ui.components.logger_utils import log_event


class BOMEditorPage(QWidget):
    def __init__(self, mongo, user, parent=None):
        super().__init__(parent)

        self.mongo = mongo
        self.user = user

        # Log page load
        log_event(
            "info",
            "Opened BOM Editor Page",
            user=self.user.username
        )

        # Audit page load
        self.mongo.log_event(
            "bom.page.open",
            performed_by=self.user.username,
            details="Opened BOM Editor Page"
        )

        # Load UOM metadata
        uoms = {u["uom"]: u for u in self.mongo.uom_list.find({})}

        items_list = []
        for item in self.mongo.inventory.find({}):
            uom = item["uom"]
            item["uom_quantity_type"] = uoms.get(uom, {}).get("quantity_type", "decimal")
            items_list.append(item)

        layout = QVBoxLayout()
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(12)

        title = QLabel("Bill of Materials Editor")
        title.setStyleSheet("font-size: 20px; font-weight: bold;")

        self.editor = BOMEditorWidget(items_list)

        layout.addWidget(title)
        layout.addWidget(self.editor)
        self.setLayout(layout)

        # Connect signals
        self.editor.save_requested.connect(self._save_bom_to_db)
        self.editor.assembly_cb.currentIndexChanged.connect(self._auto_increment_revision)


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

        # Audit
        self.mongo.log_event(
            "bom.save",
            performed_by=self.user.username,
            details=f"Saved BOM for assembly {bom_data.get('assembly_part_number')} "
                    f"rev {bom_data.get('assembly_revision')} BOM rev {bom_data.get('revision')}"
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

            QMessageBox.critical(self, "Error", f"Failed to save BOM:\n{e}")


    # ---------------------------------------------------------
    # AUTO-INCREMENT + LOAD EXISTING BOM
    # ---------------------------------------------------------
    def _auto_increment_revision(self):

        assembly = self.editor.assembly_cb.currentData()
        if not assembly:
            return

        part_number = assembly.get("part_number")
        assembly_rev = assembly.get("revision")

        if not part_number or not assembly_rev:
            return

        # Find existing BOMs
        existing_boms = list(self.mongo.bom.find({
            "assembly_part_number": part_number,
            "assembly_revision": assembly_rev
        }))

        # Extract numeric revisions
        numeric_boms = []
        for bom in existing_boms:
            try:
                numeric_boms.append((int(bom["revision"]), bom))
            except:
                pass

        # -----------------------------------------------------
        # CASE 1: Existing BOMs found → load latest BOM
        # -----------------------------------------------------
        if numeric_boms:
            numeric_boms.sort(key=lambda x: x[0])
            latest_rev, latest_bom = numeric_boms[-1]

            # Log + audit
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

            # Load BOM lines into editor
            self._load_bom_into_editor(latest_bom)

            # Compute next revision
            next_rev = str(latest_rev + 1)

            # Store next revision (UI will show this)
            self.editor.next_revision = next_rev

            # Update revision UI
            self.editor.revision_cb.clear()
            self.editor.revision_cb.addItem(next_rev)
            self.editor.revision_cb.setEnabled(False)

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

        # Store next revision
        self.editor.next_revision = next_rev

        # Update revision UI
        self.editor.revision_cb.clear()
        self.editor.revision_cb.addItem(next_rev)
        self.editor.revision_cb.setEnabled(False)


    # ---------------------------------------------------------
    # LOAD EXISTING BOM INTO EDITOR
    # ---------------------------------------------------------
    def _load_bom_into_editor(self, bom_doc):
        """
        Populate the BOM editor UI with an existing BOM document.
        """

        # Store loaded revision internally (NOT shown in UI)
        self.editor.loaded_revision = bom_doc["revision"]

        # Clear existing rows
        self.editor.clear_rows()

        # Add BOM lines
        for line in bom_doc.get("lines", []):
            self.editor.add_row(
                component_part_number=line.get("component_part_number"),
                component_revision=line.get("component_revision"),
                quantity=line.get("quantity"),
                uom=line.get("uom"),
                comments=line.get("comments", "")
            )
