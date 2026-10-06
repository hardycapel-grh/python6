# Admin: Audit Log

## Purpose
The **Audit Log** page provides a detailed record of actions performed throughout the system.  
It is designed for administrators who need to:

- Track user activity  
- Diagnose issues  
- Verify changes  
- Maintain accountability  
- Review security‑related events  

The Audit Log is an essential tool for understanding what happened, when it happened, and who performed the action.

---

## What You Can Do Here

### View System Events
Browse a chronological list of all recorded actions, including:

- User logins  
- Data changes  
- Permission updates  
- Role assignments  
- Inventory movements  
- Administrative actions  

### Filter Events
Use filters to narrow down the log by:

- User  
- Event type  
- Date range  
- Severity  
- Keywords  

This makes it easy to locate specific actions or investigate issues.

### Inspect Event Details
Each log entry contains structured data showing:

- Who performed the action  
- What was changed  
- Old and new values  
- Timestamps  
- Related IDs (e.g., order IDs, user IDs)  

### Trace Activity
Follow a sequence of events to understand how a change occurred or how an issue developed.

---

## Key Fields

### Timestamp
The exact date and time the event occurred.

### User
The user who performed the action.  
System‑generated events may show a special identifier.

### Event Type
A short description of the action, such as:

- User updated  
- Permission changed  
- Works Order modified  
- Inventory adjusted  

### Details
Structured information describing the event in depth.

### Severity (if applicable)
Some systems classify events as:

- Info  
- Warning  
- Error  

This helps highlight important or problematic actions.

---

## Permissions Required
To access the Audit Log page, you typically need:

- `audit.read`  
- or a broader admin permission such as `admin.access`

If you cannot see this page, your role may not include audit‑log access.

---

## Workflow Context
The Audit Log is part of the Admin module and sits outside the main operational workflow.  
It supports the workflow by providing:

- Visibility into user actions  
- A record of changes for troubleshooting  
- Accountability for administrative operations  
- Insight into system behaviour  

Audit logs are often used during investigations, debugging, or compliance checks.

---

## Notes & Tips

- Use filters to quickly locate relevant events.  
- Review audit entries when unexpected behaviour occurs.  
- Errors in the audit log often indicate deeper issues that need attention.  
- Audit logs cannot usually be edited — they are designed to be tamper‑proof.  
- If a user claims they “didn’t change anything”, the audit log can confirm what happened.

---

## Crib

- Use the filters to filter the log.

---

# End of File
