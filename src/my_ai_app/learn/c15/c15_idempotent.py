import hashlib
from datetime import date

ORDERS = {}  # idempotency key -> order id (in KitchenOS: a table with a UNIQUE key column)


def create_purchase_order(item, kg):
    key = hashlib.sha256(f"{item.lower()}|{kg}|{date.today()}".encode()).hexdigest()
    if key in ORDERS:
        return f"already placed today: {ORDERS[key]} (not ordered again)"
    order_id = f"PO-{len(ORDERS) + 1}"
    ORDERS[key] = order_id
    return f"placed {order_id}: {kg} kg {item}"


print(create_purchase_order("onion", 10))
print(create_purchase_order("onion", 10))   # a retry or a duplicate call
print(create_purchase_order("Onion", 10))   # the same order, different capital letter
print(create_purchase_order("onion", 15))   # a genuinely different order