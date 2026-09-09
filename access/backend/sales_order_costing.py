"""
Sales Order costing logic.

Calculates material, labour, overhead and total cost for a given Sales Order
based on its linked Works Orders.
"""

from typing import Dict, Any


def calculate_sales_order_cost(mongo, so_number: int) -> Dict[str, Any]:
    """
    Calculate cost breakdown for a Sales Order.

    mongo: your existing mongo wrapper (with .works_orders, .sales_orders, etc.)
    so_number: Sales Order number (int or str)

    Returns a dict like:
    {
        "material_cost": float,
        "labour_cost": float,
        "overhead_cost": float,
        "total_cost": float,
        "profit": float,          # optional, can be 0.0 if not known
    }
    """

    # Fetch all WOs for this SO
    wos = list(mongo.works_orders.find({"so_number": so_number}))

    material_cost = 0.0
    labour_cost = 0.0
    overhead_cost = 0.0

    for wo in wos:
        # Material cost: sum item["unit_cost"] * item["qty"] if present
        for item in wo.get("items", []):
            unit_cost = float(item.get("unit_cost", 0.0))
            qty = float(item.get("qty", 0.0))
            material_cost += unit_cost * qty

        # Labour cost: assume stored per WO
        labour_cost += float(wo.get("labour_cost", 0.0))

        # Overhead: assume stored per WO or as percentage of labour
        overhead_cost += float(wo.get("overhead_cost", 0.0))

    total_cost = material_cost + labour_cost + overhead_cost

    # Profit: if SO has a selling_price, we can derive profit
    so = mongo.sales_orders.find_one({"so_number": so_number}) or {}
    selling_price = float(so.get("selling_price", 0.0))
    profit = selling_price - total_cost if selling_price else 0.0

    return {
        "material_cost": round(material_cost, 2),
        "labour_cost": round(labour_cost, 2),
        "overhead_cost": round(overhead_cost, 2),
        "total_cost": round(total_cost, 2),
        "profit": round(profit, 2),
    }
