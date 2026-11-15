import json

STOCK = {"paneer": 2.5, "onion": 12}
SALES_TODAY = {"paneer tikka": 14}


def get_stock(item):
    return f"{STOCK.get(item.lower(), 0)} kg"


def get_sales(dish):
    return f"{SALES_TODAY.get(dish.lower(), 0)} plates sold today"


def create_purchase_order(item, kg):
    if not 0 < kg <= 50:
        return "ERROR: kg must be between 1 and 50"
    return f"order drafted: {kg} kg {item} (waiting for owner approval)"


TOOLS = {"get_stock": get_stock, "get_sales": get_sales, "create_purchase_order": create_purchase_order}

ALLOWED = {
    "owner": {"get_stock", "get_sales", "create_purchase_order"},
    "staff": {"get_stock"},
}


def run_tool(name, arguments, role):
    if name not in ALLOWED.get(role, set()):
        return f"ERROR: '{name}' is not allowed for role '{role}'"
    try:
        return TOOLS[name](**json.loads(arguments))
    except Exception as e:
        return f"ERROR: {name} failed: {e}"


print(run_tool("get_stock", '{"item": "paneer"}', "staff"))
print(run_tool("get_sales", '{"dish": "paneer tikka"}', "staff"))
print(run_tool("get_sales", '{"dish": "paneer tikka"}', "owner"))
print(run_tool("create_purchase_order", '{"item": "onion", "kg": 500}', "owner"))
print(run_tool("create_purchase_order", '{"item": "onion", "kg": 10}', "owner"))
print(run_tool("run_sql", '{"query": "DELETE FROM orders"}', "owner"))