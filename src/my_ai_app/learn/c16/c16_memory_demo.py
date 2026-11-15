import os

from dotenv import load_dotenv
from groq import Groq

load_dotenv()

api_key = os.environ.get("GROQ_API_KEY")
if not api_key:
    raise SystemExit("GROQ_API_KEY is missing - check .env")
client = Groq(api_key=api_key)
MODEL = "openai/gpt-oss-120b"


def ask(messages):
    resp = client.chat.completions.create(
        model=MODEL, messages=messages, reasoning_effort="low", max_tokens=400,
    )
    print(f"   (sent {len(messages)} messages = {resp.usage.prompt_tokens} tokens)")
    return resp.choices[0].message.content


# ---------- 1. WITHOUT history: every call alone ----------
print("1. WITHOUT history")
print("A:", ask([{"role": "user", "content": "My name is Jay and I run a cloud kitchen."}]))
print("A:", ask([{"role": "user", "content": "What is my name and what do I run?"}]))

# ---------- 2. WITH history: we keep the sheet and re-send it ----------
print("\n2. WITH history")
history = [{"role": "user", "content": "My name is Jay and I run a cloud kitchen."}]
reply = ask(history)
print("A:", reply)
history.append({"role": "assistant", "content": reply})          # write its answer on the sheet
history.append({"role": "user", "content": "What is my name and what do I run?"})
print("A:", ask(history))