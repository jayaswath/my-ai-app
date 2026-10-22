import os

from dotenv import load_dotenv
from groq import Groq

load_dotenv()
api_key = os.environ.get("GROQ_API_KEY")
if not api_key:
    raise SystemExit("GROQ_API_KEY missing - put it in .env")
client = Groq(api_key=api_key)

MODEL = "openai/gpt-oss-120b"

menu = "\n".join(f"Dish {i}: price {i * 10} rupees, prep time {i % 30 + 5} minutes" for i in range(1, 201))
SYSTEM = "You are the KitchenOS assistant. Answer in one short line.\nToday's menu:\n" + menu


def ask(question):
    resp = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": SYSTEM},
            {"role": "user", "content": question},
        ],
        reasoning_effort="low",
        max_tokens=300,
    )
    usage = resp.usage
    details = usage.prompt_tokens_details
    cached = details.cached_tokens if details else 0
    print(question)
    print("   answer:", resp.choices[0].message.content)
    print("   prompt tokens:", usage.prompt_tokens, "| cached:", cached)


ask("What is the price of Dish 7?")
ask("What is the prep time of Dish 12?")