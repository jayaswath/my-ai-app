def trim_history(messages: list[dict], keep_last: int = 4) -> list[dict]:
    system = [m for m in messages if m["role"] == "system"]
    rest = [m for m in messages if m["role"] != "system"]
    return system + rest[-keep_last:]


history = [{"role": "system", "content": "You are the KitchenOS assistant."}]
for i in range(1, 6):
    history.append({"role": "user", "content": f"question {i}"})
    history.append({"role": "assistant", "content": f"answer {i}"})

print(len(history), "messages stored")
sent = trim_history(history, keep_last=4)
print(len(sent), "messages sent:")
for m in sent:
    print(" ", m["role"], "-", m["content"])