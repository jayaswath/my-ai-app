import operator
import sys
from typing import Annotated, TypedDict

from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph.graph import END, START, StateGraph

CRASH = len(sys.argv) > 1 and sys.argv[1] == "crash"     # run with the word crash to fake a failure


class State(TypedDict):
    notes: Annotated[list, operator.add]


def fetch_facts(state: State) -> dict:
    print("  running fetch_facts   (imagine: slow SQL + a paid Groq call)")
    return {"notes": ["facts fetched"]}


def check_stock(state: State) -> dict:
    print("  running check_stock")
    if CRASH:
        raise ConnectionError("stock database is down")
    return {"notes": ["paneer: 0 kg"]}


def write_digest(state: State) -> dict:
    print("  running write_digest")
    return {"notes": ["digest written"]}


graph = StateGraph(State)
graph.add_node("fetch_facts", fetch_facts)
graph.add_node("check_stock", check_stock)
graph.add_node("write_digest", write_digest)
graph.add_edge(START, "fetch_facts")
graph.add_edge("fetch_facts", "check_stock")
graph.add_edge("check_stock", "write_digest")
graph.add_edge("write_digest", END)

config = {"configurable": {"thread_id": "digest-2026-10-25"}}     # one thread per day's digest

with SqliteSaver.from_conn_string("data/lg_checkpoints.db") as saver:
    app = graph.compile(checkpointer=saver)
    saved = app.get_state(config)                      # what is saved for this thread?

    if saved.next:                                     # it stopped half-way last time
        print(f"RESUMING - the next step was: {saved.next}")
        result = app.invoke(None, config)              # None = don't start over, continue
    elif saved.values:                                 # it finished last time
        print("ALREADY DONE for this thread:", saved.values["notes"])
        sys.exit()
    else:                                              # nothing saved yet
        print("STARTING FRESH")
        result = app.invoke({"notes": []}, config)

    print("NOTES:", result["notes"])