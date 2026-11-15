import operator
from typing import Annotated, TypedDict

from langgraph.graph import END, START, StateGraph


class State(TypedDict):
    dish: str
    plates_yesterday: int
    plates_last_week: int
    change: int
    notes: Annotated[list, operator.add]


# ---------- nodes: plain functions ----------
def compute_change(state: State) -> dict:
    change = state["plates_yesterday"] - state["plates_last_week"]
    return {"change": change, "notes": [f"change computed: {change}"]}


def investigate(state: State) -> dict:
    return {"notes": [f"BIG DROP - check the stock for {state['dish']}"]}


def all_good(state: State) -> dict:
    return {"notes": ["normal day - nothing to do"]}


# ---------- NEW: the router - the IF. It returns the NAME of the next node ----------
def route(state: State) -> str:
    if state["change"] <= -10:
        return "investigate"
    return "all_good"


# ---------- the graph ----------
graph = StateGraph(State)
graph.add_node("compute_change", compute_change)
graph.add_node("investigate", investigate)
graph.add_node("all_good", all_good)

graph.add_edge(START, "compute_change")
graph.add_conditional_edges("compute_change", route)   # NEW: after compute_change, ask route() where to go
graph.add_edge("investigate", END)
graph.add_edge("all_good", END)
app = graph.compile()

# ---------- run it for two dishes ----------
for tray in [
    {"dish": "Paneer Tikka", "plates_yesterday": 0, "plates_last_week": 22, "notes": []},
    {"dish": "Chicken Biryani", "plates_yesterday": 40, "plates_last_week": 42, "notes": []},
]:
    print(f"\n{tray['dish']}:")
    for update in app.stream(tray, stream_mode="updates"):
        print("  ", update)