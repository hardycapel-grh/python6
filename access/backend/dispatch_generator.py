"""
Dispatch note generation logic.

Creates a dispatch note / delivery note for a finished Sales Order.
"""

from datetime import datetime


def _get_next_dispatch_number(mongo) -> int:
    """
    Simple auto-increment dispatch number based on existing documents.
    If no dispatch notes exist, start at 1.
    """
    last = mongo.dispatch_notes.find_one(
        {},
        sort=[("dispatch_number", -1)]
    )
    if last and "dispatch_number" in last:
        return int(last["dispatch_number"]) + 1
    return 1


def generate_dispatch_note(mongo, so_number: int) -> int:
    """
    Generate a dispatch note for the given Sales Order.

    mongo: your mongo wrapper (with .sales_orders, .dispatch_notes, etc.)
    so_number: Sales Order number

    Returns the new dispatch_number (int).
    """

    so = mongo.sales_orders.find_one({"so_number": so_number})
    if not so:
        raise ValueError(f"Sales Order {so_number} not found")

    dispatch_number = _get_next_dispatch_number(mongo)

    dispatch_doc = {
        "dispatch_number": dispatch_number,
        "so_number": so_number,
        "customer": so.get("customer"),
        "req_date": so.get("req_date"),
        "created_at": datetime.utcnow(),
        "status": "open",
        "items": so.get("items", []),  # ship the SO items as-is for now
    }

    mongo.dispatch_notes.insert_one(dispatch_doc)

    return dispatch_number
