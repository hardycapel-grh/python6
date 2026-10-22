# Works Orders

## Purpose
A **Works Order (WO)** represents the manufacturing or assembly work required to fulfil a Sales Order.  
Every WO belongs to exactly one Sales Order and contains the specific BOM items allocated to it.

Works Orders allow you to:

- Allocate BOM items from the Sales Order  
- Track production progress  
- Ensure all required items are accounted for  
- Complete manufacturing before the Sales Order can be finished  

---

## How Works Orders Are Created

### Automatic Creation
When a Sales Order is **released**, you may attach one or more Works Orders.

### Manual Creation
Click **Attach Works Order** inside the Sales Order editor.

This creates a new WO with:

- A unique **WO Number**  
- The same **SO Number**  
- The same **Customer**  
- An empty item list  
- Status: **new**  
- Type: same as the Sales Order (usually *firm*)  
- Created by: the current user  

---

## Allocating Items to a Works Order

After creating a WO, the system prompts you to allocate BOM items.

### Allocation Rules
- You may allocate **any unallocated BOM items** from the Sales Order.  
- Items already allocated to other WOs are excluded.  
- You may allocate multiple items at once using the **BOM Multi‑Select** dialog.

### Allocation Workflow
1. Click **Attach Works Order**  
2. The BOM selection dialog appears  
3. Tick the items to allocate  
4. Confirm  
5. The WO now contains those items  

You may create multiple WOs until all BOM items are allocated.

---

## Works Order Status Pipeline

Works Orders follow a simple status progression:

| Status      | Meaning |
|-------------|---------|
| **new**     | WO created, items allocated, not yet in production |
| **in-work** | WO is actively being worked on |
| **completed** | All work finished; WO ready for SO finishing |

### How Status Changes Occur

- **new → in-work**  
  Triggered when the Sales Order moves to *in-work* and all BOM items are allocated.

- **in-work → completed**  
  Set manually or by your production workflow (outside this dialog).

A Sales Order **cannot** be finished until **all** its Works Orders are **completed**.

---

## Viewing Attached Works Orders

Inside the Sales Order editor, the **Works Orders** list shows:

- WO Number  
- WO Status  

Example:


This list updates automatically whenever WOs are created or modified.

---

## Rules for Moving the Sales Order to In‑Work

The **Move to In‑Work** button becomes available only when:

1. The Sales Order is **released**  
2. **All BOM items** have been allocated to Works Orders  
3. At least **one WO** exists  

If any BOM items are unallocated, the button remains hidden.

---

## Rules for Finishing the Sales Order

A Sales Order can only be finished when:

1. All Works Orders are **completed**  
2. The BOM of the firm order **matches** the BOM of the linked enquiry  
   - Same part numbers  
   - Same quantities  
   - No missing items  
   - No extra items  

If any mismatch exists, finishing is blocked and the system prompts you to resolve it.

---

## BOM Matching (Firm vs Enquiry)

When finishing a firm Sales Order linked to an enquiry:

### The following must match:

- **Part numbers**  
- **Quantities**  

### The system checks for:

- Missing items  
- Extra items  
- Quantity mismatches  

If mismatches exist:

- A detailed message is shown  
- The **Pick** button becomes enabled  
- You may re‑pick a different enquiry  
- The Sales Order cannot be finished until the mismatch is resolved  

---

## Buttons & Actions

### **Attach Works Order**
Creates a new WO and prompts allocation of BOM items.

### **Move to In‑Work**
Moves the Sales Order to *in-work* if all BOM items are allocated.

### **Finish Order**
Finishes the Sales Order only if:
- All WOs are completed  
- BOM matches the linked enquiry  

### **Pick (Enquiry Link)**
Normally disabled.  
Enabled only when BOM mismatch occurs during finishing.

Allows re‑selecting the enquiry.

---

# Crib — Works Orders
 -Overview
- - When a Sales Order is created an initial Works Order is also created. This is mainly used for time bookings that fall outside of any other booking method.
- - Other Works Orders are created from the Sales Order editor using **Attach Works Order**. All Works Orders are of the same type (Firm or Enquiry) as the parent Sales Order. When a Works Order is created the Sales order BOM items can be attached either all to one or shared between more than one Works Order. Unallocated items cannot be left behind.
- - A Sales Order cannot move to **In‑Work** until **all BOM items** are allocated.  
- - A Sales Order cannot be **Finished** until **all Works Orders are completed**.  
- - Firm Sales Orders linked to an enquiry must have **matching BOMs** (items + quantities).  
- - If BOM mismatch occurs, the **Pick** button becomes enabled so you can re‑select the enquiry.  
- - Works Orders track production progress and ensure all required work is completed before finishing.

- Enquiry type Works Orders
- - Clicking Works Orders from the left pane opens the Works Orders selector. There are filters at the top of the selector that narrow the choice for selection.
- - Double click the required enquiry type Works Order to open the Works Order editor.
- - The editor is divided in to 4 panes. The top pane shows the Works Orders details. The bottom pane allows the user to add Works Order notes. The third pane summarises the estimated costs. The second pane is where we create the estimate.
- - Click 'Release' to release the Works Order so the estimate can be built. The estimate can built directly in to the estimate pane. Also, click 'Edit Breakdown' to build an estimate for each individual item.
- - Click 'Approve Estimate' once the estimate is complete.
- - Click 'Finish' to complete the works order.


---

# End of File
