import operator
from typing import Annotated, TypedDict

from langgraph.graph import END, START, StateGraph


# ---------- 1. the STATE: the tray that travels between nodes ----------
class State(TypedDict):
    dish: str
    plates_yesterday: int
    plates_last_week: int
    change: int
    notes: Annotated[list, operator.add]     # reducer: ADD to this list, never replace it


# ---------- 2. NODES: plain functions - read the tray, return ONLY what changes ----------
def compute_change(state: State) -> dict:
    change = state["plates_yesterday"] - state["plates_last_week"]
    return {"change": change, "notes": [f"change computed: {change}"]}


def flag_drop(state: State) -> dict:
    if state["change"] <= -10:
        return {"notes": ["BIG DROP - investigate"]}
    return {"notes": ["normal day"]}


# ---------- 3. the GRAPH: two stations in a line ----------
graph = StateGraph(State)
graph.add_node("compute_change", compute_change)
graph.add_node("flag_drop", flag_drop)
graph.add_edge(START, "compute_change")
graph.add_edge("compute_change", "flag_drop")
graph.add_edge("flag_drop", END)
app = graph.compile()

# ---------- 4. run it ----------
start_tray = {"dish": "Paneer Tikka", "plates_yesterday": 0, "plates_last_week": 22, "notes": []}

print("RUN ORDER (what each node returned):")
for update in app.stream(start_tray, stream_mode="updates"):
    print("  ", update)

print("\nFINAL TRAY:")
print(app.invoke(start_tray))