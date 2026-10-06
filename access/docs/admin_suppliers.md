# Admin: Suppliers

## Purpose
The **Suppliers** page allows administrators to create, manage, and maintain supplier records used throughout the system.  
Suppliers are essential for purchasing, inventory replenishment, and BOM sourcing.  
Accurate supplier data ensures smooth procurement workflows and reliable stock management.

---

## What You Can Do Here

### Create New Suppliers
Add new supplier records with details such as:

- Supplier name  
- Contact information  
- Address  
- Reference codes  
- Notes or special instructions  

### Edit Existing Suppliers
Update supplier details to keep information accurate and current.

### Manage Supplier Status
Enable or disable suppliers depending on whether they are actively used.

### Link Suppliers to Items (if applicable)
Some systems allow items to reference preferred or approved suppliers.

### Remove Unused Suppliers
Delete suppliers that are no longer required.  
(Only possible if they are not referenced by items or purchase records.)

---

## Key Fields

### Supplier Name
The official name of the supplier or company.

### Contact Details
Information such as:

- Phone number  
- Email address  
- Website  
- Contact person  

### Address
The supplier’s physical or mailing address.

### Reference Code
An optional internal code used for quick identification or integration.

### Notes
Additional information such as:

- Lead times  
- Delivery instructions  
- Payment terms  
- Special conditions  

### Status
Indicates whether the supplier is active.  
Inactive suppliers cannot be used in purchasing workflows.

---

## Permissions Required
To access the Suppliers page, you typically need:

- `suppliers.manage`  
- or a broader admin permission such as `admin.access`

If you cannot see this page, your role may not include supplier‑management capabilities.

---

## Workflow Context
Suppliers are part of the Admin module and sit outside the main operational workflow.  
They support the workflow by ensuring:

- Purchasing processes have accurate supplier data  
- Inventory replenishment is reliable  
- BOM components can reference correct suppliers  
- Procurement decisions are well‑informed  

Incorrect supplier configuration can lead to ordering mistakes or delays.

---

## Notes & Tips

- Keep supplier contact details up‑to‑date to avoid communication issues.  
- Use reference codes for quick lookup in purchasing workflows.  
- Disable suppliers instead of deleting them if they may be needed later.  
- Record lead times and payment terms to help purchasing staff.  
- Review supplier usage before removing a supplier.

---

## Crib
- Click Add to create a new supplier. Enter the supplier name, contact details, address, and any notes or reference codes.
- Select a supplier and click Edit to update its details.
- Select a supplier and click Delete to remove it. A supplier can only be deleted if it is not referenced by any items or purchasing records.
- Select a supplier and click View to view its details.

# End of File
