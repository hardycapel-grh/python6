# Shop Orders

## Purpose

Shop Orders (ShOs) are used to manage and control manufacturing activity.

A Shop Order is created from a Firm Works Order and is associated with a specific BOM item.

A Shop Order represents a manufacturing package containing:

- Manufacturing quantity
- Shop Order BOM
- Shop Order Routing
- Time bookings
- Material issues
- Production status

Shop Orders are where manufacturing activity takes place.

---

# Relationship Structure

Shop Orders exist within the following hierarchy:

Sales Order
    ↓
Firm Works Order
    ↓
Shop Order

The parent Works Order is responsible for planning and allocation.

The Shop Order is responsible for production.

---

# Shop Order Creation

Shop Orders are created from a Firm Works Order.

To create a Shop Order:

1. Open the Firm Works Order.
2. Select a BOM item.
3. Click Create Shop Order.
4. Enter the quantity to manufacture.
5. Confirm.

A Shop Order is then created against the selected BOM item.

Multiple Shop Orders may be created against the same BOM item.

Example:

Widget Qty 10

ShO1001 Qty 4
ShO1002 Qty 6

---

# Shop Order Information

Each Shop Order contains:

- Shop Order Number
- Works Order Number
- Sales Order Number
- Customer
- Part Number
- Description
- Quantity
- Unit Of Measure
- Required Date
- Status
- BOM Revision

The required date is inherited from the parent Works Order.

---

# Shop Order Status Flow

New
 ↓
Released
 ↓
In Work
 ↓
Finished

---

## New

The Shop Order has been created but manufacturing preparation has not started.

Available actions:

- Release

Unavailable actions:

- Load Master BOM
- Edit BOM
- Load Master Rout
- Edit Rout
- Book Time
- Issue Materials
- Finish

---

## Released

The Shop Order is ready for production preparation.

Available actions:

- Load Master BOM
- Edit BOM
- Load Master Rout
- Edit Rout
- Set To In Work

At this stage the manufacturing package is assembled.

---

## In Work

Manufacturing activity is underway.

Available actions:

- Edit BOM
- Edit Rout
- Book Time
- Issue Materials
- Finish

---

## Finished

Manufacturing is complete.

At this stage:

- The Shop Order becomes read-only.
- No further production transactions should be recorded.
- Labour and material activity should be complete.

---

# Shop Order BOM

The Shop Order BOM is separate from the Master BOM.

A newly-created Shop Order contains:

No Shop Order BOM loaded.

The production planner may load the latest engineering BOM using:

Load Master BOM

Once loaded, the Shop Order owns its own BOM.

Changes to the Engineering BOM do not affect existing Shop Orders.

---

# BOM Revision Traceability

When a Master BOM is loaded:

- The BOM lines are copied into the Shop Order.
- The BOM Revision is recorded on the Shop Order.
- The Shop Order becomes independent of future engineering changes.

Example:

Part Number: XYZ345
BOM Revision: 13

This provides manufacturing traceability and ensures it is always possible to determine the BOM revision used during production.

---

# Editing the Shop Order BOM

The Shop Order BOM may be modified independently of Engineering.

Typical reasons include:

- Additional manufacturing consumables
- Material substitutions
- Production-specific additions
- Planning corrections
- Temporary shop floor changes

Editing a Shop Order BOM does not modify the Master BOM.

---

# Adding Components

Components may be added directly within the Shop Order BOM editor.

To add a component:

1. Open the Shop Order.
2. Click Edit BOM.
3. Click Add Component.
4. Select the required component.
5. Enter quantity information.
6. Save the Shop Order BOM.

---

# Removing Components

Components may be removed from the Shop Order BOM.

To remove a component:

1. Open Edit BOM.
2. Locate the component row.
3. Click Remove.
4. Save the Shop Order BOM.

---

# Shop Order BOM vs Master BOM

## Master BOM

Purpose:

- Engineering definition

Owner:

- Engineering

Revision Controlled:

- Yes

Changes Affect Existing Shop Orders:

- No

---

## Shop Order BOM

Purpose:

- Manufacturing definition

Owner:

- Production

Revision Controlled:

- No

Changes Affect Master BOM:

- No

---

# Shop Order Routing

Shop Order Routing defines the operations required to manufacture the item.

Examples:

- Cutting
- Turning
- Milling
- Folding
- Welding
- Assembly
- Inspection
- Test

Routing functionality is under development.

The Shop Order Rout will be independent of the Master Rout.

---

# Required Dates

Shop Orders inherit their required date from the parent Works Order.

Hierarchy:

Sales Order
    ↓
Works Order
    ↓
Shop Order

This ensures scheduling consistency throughout manufacturing.

---

# Notes

Notes may be added throughout the life of the Shop Order.

Notes are stored directly against the Shop Order and form part of the production record.

---

# Future Functionality

Planned functionality includes:

- Routing management
- Rout revision tracking
- Time booking
- Material issue
- Material shortages
- Labour collection
- Production progress tracking
- Work centre allocation
- Manufacturing traceability
- Shop floor reporting

---

# Completion Rules

## Move To In Work

A Shop Order should only move to In Work when:

- The Shop Order BOM has been loaded.
- The Shop Order Routing has been loaded.
- Production preparation is complete.

---

## Finish Shop Order

A Shop Order should only be finished when:

- All manufacturing operations are complete.
- Labour bookings have been entered.
- Material issues have been recorded.
- Any shortages have been resolved.

---

# Crib – Shop Orders

- Shop Orders are created from Firm Works Orders.
- A Shop Order belongs to a specific BOM item.
- Multiple Shop Orders may be created against the same BOM item.
- Shop Orders inherit the required date from the parent Works Order.
- Shop Orders are where manufacturing activity takes place.
- Release the Shop Order before loading production data.
- Load Master BOM copies the latest Engineering BOM into the Shop Order.
- The Shop Order BOM becomes independent of the Master BOM.
- Editing a Shop Order BOM does not affect Engineering data.
- BOM revisions are stored on the Shop Order for traceability.
- Shop Order BOM changes affect only that Shop Order.
- Shop Order Routing will be maintained separately from the Master Rout.
- Time bookings will be recorded against Shop Orders.
- Material issues will be recorded against Shop Orders.
- Manufacturing progress will be tracked at Shop Order level.
- A Finished Shop Order becomes read-only.
- Firm Works Orders cannot be completed until all linked Shop Orders are finished.
- Shop Orders form the core production record for manufactured items.
- - Double click the required Shop Order to load it into the editor.
- - Click 'Release' to release the shop order for editing.
- - Click 'Load BOM' to load the shop order BOM with the latest revision of that parts BOM.
- - Click 'Edit BOM' to edit the shop order BOM.
- - - In the Shop order BOM editor you can add remove and modify BOM items.

# End of File