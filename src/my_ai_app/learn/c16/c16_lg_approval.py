import sys
from typing import TypedDict

from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph.graph import END, START, StateGraph
from langgraph.types import Command, interrupt


class State(TypedDict):
    item: str
    kg: float
    decision: str


def draft_order(state: State) -> dict:
    print(f"  draft_order: {state['kg']} kg {state['item']} drafted")
    return {}


def owner_approval(state: State) -> dict:
    answer = interrupt(f"Approve {state['kg']} kg {state['item']}? (y/n)")   # PAUSE here, save, stop
    print(f"  owner_approval: the owner said {answer}")                      # runs only after resume
    return {"decision": "approved" if answer == "y" else "rejected"}


def place_order(state: State) -> dict:
    if state["decision"] == "approved":
        print(f"  >>> ORDER SENT TO SUPPLIER: {state['kg']} kg {state['item']}")
    else:
        print("  order cancelled - nothing sent")
    return {}


graph = StateGraph(State)
graph.add_node("draft_order", draft_order)
graph.add_node("owner_approval", owner_approval)
graph.add_node("place_order", place_order)
graph.add_edge(START, "draft_order")
graph.add_edge("draft_order", "owner_approval")
graph.add_edge("owner_approval", "place_order")
graph.add_edge("place_order", END)

config = {"configurable": {"thread_id": "order-paneer-2026-10-24"}}
answer = sys.argv[1] if len(sys.argv) > 1 else None        # y or n typed after the file name

with SqliteSaver.from_conn_string("data/lg_approval.db") as saver:
    app = graph.compile(checkpointer=saver)
    saved = app.get_state(config)

    if answer:                                             # the OWNER is answering
        if not saved.next:
            print("Nothing is waiting for approval.")
        else:
            print(f"RESUMING with the owner's answer: {answer}")
            app.invoke(Command(resume=answer), config)     # continue the paused run
    elif saved.next:
        print("Still waiting for the owner. Run again with y or n after the file name.")
    elif saved.values:
        print("Already finished:", saved.values["decision"])
    else:                                                  # the AGENT starts
        print("STARTING: the agent drafts an order")
        result = app.invoke({"item": "paneer", "kg": 20, "decision": ""}, config)
        print("PAUSED - question for the owner:", result["__interrupt__"][0].value)