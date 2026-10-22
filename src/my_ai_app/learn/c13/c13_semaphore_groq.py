import asyncio
import os
import time

from dotenv import load_dotenv
from groq import AsyncGroq

load_dotenv()
api_key = os.environ.get("GROQ_API_KEY")
if not api_key:
    raise SystemExit("GROQ_API_KEY missing - put it in .env")
client = AsyncGroq(api_key=api_key)

limit = asyncio.Semaphore(3)


async def ask(question: str) -> str:
    async with limit:
        resp = await client.chat.completions.create(
            model="openai/gpt-oss-120b",
            messages=[{"role": "user", "content": question}],
            reasoning_effort="low",
            max_tokens=300,
        )
        return resp.choices[0].message.content


async def main():
    dishes = ["Biryani", "Dosa", "Chai", "Naan", "Idli", "Vada", "Paneer Tikka", "Dal Makhani", "Gulab Jamun", "Upma"]
    questions = [f"One word, plain text, no markdown: famous in which state  {d}?" for d in dishes]
    answers = await asyncio.gather(*[ask(q) for q in questions])
    print(answers)


start = time.perf_counter()
asyncio.run(main())
print(f"total: {time.perf_counter() - start:.1f}s")