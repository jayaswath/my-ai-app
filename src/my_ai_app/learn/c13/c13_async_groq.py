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


async def ask(question: str) -> str:
    resp = await client.chat.completions.create(
        model="openai/gpt-oss-120b",
        messages=[{"role": "user", "content": question}],
        reasoning_effort="low",
        max_tokens=300,
    )
    return resp.choices[0].message.content


async def main():
    answers = await asyncio.gather(
        ask("One word: a South Indian breakfast."),
        ask("One word: a North Indian bread."),
        ask("One word: a popular Indian sweet."),
    )
    print(answers)


start = time.perf_counter()
asyncio.run(main())
print(f"total: {time.perf_counter() - start:.1f}s")