# Admin: Inventory

## Purpose
The **Inventory** page allows administrators to create and manage inventory items used throughout the system.  
Inventory items form the foundation for Sales Orders, Works Orders, BOMs, costing, and stock control.

Accurate inventory data ensures correct part selection, traceability, and workflow consistency.

---

## What You Can Do Here

### Add New Inventory Items
Click **Add** to create a new inventory item.  
Enter:

- Part number  
- Description  
- Revision  
- UOM  
- Status (active or inactive)  
- Item type (e.g., assembly, component, consumable)  
- Optional fields such as supplier, cost, notes, etc.

### Edit Existing Inventory Items
Select an item and click **Edit** to update:

- Part number  
- Description  
- Revision  
- UOM  
- Status  
- Any additional item attributes  

### Delete Inventory Items
Select an item and click **Delete** to remove it.  
An inventory item can only be deleted if it is **not** referenced by:

- BOMs  
- Sales Orders  
- Works Orders  
- Stock records  

Inactive items remain visible but cannot be selected in workflows.

---

## Key Fields

### Part Number
The unique identifier for the item.  
Use a consistent numbering scheme for clarity and traceability.

### Description
A human‑readable description of the item.

### Revision
The revision level of the item.  
Revisions allow changes to be tracked over time.

### UOM (Unit of Measure)
Defines how the item is measured (Each, Box, Kg, etc.).

### Status
Indicates whether the item is active.  
Inactive items cannot be selected in new transactions.

### Item Type
Defines how the item behaves in workflows:

- **Assembly** – can have a BOM  
- **Component** – used inside BOMs  
- **Consumable** – used variably or as required  
- **Service/Labour** – non‑material items (if enabled)

---

## Workflow Context
Inventory items are used in:

- Sales Orders  
- Works Orders  
- BOM Editor  
- Costing  
- Stock control  
- Purchasing (if enabled)

Changing an inventory item affects future workflows but does **not** alter historical records.

---

## Notes & Tips

- Keep part numbers consistent and meaningful.  
- Use revisions to track changes instead of overwriting old data.  
- Inactivate items rather than deleting them if they may be needed later.  
- Ensure UOMs are correct before releasing items to production.  
- Review BOM usage before deleting an item.

---

# Crib — Inventory

- Click **Inventory List** to populate the list.
- Click **Add** to create a new inventory item. Enter part number, description, revision, UOM, status, and item type.
- Select an inventory item and click **Edit** to update its details.
- Select an inventory item and click **Delete** to remove it. An item can only be deleted if it is **not** referenced by BOMs, orders, or stock records.
- Select an inventory item and click **Receive Stock**. Complete the dialog and save.
- Select an inventory item and click **View Batches** to view the batches making up the current stock. The 'View Batches' page has filters to make visulisation easier for large lists.
- Select an inventory item and click **Move Stock** to move a quantity of a batch from one store to another. Complete the 'Move Stock' dialog. Note the resulting moved stock will have 'MOVE-' prefixed on to it's batch number.

---

# End of File
