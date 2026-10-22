import os

from dotenv import load_dotenv
from groq import Groq

load_dotenv()
api_key = os.environ.get("GROQ_API_KEY")
if not api_key:
    raise SystemExit("GROQ_API_KEY missing - put it in .env")
client = Groq(api_key=api_key)


def pct(now: float, before: float) -> float:
    return round((now / before - 1) * 100, 1)


SYSTEM = ("You write the owner's morning WhatsApp message. "
          "Copy the style of the example exactly. Use only the numbers given.")

EXAMPLE_DATA = """day: Saturday
orders: 280 (+5.3%)
revenue: Rs 84,000 (+6.1%)
star dish: Mutton Biryani, 90 plates
alert: Veg Biryani -35.0%"""

EXAMPLE_REPLY = """Good morning! Saturday: 280 orders (+5.3%), Rs 84,000 revenue (+6.1%).
Star dish: Mutton Biryani, 90 plates.
Watch out: Veg Biryani fell 35%. Try it as today's combo offer."""

today = (
    "day: Sunday\n"
    f"orders: 312 ({pct(312, 287):+}%)\n"
    f"revenue: Rs 96,400 ({pct(96400, 88100):+}%)\n"
    "star dish: Chicken Biryani, 142 plates\n"
    f"alert: Paneer Tikka {pct(18, 31):+}%"
)

messages = [
    {"role": "system", "content": SYSTEM},
    {"role": "user", "content": EXAMPLE_DATA},
    {"role": "assistant", "content": EXAMPLE_REPLY},
    {"role": "user", "content": today},
]

print(today, "\n")
resp = client.chat.completions.create(
    model="openai/gpt-oss-120b",
    messages=messages,
    temperature=0.2,
    reasoning_effort="low",
    max_tokens=1500,
)
print(resp.choices[0].message.content)