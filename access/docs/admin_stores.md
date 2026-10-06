# Admin: Stores

## Purpose
The **Stores** page allows administrators to define and manage the stores used throughout the system.  
A store represents a physical or logical location where inventory is held, such as:

- Warehouses  
- Workshops  
- Stock rooms  
- External storage locations  

Stores form the foundation of the inventory system, and many workflows depend on them being correctly configured.

---

## What You Can Do Here

### Create New Stores
Add new stores to support operational or inventory needs.  
Each store can represent a building, department, or external facility.

### Edit Existing Stores
Modify store names or descriptions to keep information accurate and up‑to‑date.

### Manage Store Activity
Enable or disable stores depending on whether they are currently in use.

### Link Store Locations
Stores contain **Store Locations**, which are managed separately.  
This page defines the parent store; locations are configured in *Admin: Store Locations*.

---

## Key Fields

### Store Name
A descriptive name for the store, such as:

- Main Warehouse  
- Workshop  
- External Storage  
- Finished Goods  

### Description
Optional additional information about the store’s purpose or contents.

### Status
Indicates whether the store is active.  
Inactive stores cannot be used in inventory workflows.

---

## Permissions Required
To access the Stores page, you typically need:

- `stores.manage`  
- or a broader admin permission such as `admin.access`

If you cannot see this page, your role may not include store‑management capabilities.

---

## Workflow Context
Stores are part of the Admin module and sit outside the main operational workflow.  
They support the workflow by ensuring:

- Inventory is organised  
- Stock movements are correctly tracked  
- Items are stored in meaningful locations  
- Operational processes have accurate storage information  

Incorrect store configuration can lead to inventory errors or workflow interruptions.

---

## Notes & Tips

- Keep store names clear and consistent to avoid confusion.  
- Disable stores that are no longer used rather than deleting them.  
- Ensure store locations are properly configured under *Admin: Store Locations*.  
- Review store usage periodically to maintain accurate inventory structure.

---

## Crib

- Click 'Add' to add a new store. Give the store a name, select 'active' or 'inactive' for the store status. Select 'Internal' for a general store that can be used by any customer, or 'Customer' for a customer specific store.
- Select a store and click 'Edit' to edit a store.
- Select a store and click 'Delete' to delete a store.

---

# End of File
