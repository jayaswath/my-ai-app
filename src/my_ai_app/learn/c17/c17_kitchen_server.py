import sys

from mcp.server.fastmcp import FastMCP

mcp = FastMCP("kitchen")                       # the server, with a name hosts will show

# ---------- fake kitchen data (stands in for KitchenOS tables) ----------
SALES = {
    "2026-10-23": {"Paneer Tikka": 0, "Chicken Biryani": 40, "Veg Biryani": 18},
    "2026-10-16": {"Paneer Tikka": 22, "Chicken Biryani": 42, "Veg Biryani": 20},
}
STOCK = {
    "paneer": "paneer: 0 kg - ran out on 2026-10-23 at 2:10 pm",
    "chicken": "chicken: 6 kg",
    "rice": "rice: 18 kg",
}


# ---------- TOOLS: plain functions + @mcp.tool() ----------
@mcp.tool()
def get_stock(item: str) -> str:
    """Current stock of ONE ingredient, e.g. paneer."""
    print(f"[server] get_stock({item})", file=sys.stderr)        # logs go to stderr, NEVER print() plain
    return STOCK.get(item.lower(), f"{item} is not in the inventory")


@mcp.tool()
def get_sales(day: str) -> str:
    """Plates sold per dish on ONE day. day is YYYY-MM-DD, e.g. 2026-10-23."""
    print(f"[server] get_sales({day})", file=sys.stderr)
    dishes = SALES.get(day)
    if dishes is None:
        return f"no sales recorded for {day}"
    lines = ", ".join(f"{dish} {plates}" for dish, plates in dishes.items())
    return f"{day}: {lines} - total {sum(dishes.values())} plates"


# ---------- NEW: a RESOURCE - read-only data, found by its URI ----------
@mcp.resource("kitchen://menu")
def menu() -> str:
    """Today's menu with prices."""
    return "Paneer Tikka - Rs 220\nChicken Biryani - Rs 249\nVeg Biryani - Rs 199"


# ---------- NEW: a PROMPT - a ready-made prompt the user can pick ----------
@mcp.prompt()
def daily_digest(day: str) -> str:
    """The owner's morning digest for one day."""
    return (f"You are the morning manager of a cloud kitchen. Use get_sales for {day} and for the "
            f"same weekday one week earlier. If a dish dropped a lot, check its main ingredient with "
            f"get_stock. Reply with EXACTLY 3 plain lines: totals, the biggest drop and its cause, one action.")


if __name__ == "__main__":
    mcp.run()                                  # stdio by default: wait for messages on input