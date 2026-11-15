import operator
from typing import Annotated, TypedDict

from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import END, START, StateGraph

from c16_cost import MODEL, client


class State(TypedDict):
    messages: Annotated[list, operator.add]


def call_model(state: State) -> dict:
    print(f"   (sent {len(state['messages'])} messages)")
    resp = client.chat.completions.create(
        model=MODEL, messages=state["messages"], reasoning_effort="low", max_tokens=400,
    )
    return {"messages": [{"role": "assistant", "content": resp.choices[0].message.content or ""}]}


graph = StateGraph(State)
graph.add_node("agent", call_model)
graph.add_edge(START, "agent")
graph.add_edge("agent", END)
app = graph.compile(checkpointer=InMemorySaver())      # NEW: save the state after every step


def ask(question, thread):
    config = {"configurable": {"thread_id": thread}}    # NEW: which conversation this is
    final = app.invoke({"messages": [{"role": "user", "content": question}]}, config)
    return final["messages"][-1]["content"]


print("Thread jay-1:")
print("A:", ask("My name is Jay and I run a cloud kitchen.", "jay-1"))
print("A:", ask("What is my name and what do I run?", "jay-1"))

print("\nThread new-guy:")
print("A:", ask("What is my name and what do I run?", "new-guy"))