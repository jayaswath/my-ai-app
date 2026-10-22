import os

from dotenv import load_dotenv
from groq import Groq

load_dotenv()
api_key = os.environ.get("GROQ_API_KEY")
if not api_key:
    raise SystemExit("GROQ_API_KEY missing - put it in .env")
client = Groq(api_key=api_key)

stream = client.chat.completions.create(
    model="openai/gpt-oss-120b",
    messages=[{"role": "user", "content": "In 5 short lines, plain text, how do I make masala chai?"}],
    reasoning_effort="low",
    max_tokens=500,
    stream=True,
)

for chunk in stream:
    piece = chunk.choices[0].delta.content
    if piece:
        print(piece, end="", flush=True)
print()