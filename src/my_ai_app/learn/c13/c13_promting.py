import os

from dotenv import load_dotenv
from groq import Groq

load_dotenv()
api_key = os.environ.get("GROQ_API_KEY")
if not api_key:
    raise SystemExit("GROQ_API_KEY missing - put it in .env")
client = Groq(api_key=api_key)

DATA = """date: Sunday 18 Oct
orders: 312 (last Sunday: 287)
revenue: Rs 96,400 (last Sunday: Rs 88,100)
top dish: Chicken Biryani 142 (last Sunday: 120)
falling dish: Paneer Tikka 18 (last Sunday: 31)
late deliveries: 9 of 312"""


def ask(messages: list[dict]) -> str:
    resp = client.chat.completions.create(
        model="openai/gpt-oss-120b",
        messages=messages,
        temperature=0.2,
        reasoning_effort="low",
        max_tokens=1500,
    )
    return resp.choices[0].message.content


vague = [{"role": "user", "content": "Summarise this: " + DATA}]

clear = [
    {"role": "system", "content": (
        "You write a morning WhatsApp message for a cloud-kitchen owner.\n"
        "Rules:\n"
        "- Maximum 4 short lines, plain text, no markdown, no emojis.\n"
        "- Line 1: orders and revenue vs last Sunday, with % change.\n"
        "- Line 2: the best-selling dish.\n"
        "- Line 3: the biggest problem and one concrete action.\n"
        "- Use only numbers from the data. Never invent numbers."
    )},
    {"role": "user", "content": f"<data>\n{DATA}\n</data>"},
]

print("=== VAGUE ===\n" + ask(vague))
print("\n=== CLEAR ===\n" + ask(clear))