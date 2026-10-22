import os

from dotenv import load_dotenv
from groq import Groq
from pydantic import BaseModel, ValidationError

load_dotenv()
api_key = os.environ.get("GROQ_API_KEY")
if not api_key:
    raise SystemExit("GROQ_API_KEY missing - put it in .env")
client = Groq(api_key=api_key)


class BillLine(BaseModel):
    item: str
    quantity: float
    unit: str
    price: float


class Bill(BaseModel):
    supplier: str
    lines: list[BillLine]


BILL_TEXT = """Sri Lakshmi Traders, KR Market
Onion 12 kg @ 38 = 456
Tomato 7 kg @ 42 = 294
Basmati rice 25 kg @ 96 = 2400
Total 3150"""


def extract(mode: str) -> str:
    if mode == "json_object":
        fmt = {"type": "json_object"}
    else:
        fmt = {"type": "json_schema",
               "json_schema": {"name": "bill", "schema": Bill.model_json_schema()}}
    resp = client.chat.completions.create(
        model="openai/gpt-oss-120b",
        messages=[
            {"role": "system", "content": "Extract this supplier bill as JSON."},
            {"role": "user", "content": BILL_TEXT},
        ],
        response_format=fmt,
        temperature=0,
        reasoning_effort="low",
        max_tokens=2000,
    )
    return resp.choices[0].message.content


for mode in ["json_object", "json_schema"]:
    raw = extract(mode)
    print(f"=== {mode} ===\n{raw}")
    try:
        bill = Bill.model_validate_json(raw)
        print(f"VALID: {len(bill.lines)} lines from {bill.supplier}\n")
    except ValidationError as e:
        print(f"INVALID: {e.error_count()} problems\n")