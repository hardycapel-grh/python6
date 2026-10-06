# Admin: BOM Editor

## Purpose
The **BOM Editor** allows administrators to create and manage Bills of Materials (BOMs) for items and assemblies.  
A BOM defines the components, quantities, and structure required to build or assemble a product.

This page is essential for manufacturing, repair workflows, and any process that relies on structured component lists.

---

## What You Can Do Here

### Create New BOMs
Define a new Bill of Materials for an item or assembly, including:

- Component items  
- Required quantities  
- Units of measure  
- Optional notes or instructions  

### Edit Existing BOMs
Modify BOM structures to reflect changes in design, materials, or production requirements.

### Add or Remove Components
Update the list of components that make up an item.  
This includes adjusting quantities or replacing obsolete parts.

### Manage Nested BOMs
Some items may contain sub‑assemblies with their own BOMs.  
The BOM Editor supports hierarchical structures where components can themselves have BOMs.

### Validate BOM Structure
Ensure that:

- All components exist  
- UOMs are correct  
- Quantities are valid  
- No circular references exist  

### Delete BOMs
Remove BOMs that are no longer required.  
(Only possible if they are not referenced by active workflows.)

---

## Key Fields

### Parent Item
The item or assembly that the BOM belongs to.

### Component Item
An item required to build the parent item.

### Quantity
The amount of the component needed.

### Unit of Measure (UOM)
The measurement unit for the component quantity, such as:

- Each  
- Kg  
- Metre  
- Pack  

### Notes
Optional instructions or comments related to assembly or component usage.

### Structure
Indicates whether the BOM is:

- Flat (simple list of components)  
- Nested (components with their own BOMs)

---

## Permissions Required
To access the BOM Editor, you typically need:

- `bom.manage`  
- or a broader admin permission such as `admin.access`

If you cannot see this page, your role may not include BOM‑management capabilities.

---

## Workflow Context
The BOM Editor is part of the Admin module and sits outside the main operational workflow.  
It supports the workflow by ensuring:

- Items have correct component structures  
- Manufacturing and repair processes use accurate data  
- Inventory consumption is predictable  
- Works Orders can reference correct BOMs  

Incorrect BOM configuration can lead to production errors, missing components, or inaccurate stock usage.

---

## Notes & Tips

- Keep BOMs up‑to‑date with design or material changes.  
- Use nested BOMs for complex assemblies to keep structures clean.  
- Verify UOMs before adding components to avoid quantity confusion.  
- Review BOM usage before deleting or modifying components.  
- Avoid circular references — an item cannot contain itself as a component.

---

## Crib

- Select an inventory item from the left pane. (Use the search or the drop down to aid searching through the inventory items).
- Click 'Add Component', start typing the component part number and then select. 
- Enter the quantity depending on the unit of measure.
- Select between 'Fixed', 'As required', and 'provisioned'.
- Add a comment if required.

- The differences between: 'Fixed', 'As required', and 'provisioned':
- Fixed
Meaning:  
A normal BOM quantity. The component is consumed in a predictable, measurable amount every time the assembly is built.
Use when:
Screws, bolts, washers
PCB, housing, cable
Resin, paint, adhesive (if measured per build)
Behaviour:
Quantity required
UOM required
Used every build
Included in cost roll‑ups and material planning

- As Required
Meaning:  
Used variably depending on the job. No fixed quantity. The technician decides how much is needed.
Use when:
Glue, solvent, cleaning alcohol
Touch‑up paint
Cable ties, heat‑shrink
Any consumable with unpredictable usage
Behaviour:
Quantity ignored
UOM optional
Still considered “used” during the build
Not included in strict material planning
Appears on BOM for visibility only

- Provisioned
Meaning:  
Item must be available, but is not consumed per build. It’s stocked occasionally or used only sometimes.
Use when:
Tools required for assembly
PPE items
Spare fuses, filters
Lubricants used only during service intervals
Maintenance consumables
Behaviour:
Quantity ignored
UOM optional
Not consumed per build
Not included in cost roll‑ups
Included in BOM for provisioning/documentation

---

# End of File
