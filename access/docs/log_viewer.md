# Log Viewer

## Purpose
The **Log Viewer** provides a real‑time, searchable view of system log entries. It helps you understand what the system is doing, diagnose issues, and trace actions performed by users or background processes.

This page is primarily used for **monitoring**, **debugging**, and **auditing**.

---

## When to Use This Page
Use the Log Viewer when you need to:

- See what the system is doing right now  
- Diagnose unexpected behaviour  
- Check whether an operation succeeded or failed  
- Trace user actions  
- Review warnings or errors  
- Understand the sequence of events leading up to an issue  

---

## Key Fields

### Timestamp
The exact date and time the log entry was recorded.  
Useful for correlating events or identifying when an issue occurred.

### Level
The severity or type of log entry, such as:

- `debug` — low‑level system information  
- `info` — normal operational messages  
- `warn` — something unexpected but not fatal  
- `error` — a failure or problem requiring attention  

### Event
A short description of what happened.  
Examples include:

- User logged in  
- Works Order updated  
- Permission denied  
- Database write failure  

### Details
Additional structured information associated with the event.  
This may include:

- Usernames  
- IDs  
- Permissions  
- Data changes  
- Error messages  

---

## Actions You Can Perform

### Scroll Through Logs
Browse through all available log entries in chronological order.

### Search
Use the search box to filter log entries by:

- Username  
- Event type  
- Keywords  
- Error messages  
- IDs  

This helps you quickly locate relevant information.

### Filter by Level
Focus on specific log levels, such as:

- Only errors  
- Only warnings  
- Only info messages  

Useful when diagnosing issues.

### Inspect Details
Clicking or expanding a log entry (depending on your UI) shows additional structured data.

---

## Permissions Required
Access to the Log Viewer typically requires elevated permissions, such as:

- `logs.read`  
- `logs.admin`  

If you cannot see the Log Viewer in the sidebar, you may not have the required permission.

---

## Workflow Context
The Log Viewer is not part of the main operational workflow  
*(Sales Orders → Works Orders → Breakdown → Finish)*.

Instead, it supports the workflow by providing:

- Visibility into system behaviour  
- Diagnostics when something goes wrong  
- Confirmation that actions were logged correctly  
- Insight into user activity  

Administrators and developers use this page frequently during troubleshooting.

---

## Notes & Tips

- If something “didn’t save”, check the Log Viewer for errors.  
- Warnings often indicate misconfigurations or missing data.  
- Errors should be investigated immediately.  
- Use search to quickly find entries related to a specific user or order.  
- If logs appear empty, confirm that logging is enabled and that you have permission to view them.

---

# Crib

- Select filters (check boxes)
- Open folder button opens the log file folder location
- Use the Filter text box to enter a phrase to search for.

---

# End of File