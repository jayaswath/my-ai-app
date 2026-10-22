import hashlib
import json
import os
import time

from dotenv import load_dotenv
from groq import Groq

load_dotenv()
api_key = os.environ.get("GROQ_API_KEY")
if not api_key:
    raise SystemExit("GROQ_API_KEY missing - put it in .env")
client = Groq(api_key=api_key)

MODEL = "openai/gpt-oss-120b"
TTL = 5  # seconds an answer stays fresh          # NEW
cache = {}


def make_key(messages):
    text = json.dumps({"model": MODEL, "messages": messages}, sort_keys=True)
    return hashlib.sha256(text.encode()).hexdigest()


def ask(messages):
    key = make_key(messages)
    if key in cache:
        answer, saved_at = cache[key]                 # NEW 
        if time.time() - saved_at < TTL:              # NEW
            return answer
    resp = client.chat.completions.create(
        model=MODEL,
        messages=messages,
        reasoning_effort="low",
        max_tokens=300,
    )
    answer = resp.choices[0].message.content
    cache[key] = (answer, time.time())                # NEW
    return answer


messages = [{"role": "user", "content": "One word, plain text: the main ingredient of Dosa?"}]


def show(label):
    start = time.perf_counter()
    answer = ask(messages)
    print(label, "->", answer, f"{time.perf_counter() - start:.2f}s")


show("first   ")
show("again   ")
time.sleep(6)
show("after 6s")