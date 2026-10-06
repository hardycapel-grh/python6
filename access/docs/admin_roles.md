# Admin: Roles

## Purpose
The **Roles** page allows administrators to define and manage roles within the system.  
Roles act as permission groups, making it easier to assign consistent access levels to multiple users.

Instead of giving each user dozens of individual permissions, roles let you bundle permissions together and apply them in one step.

---

## What You Can Do Here

### Create New Roles
Add new roles to support different job functions or access levels, such as:

- Warehouse Staff  
- Sales Team  
- Managers  
- Administrators  

### Edit Existing Roles
Modify role names or adjust the permissions assigned to them.

### Assign Permissions to Roles
Roles determine what users assigned to them can do.  
You can add or remove permissions to tailor each role’s capabilities.

### Review Role Permissions
See exactly which permissions a role grants.  
This helps ensure users receive the correct level of access.

### Delete Roles
Remove roles that are no longer needed.  
(Only possible if no users are currently assigned to the role.)

---

## Key Fields

### Role Name
A descriptive name for the role, such as “Admin” or “Editor”.

### Permissions
A list of all permissions assigned to the role.  
These may include:

- Sales Order editing  
- Works Order access  
- Inventory management  
- Admin module access  
- Log viewing  

### Assigned Users
Shows which users currently belong to the role.  
This helps you understand the impact of changes.

---

## Permissions Required
To access the Roles page, you typically need:

- `roles.manage`  
- or a broader admin permission such as `admin.access`

If you cannot see this page, your role may not include role‑management capabilities.

---

## Workflow Context
Roles are part of the Admin module and sit outside the main operational workflow.  
They support the workflow by ensuring:

- Users have the correct access  
- Permissions are grouped logically  
- Security is maintained  
- Administrative changes are easy to manage  

Changes made here affect all users assigned to the role.

---

## Notes & Tips

- Be careful when removing permissions — it affects every user assigned to the role.  
- Use roles to keep permission management simple and consistent.  
- If a user reports missing features, check their role’s permissions first.  
- Avoid creating too many roles; keep them clear and purposeful.  
- Review assigned users before making major changes.

---

## Crib

- Click 'Add Role' to add a role, enter a name and description and select permissions for that role.
- Select a role and click 'Edit Role' to edit to edit a roles description and change the roles permissions.
- Click 'Delete Role' to delete the role. 

---

# End of File
