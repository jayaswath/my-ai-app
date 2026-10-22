import base64
import json
import os
from pathlib import Path
from typing import Literal

from dotenv import load_dotenv
from openai import OpenAI
from pydantic import BaseModel, Field, ValidationError, field_validator, model_validator

load_dotenv()
api_key = os.environ.get("GEMINI_API_KEY")
if not api_key:
    raise SystemExit("GEMINI_API_KEY missing - put it in .env")
client = OpenAI(
    api_key=api_key,
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
)


# ---- same as item 20 ----
class BillLine(BaseModel):
    item: str = Field(min_length=1)
    quantity: float = Field(gt=0, description="amount bought, e.g. 12")
    unit: Literal["kg", "g", "litre", "ml", "piece", "packet"]
    unit_price: float = Field(gt=0, description="price for ONE unit, e.g. 38")
    line_total: float = Field(gt=0, description="quantity x unit_price, e.g. 456")

    @field_validator("unit", mode="before")
    @classmethod
    def clean_unit(cls, v):
        return v.strip().lower()

    @model_validator(mode="after")
    def total_must_match(self):
        if abs(self.quantity * self.unit_price - self.line_total) > 1:
            raise ValueError(f"{self.quantity} x {self.unit_price} is not {self.line_total}")
        return self


# ---- new: the whole bill ----
class Bill(BaseModel):
    supplier: str
    bill_number: str
    lines: list[BillLine]
    grand_total: float = Field(gt=0)

    @model_validator(mode="after")
    def lines_must_add_up(self):
        added = sum(line.line_total for line in self.lines)
        if abs(added - self.grand_total) > 1:
            raise ValueError(f"lines add up to {added}, but grand total is {self.grand_total}")
        return self


SYSTEM = (
    "Extract the supplier bill in the image as JSON matching this schema:\n"
    + json.dumps(Bill.model_json_schema())
    + "\nReturn ONLY the JSON object. No markdown, no ``` fences."
)


def extract_bill(image_b64, max_tries=3):
    messages = [
        {"role": "system", "content": SYSTEM},
        {
            "role": "user",
            "content": [
                {"type": "text", "text": "Extract this bill."},
                {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{image_b64}"}},
            ],
        },
    ]
    for attempt in range(1, max_tries + 1):
        resp = client.chat.completions.create(model="gemini-3.8-flash", messages=messages)
        raw = resp.choices[0].message.content
        try:
            return Bill.model_validate_json(raw)
        except ValidationError as e:
            print(f"attempt {attempt} failed:\n{e}\n")
            messages.append({"role": "assistant", "content": raw})
            messages.append({"role": "user", "content": f"Fix this: {e}"})
    raise ValueError("no valid bill after all tries")


image_path = Path("data") / "sample_bill.jpg"
image_b64 = base64.b64encode(image_path.read_bytes()).decode("utf-8")

bill = extract_bill(image_b64)
print("Supplier:", bill.supplier, "| Bill:", bill.bill_number)
for line in bill.lines:
    print(" ", line.item, line.quantity, line.unit, "x", line.unit_price, "=", line.line_total)
print("Grand total:", bill.grand_total)