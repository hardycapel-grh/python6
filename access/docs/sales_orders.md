# Sales Orders

## Purpose
The **Sales Orders** page allows you to create, edit, manage, and track customer sales orders.  
Sales Orders form the starting point for production: each Sales Order automatically generates a Works Order, ensuring the job enters the Workbench immediately.

Accurate Sales Orders ensure correct scheduling, costing, and workflow visibility.

---

## What You Can Do Here

### Add a New Sales Order
Click **Add Sales Order** to create a new order.

You can enter:

- **SO Number** – auto‑generated (or manually entered if required)
- **Customer** – selected from the customer list
- **Required Date**
- **Items** – list of parts being ordered
- **Type** – *Firm* or *Enquiry*
- **Status** – defaults to *new*

When saved:

- The Sales Order is created
- A **Works Order** is automatically generated and added to the Workbench

---

### Edit an Existing Sales Order
Select an order and click **Edit Sales Order**.

You can update:

- Customer  
- Required date  
- Items  
- Status  
- Type  
- Any additional fields supported by the editor

Editing a Sales Order also updates the linked Works Order where appropriate.

---

### Hold / Unhold a Sales Order
Select an order and click **Hold / Unhold**.

- When holding, you must enter a **hold reason**
- Held orders appear as *Held* in the Workbench
- Unholding clears the hold reason

Holding prevents further processing until released.

---

### Cancel / Uncancel a Sales Order
Select an order and click **Cancel**.

- You must enter a **cancellation reason**
- Cancelled orders are removed from active workflow
- Uncancelling restores the order to *new* status

---

### Clone a Sales Order
Select an order and click **Clone**.

Cloning creates:

- A new Sales Order with identical details
- A new Works Order linked to the cloned SO

Useful for repeat jobs or re‑orders.

---

## Key Fields

### SO Number
Unique identifier for the Sales Order.  
Generated automatically using the next available number.

### Customer
The customer placing the order.  
Populated from the customer list.

### Required Date
The date the customer needs the order completed.

### Items
List of parts or assemblies being ordered.

### Status
Workflow state of the order:

- **new**
- **released**
- **in‑work**
- **finished**
- **cancelled**

### Type
Defines the nature of the order:

- **Firm** – confirmed order  
- **Enquiry** – provisional or quotation stage

### Held
Indicates whether the order is on hold.  
Held orders require a reason.

---

## Workflow Context

Sales Orders feed directly into:

- **Works Orders** (auto‑generated)
- **Workbench** (SO + WO visibility)
- **Production scheduling**
- **Costing**
- **Inventory planning**

Changes to a Sales Order immediately affect downstream workflow.

---

## Notes & Tips

- Use **Hold** for temporary stops rather than cancelling.
- Cloning is ideal for repeat jobs or template orders.
- Ensure customer and item details are correct before releasing.
- Cancelled orders are removed from active workflow but remain in history.
- Works Orders are always created automatically — no manual step required.

---

# Crib — Sales Orders
- Click **Sales Order List** this load the Sales Order list page.
- Use the filters to reduce the lists contents.
- Click **Add Sales Order** to create a new order. The Add Sales Order Dialog loads.   
- - Select customer from the drop down.
- - Select required date from the date picker.
- - Choose between 'enquiry' and 'firm' types. Enquiry type is essentially the estimate supplied to the customer. Firm type is the actual requirement to fulfil a customers order. Note a firm type will need to link to it's equivalent enquiry.
- - Click in the "Search inventory" box and start typing and then select the items that make up the sales orders inventory. Be sure to enter the the quantity (be aware of the Unit Of Measure (UOM)). Click 'Add Selected item' to add the item. To remove the item, highlight it and click 'Remove Item'.
- - Click 'OK' to complete the new sales order.
- Select a Sales Order and Click **Clone** to make an exact copy which can be edited.
- Select a Sales Order and Click **Edit Sales Order** to edit an Order. 
- - Enquiry type Sales Order.
- - - A 'new' Sales Order is simply that. It is new waiting action. It will have one 'Works Order' attached. This WO is simply for any time bookings required that fall outside any normal processing.
- - - Click **Release** to release the Sales Order for further work.


---

# End of File
