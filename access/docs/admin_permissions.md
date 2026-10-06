# Admin: Permissions

## Purpose
The **Permissions** page allows administrators to view, manage, and organise all permissions available within the system.  
Permissions define what actions users can perform, and they form the foundation of the system’s security model.

Roles are built from permissions, and users inherit permissions from their roles — with optional overrides.  
This page provides a complete overview of every permission in the system.

---

## What You Can Do Here

### View All Permissions
See a full list of every permission the system supports, including:

- Sales Order permissions  
- Works Order permissions  
- Inventory permissions  
- Admin permissions  
- Log viewer permissions  
- BOM editor permissions  

### Edit Permission Details (if applicable)
Some systems allow editing descriptions or categories for clarity.

### Organise Permissions
Permissions may be grouped into categories such as:

- Sales  
- Works Orders  
- Inventory  
- Admin  
- Logs  
- BOM  

This helps administrators understand how permissions relate to system features.

### Assign Permissions to Roles
Although roles are managed in *Admin: Roles*, this page helps you understand which permissions belong to which roles.

### Review Permission Usage
See which roles or users currently rely on a specific permission.

---

## Key Fields

### Permission Name
The internal name of the permission, such as:

- `sales.read`  
- `sales.edit`  
- `works.read`  
- `admin.access`  
- `logs.read`  

### Description
A human‑readable explanation of what the permission allows.

### Category
Groups permissions into logical sections for easier navigation.

### Assigned Roles
Shows which roles include this permission.

### Assigned Users (if applicable)
Some systems allow direct user‑level permission assignment.  
This field shows which users have the permission individually.

---

## Permissions Required
To access the Permissions page, you typically need:

- `permissions.manage`  
- or a broader admin permission such as `admin.access`

If you cannot see this page, your role may not include permission‑management capabilities.

---

## Workflow Context
Permissions are part of the Admin module and sit outside the main operational workflow.  
They support the workflow by ensuring:

- Users have correct access  
- Roles are built consistently  
- Security is maintained  
- Administrative changes are predictable and traceable  

Incorrect permission configuration can lead to missing features, disabled buttons, or unintended access.

---

## Notes & Tips

- Avoid giving users direct permissions unless absolutely necessary — roles are easier to maintain.  
- Keep permission descriptions clear to help future administrators.  
- Review permission usage before removing or renaming a permission.  
- If a user reports missing functionality, check both their role and any direct permissions.  
- Use categories to keep permissions organised and easy to navigate.

---

## Crib

-Click Add to create a new permission. Enter a permission name and a description and category.
-Select a permission and click Edit to change its name, description, or category.
-Select a permission and click Delete to remove it. A permission can only be deleted if it is not assigned to any roles or users.

# End of File
