"""
Invoice generation logic.

Creates an invoice document for a finished Sales Order.
"""

from datetime import datetime
from typing import Dict, Any


def _get_next_invoice_number(mongo) -> int:
    """
    Simple auto-increment invoice number based on existing documents.
    If no invoices exist, start at 1.
    """
    last = mongo.invoices.find_one(
        {},
        sort=[("invoice_number", -1)]
    )
    if last and "invoice_number" in last:
        return int(last["invoice_number"]) + 1
    return 1


def generate_invoice(mongo, so_number: int, cost_data: Dict[str, Any]) -> int:
    """
    Generate an invoice for the given Sales Order.

    mongo: your mongo wrapper (with .sales_orders, .invoices, etc.)
    so_number: Sales Order number
    cost_data: dict returned by calculate_sales_order_cost()

    Returns the new invoice_number (int).
    """

    so = mongo.sales_orders.find_one({"so_number": so_number})
    if not so:
        raise ValueError(f"Sales Order {so_number} not found")

    invoice_number = _get_next_invoice_number(mongo)

    invoice_doc = {
        "invoice_number": invoice_number,
        "so_number": so_number,
        "customer": so.get("customer"),
        "req_date": so.get("req_date"),
        "created_at": datetime.utcnow(),
        "status": "draft",  # or "issued" if you prefer
        "lines": [],        # you can expand this later
        "costs": cost_data,
        "selling_price": float(so.get("selling_price", 0.0)),
    }

    # Basic single-line invoice for now: whole SO as one line
    invoice_doc["lines"].append({
        "description": f"Sales Order {so_number}",
        "amount": float(so.get("selling_price", cost_data.get("total_cost", 0.0))),
    })

    mongo.invoices.insert_one(invoice_doc)

    return invoice_number
