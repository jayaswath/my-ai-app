import operator
from typing import Annotated, TypedDict

from langgraph.graph import END, START, StateGraph

from c16_cost import MODEL, client, run_tool, tools
from c16_digest import DIGEST_GOAL, RUN_DAY, load_sales_table, sales_facts


# ---------- the STATE: just the messages list (your "sheet") ----------
class State(TypedDict):
    messages: Annotated[list, operator.add]          # every node ADDS messages, like messages.append


# ---------- NODE 1: call the model once ----------
def call_model(state: State) -> dict:
    resp = client.chat.completions.create(
        model=MODEL, messages=state["messages"], tools=tools,
        reasoning_effort="low", max_tokens=800,
    )
    msg = resp.choices[0].message
    reply = {"role": "assistant", "content": msg.content or ""}
    if msg.tool_calls:
        reply["tool_calls"] = [call.model_dump() for call in msg.tool_calls]
        print(f"[agent] asks for: {', '.join(call.function.name for call in msg.tool_calls)}")
    else:
        print("[agent] final answer")
    return {"messages": [reply]}


# ---------- NODE 2: run every tool the model asked for ----------
def run_tools(state: State) -> dict:
    last = state["messages"][-1]                     # the model's request is the newest message
    results = []
    for call in last["tool_calls"]:
        result = run_tool(call["function"]["name"], call["function"]["arguments"])
        print(f"[tools] {call['function']['name']}{call['function']['arguments']} -> {result}")
        results.append({"role": "tool", "tool_call_id": call["id"], "content": result})
    return {"messages": results}


# ---------- the ROUTER: did the model ask for tools? ----------
def route(state: State) -> str:
    if state["messages"][-1].get("tool_calls"):
        return "tools"
    return END


# ---------- the GRAPH ----------
graph = StateGraph(State)
graph.add_node("agent", call_model)
graph.add_node("tools", run_tools)
graph.add_edge(START, "agent")
graph.add_conditional_edges("agent", route, ["tools", END])
graph.add_edge("tools", "agent")                     # the arrow BACK = the loop
app = graph.compile()


if __name__ == "__main__":
    load_sales_table()
    facts = sales_facts(RUN_DAY)
    trigger = (f"Today is {RUN_DAY:%A %Y-%m-%d}. Run the morning check.\n\n"
               f"Facts computed by code (correct - do not re-check them):\n{facts}")

    final = app.invoke(
        {"messages": [{"role": "system", "content": DIGEST_GOAL},
                      {"role": "user", "content": trigger}]},
        {"recursion_limit": 10},                     # the step limit
    )
    print(f"\n({len(final['messages'])} messages on the sheet at the end)")
    print("DIGEST:\n" + final["messages"][-1]["content"])