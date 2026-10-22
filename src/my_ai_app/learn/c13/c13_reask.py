import json
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
    unit_price: float
    line_total: float


class Bill(BaseModel):
    supplier: str
    lines: list[BillLine]


SCHEMA = json.dumps(Bill.model_json_schema())
SYSTEM = f"Extract the supplier bill as JSON matching this schema:\n{SCHEMA}"

BILL_TEXT = """Sri Lakshmi Traders, KR Market
Onion 12 kg @ 38 = 456
Tomato 7 kg @ 42 = 294
Basmati rice 25 kg @ 96 = 2400
Total 3150"""


def call(messages: list[dict]) -> str:
    resp = client.chat.completions.create(
        model="openai/gpt-oss-120b",
        messages=messages,
        response_format={"type": "json_object"},
        temperature=0,
        reasoning_effort="low",
        max_tokens=2000,
    )
    return resp.choices[0].message.content


def extract_bill(text: str, max_tries: int = 3, fake_first: str | None = None) -> Bill:
    messages = [
        {"role": "system", "content": SYSTEM},
        {"role": "user", "content": text},
    ]
    for attempt in range(1, max_tries + 1):
        raw = fake_first if (attempt == 1 and fake_first) else call(messages)
        try:
            return Bill.model_validate_json(raw)
        except ValidationError as e:
            first = e.errors()[0]
            print(f"attempt {attempt}: INVALID ({e.error_count()} problems) - asking the model to fix it")
            print(f"  e.g. {first['loc']}: {first['msg']}")
            messages.append({"role": "assistant", "content": raw})
            messages.append({"role": "user",
                             "content": f"Your JSON failed validation:\n{e}\nReturn the corrected JSON only."})
    raise ValueError(f"no valid bill after {max_tries} tries")


if __name__ == "__main__":
    bill = extract_bill(BILL_TEXT, fake_first='{"vendor": "Sri Lakshmi", "items": []}')
    for line in bill.lines:
        print(f"{line.item}: {line.quantity} {line.unit} x {line.unit_price} = {line.line_total}")