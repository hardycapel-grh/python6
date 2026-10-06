# Admin Module

## Purpose
The **Admin** module provides tools for managing the core configuration of the system, including users, roles, permissions, stores, units of measure, suppliers, and audit logs.  
It is designed for administrators who maintain system structure, security, and operational data.

The Admin module contains several sub‑pages, each with its own purpose and workflow.

---

## What You Can Do Here
Administrators can:

- Create and manage user accounts  
- Assign roles and permissions  
- Configure stores and store locations  
- Define units of measure (UOMs)  
- Manage suppliers  
- Review audit logs  
- Access BOM (Bill of Materials) editing tools  

Each sub‑page in the Admin module has its own dedicated help topic.

---

## Sub‑Pages in the Admin Module

### **Users**
Manage user accounts, usernames, roles, and permissions.

### **Roles**
Define roles that group permissions together for easier assignment.

### **Stores**
Configure physical or logical stores used for inventory management.

### **UOMs**
Define units of measure used throughout the system (e.g., Each, Box, Kg).

### **Store Locations**
Create and manage locations within stores (e.g., Aisle 1, Rack 3).

### **Permissions**
View and manage all available permissions in the system.

### **Audit Log**
Review detailed records of user actions and system events.

### **Suppliers**
Manage supplier records used in purchasing and inventory workflows.

### **BOM Editor**
Create and edit Bills of Materials for items and assemblies.

---

## Permissions Required
Access to the Admin module typically requires elevated permissions such as:

- `admin.access`  
- `admin.manage`  
- Or specific permissions for each sub‑page (e.g., `users.manage`, `roles.manage`)

If you cannot see the Admin module in the sidebar, you may not have the required permissions.

---

## Workflow Context
The Admin module sits outside the main operational workflow  
*(Sales Orders → Works Orders → Breakdown → Finish)*.

Its purpose is to:

- Configure system behaviour  
- Maintain security and access control  
- Manage supporting data structures  
- Provide tools for administrators and power users  

Changes made here affect how the rest of the system operates.

---

## Notes & Tips
- Be cautious when modifying roles or permissions — changes affect all users assigned to them.  
- Use the Audit Log to verify administrative actions.  
- Keep store and location data organised to avoid inventory confusion.  
- Ensure UOMs are correct before creating items or BOMs.  
- Supplier data should be kept up‑to‑date for purchasing workflows.  

---

# End of File
