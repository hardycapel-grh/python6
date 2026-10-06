# Admin: Store Locations

## Purpose
The **Store Locations** page allows administrators to define and manage the internal locations within each store.  
Store locations represent specific areas where inventory is kept, such as:

- Aisles  
- Racks  
- Bins  
- Shelves  
- Zones  

These locations help organise inventory and ensure accurate stock tracking throughout the system.

---

## What You Can Do Here

### Create New Store Locations
Add new locations inside a store to support detailed inventory organisation.

### Edit Existing Locations
Modify location names or descriptions to keep information accurate.

### Assign Locations to Stores
Each location belongs to a specific store.  
This ensures inventory movements and stock counts are correctly mapped.

### Enable or Disable Locations
Locations can be activated or deactivated depending on operational needs.

### Remove Unused Locations
Delete locations that are no longer required.  
(Only possible if they are not referenced by inventory items.)

---

## Key Fields

### Location Name
A descriptive name for the location, such as:

- Aisle 1  
- Rack B  
- Bin 12  
- Shelf 4  

### Store
The store that this location belongs to.  
Locations cannot exist without a parent store.

### Description
Optional additional information about the location’s purpose or contents.

### Status
Indicates whether the location is active.  
Inactive locations cannot be used in inventory workflows.

---

## Permissions Required
To access the Store Locations page, you typically need:

- `store_locations.manage`  
- or a broader admin permission such as `admin.access`

If you cannot see this page, your role may not include location‑management capabilities.

---

## Workflow Context
Store Locations are part of the Admin module and sit outside the main operational workflow.  
They support the workflow by ensuring:

- Inventory is organised at a granular level  
- Stock movements are accurately tracked  
- Items are stored in meaningful, searchable locations  
- Operational processes have reliable location data  

Incorrect location configuration can lead to misplaced stock or workflow delays.

---

## Notes & Tips

- Keep location names clear and consistent across stores.  
- Avoid overly complex naming schemes — simplicity helps users find items quickly.  
- Disable locations instead of deleting them if they may be needed later.  
- Ensure each store has a logical structure of locations before adding inventory.  
- Review location usage periodically to maintain accurate inventory organisation.

---

##

- Click Add to create a new store location. Enter a location name and description.
- Select a store location and click Edit to change its name and description.
- Select a store location and click Delete to remove it. A store location can only be deleted if it is not referenced by any inventory items.
- Select a store location and click Activate/Deactivate to switch between Active and Inactive.

---

# End of File
