# Admin: UOMs

## Purpose
The **UOMs (Units of Measure)** page allows administrators to define and manage the units of measure used throughout the system.  
UOMs ensure that quantities, stock levels, and BOM components are recorded consistently and accurately.

Common examples include:

- Each  
- Box  
- Pack  
- Kilogram  
- Metre  

Correct UOM configuration is essential for inventory, purchasing, and manufacturing workflows.

---

## What You Can Do Here

### Create New UOMs
Add new units of measure to support operational or inventory needs.

### Edit Existing UOMs
Modify UOM names or descriptions to keep information accurate.

### Standardise Measurement Types
Ensure that similar items use consistent units (e.g., all weights in kilograms).

### Remove Unused UOMs
Delete UOMs that are no longer required.  
(Only possible if they are not referenced by items or BOMs.)

---

## Key Fields

### UOM Name
A short, descriptive name for the unit, such as:

- Each  
- Box  
- Kg  
- Litre  
- Metre  

### Description
Optional additional information about how the UOM is used.

### Category (if applicable)
Some systems group UOMs by type, such as:

- Weight  
- Length  
- Volume  
- Count  

This helps maintain consistency across items.

---

## Permissions Required
To access the UOMs page, you typically need:

- `uoms.manage`  
- or a broader admin permission such as `admin.access`

If you cannot see this page, your role may not include UOM‑management capabilities.

---

## Workflow Context
UOMs are part of the Admin module and sit outside the main operational workflow.  
They support the workflow by ensuring:

- Items have correct measurement units  
- BOMs use consistent quantities  
- Inventory counts are accurate  
- Purchasing and stock movements remain clear  

Incorrect UOM configuration can lead to confusion, inaccurate stock levels, or BOM errors.

---

## Notes & Tips

- Keep UOM names short and standardised.  
- Avoid creating duplicate UOMs (e.g., “Kg” and “Kilogram”).  
- Review UOM usage before deleting one.  
- Ensure BOM components use the correct UOM to avoid production mistakes.  
- Use descriptions to clarify special or uncommon units.

---

##

- Click Add to create a new Unit of Measure. Enter a UOM name (e.g., Each, Box, Kg).
- Select a UOM and click Edit to change the description and units.
- Select a UOM and click Delete to remove it. A UOM can only be deleted if it is not used by any items or BOMs.

---

# End of File
