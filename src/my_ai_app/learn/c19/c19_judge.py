import json
import os

from dotenv import load_dotenv
from groq import Groq

load_dotenv()
api_key = os.environ.get("GROQ_API_KEY")
if not api_key:
    raise SystemExit("GROQ_API_KEY is not set — put it in .env")
client = Groq(api_key=api_key)

JUDGE_MODEL = "openai/gpt-oss-120b"

FACTS = ("Yesterday: revenue Rs 18,450 from 92 orders. "
         "Paneer ran out at 8 pm (stock 0 kg). Top dish: Chicken Biryani, 31 plates.")

RUBRIC = """You are grading a morning digest written for a busy restaurant owner.

FACTS (the truth):
{facts}

DIGEST:
{digest}

Answer two questions:
1. covers_stockout: does the digest say that paneer ran out?
2. clear: is it short (5 lines or less) and plain, with NO numbers or events that are not in the FACTS? Short advice (like "reorder today") and greetings are allowed.

Return ONLY JSON: {{"covers_stockout": true or false, "clear": true or false, "reason": "<one sentence>"}}"""


def judge(digest):
    response = client.chat.completions.create(
        model=JUDGE_MODEL,
        temperature=0,
        response_format={"type": "json_object"},
        messages=[{"role": "user", "content": RUBRIC.format(facts=FACTS, digest=digest)}],
    )
    return json.loads(response.choices[0].message.content)


# three digests + MY marks (the human check)
DIGESTS = [
    {"text": "Revenue Rs 18,450 from 92 orders. Paneer ran out at 8 pm, reorder today. "
             "Chicken Biryani led with 31 plates.",
     "mine": {"covers_stockout": True, "clear": True}},
    {"text": "Revenue Rs 18,450 from 92 orders. Chicken Biryani led with 31 plates. Great day!",
     "mine": {"covers_stockout": False, "clear": True}},
    {"text": "Good morning! Yesterday was busy: Rs 18,450 from 92 orders, and this weekend should "
             "cross Rs 25,000. Paneer finished at 8 pm. Also think about adding Chinese dishes and "
             "running Instagram ads, customers love both.",
     "mine": {"covers_stockout": True, "clear": False}},
]

agree = 0
for d in DIGESTS:
    verdict = judge(d["text"])
    same = all(verdict.get(k) == v for k, v in d["mine"].items())
    agree += same
    print("AGREE   " if same else "DISAGREE", d["text"][:60], "...")
    print("         judge:", verdict)
    print("         mine :", d["mine"])

print(f"\njudge agreed with me on {agree} / {len(DIGESTS)}")