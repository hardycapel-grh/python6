# backend/wo_costing.py

def calculate_enquiry_wo_cost(mongo, wo_number):
    """
    Calculate estimated cost for an enquiry-type Works Order.
    This uses the estimate fields stored in the WO document.
    """

    wo = mongo.works_orders.find_one({"wo_number": wo_number})
    if not wo:
        return {
            "labour_cost": 0,
            "material_cost": 0,
            "subcontract_cost": 0,
            "overhead_cost": 0,
            "total_estimated_cost": 0
        }

    labour_hours = float(wo.get("labour_hours", 0))
    labour_rate = float(wo.get("labour_rate", 0))
    material_cost = float(wo.get("material_cost", 0))
    subcontract_cost = float(wo.get("subcontract_cost", 0))
    overhead_cost = float(wo.get("overhead_cost", 0))

    labour_cost = labour_hours * labour_rate

    total = labour_cost + material_cost + subcontract_cost + overhead_cost

    return {
        "labour_cost": labour_cost,
        "material_cost": material_cost,
        "subcontract_cost": subcontract_cost,
        "overhead_cost": overhead_cost,
        "total_estimated_cost": total
    }
