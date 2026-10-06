# Admin: Users

## Purpose
The **Users** page allows administrators to create, manage, and maintain user accounts within the system.  
This includes assigning roles, configuring permissions, and controlling access to different parts of the application.

User management is central to system security and workflow control.

---

## What You Can Do Here

### Create New Users
Add new user accounts with:

- Username  
- Full name  
- Assigned role  
- Initial permissions (if applicable)

### Edit Existing Users
Modify user details such as:

- Display name  
- Role  
- Permissions  
- Account status (active/inactive)

### Assign Roles
Roles determine what a user can do.  
Changing a user’s role immediately affects their access across the system.

### Manage Permissions
Grant or revoke specific permissions for fine‑grained control.  
Useful when a user needs access beyond their role defaults.

### Deactivate Users
Disable accounts that should no longer have access without deleting their history.

---

## Key Fields

### Username
The unique login identifier for the user.

### Full Name
The user’s display name, shown throughout the system.

### Role
Defines the user’s general access level.  
Examples include:

- User  
- Editor  
- Admin  
- Manager  

### Permissions
A list of all permissions assigned to the user, including:

- Sales Order access  
- Works Order access  
- Inventory access  
- Admin access  
- Log viewing  

### Status
Indicates whether the account is active or disabled.

---

## Permissions Required
To access the Users page, you typically need:

- `users.manage`  
- or a broader admin permission such as `admin.access`

If you cannot see this page, your role may not include user‑management capabilities.

---

## Workflow Context
The Users page is part of the Admin module and sits outside the main operational workflow.  
It supports the workflow by ensuring:

- The right people have the right access  
- Permissions are correctly assigned  
- Roles are properly configured  
- Security is maintained across the system  

Changes made here affect how users interact with every other page.

---

## Notes & Tips

- Changing a user’s role can significantly alter their access — review carefully.  
- Use permissions to fine‑tune access beyond role defaults.  
- Deactivating a user preserves their audit history.  
- Always verify that new users have the correct permissions before they begin work.  
- If a user reports missing buttons or disabled fields, check their permissions here.

---

## Crib

- Click 'Refresh' to update the table.
- Click 'Add User' to create a new user. Enter details in the 'Add User' dialog.
- Highlight a user in the table and click 'Edit User' (or double click the user) to edit user details including permissions.
- Click 'Delete' to delete a user.
- Click 'Enable / Disable' to swap a users status.
- Use the search box to search for a user.
- Use the 'Roles' and 'Status' drop downs to filter the users table.

---

# End of File
