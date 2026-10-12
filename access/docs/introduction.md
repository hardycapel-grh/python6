# Introduction

## Welcome to the System
This application is designed to help you manage operational workflows such as Sales Orders, Works Orders, Breakdowns, Inventory, and administrative tasks.  
The **Help** section provides clear, concise guidance for every major page in the system.

Use this introduction to understand the overall structure of the app and how the different modules fit together.

---

## What You Can Do Here
The system supports a range of activities depending on your role and permissions:

- Create and edit Sales Orders  
- Progress Works Orders through their lifecycle  
- Record breakdowns and complete repair workflows  
- Manage inventory and stock levels  
- Review audit logs and recent activity  
- Access administrative tools (if permitted)  
- View your profile and permissions  

Each page in the Help menu explains its purpose, fields, and actions in detail.

---

## How the Workflow Fits Together
The core operational workflow follows a simple, logical sequence:

1. **Sales Orders**  Sales Orders are customer instigated orders. There are two types of Sales Orders: 'Enquiry' and 'Firm'. When a customer makes an enquiry or places a firm order, they do so how they please. For example: imagine we make a toy push along trolley. The customer might order 100 trolleys and 20 spare wheels. This is probably not how we need it. So the work flow is now for us to create Works Orders from the Sales Orders. The works Orders will be how we need the breakdown.

2. **Works Orders** Works Orders are how the business organises it's work flow. Works orders are derived from Sales Orders and must, ultimately cover all the items on the Sales Order. A Works Order can be either an enquiry type or a firm type. This is inherited from the parent Sales Order. An enquiry type Works Order is used to create an estimate. A firm type Works Order is used to provision the items required to complete part or the Sales Order through a Shop Order.

3. **Shop Orders** Shop Orders are derived from firm type Works Orders. They are used to produce by manufacture or sub contracting manufacture and or purchase the required parts and resources to fulfil the works order. The Shop Order is for individual parts or an assembly. Where an assembled part is required then further shop orders are required to complete the assembly's parts. Any resources required by the sales order passed down to a works order will require a shop order so they can be provisioned. Resources that need purchasing will need a Purchase Order.

4. **Purchase Orders**  
   

This workflow is supported by additional modules such as Inventory, Permissions, and Logs.

---

## Understanding Permissions
Your role determines what you can see and do in the system.  
Permissions control access to:

- Editing or viewing orders  
- Administrative features  
- Log and audit tools  
- Inventory management  
- Settings and configuration  

If something appears disabled or unavailable, check your **My Profile** page to review your permissions.

---

## Help Page Structure
Each Help topic includes:

- **Purpose** — what the page is for  
- **Key Fields** — what the page displays  
- **Actions You Can Perform** — what you can do  
- **Permissions Required** — who can access it  
- **Workflow Context** — how it fits into the system  
- **Notes & Tips** — practical guidance  

This consistent structure makes it easy to learn each part of the system.

---

## Tips for New Users
- Start with **My Profile** to understand your permissions.  
- Use **Sales Orders** and **Works Orders** to follow the main workflow.  
- Check **Log Viewer** if something doesn’t behave as expected.  
- Use the Help menu anytime you need clarification.  
- Contact an administrator if you need additional permissions.

---

## About This Help System
All help topics are stored as Markdown files inside the `/docs` folder.  
They are displayed automatically when selected from the Help menu.

This makes the help system:

- Easy to update  
- Easy to expand  
- Easy to maintain  
- Fully integrated into the app  

---

# End of File
