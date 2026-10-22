from typing import Literal

from pydantic import BaseModel, Field, ValidationError, model_validator


class BillLine(BaseModel):
    item: str = Field(min_length=1)
    quantity: float = Field(gt=0, description="amount bought, e.g. 12")
    unit: Literal["kg", "g", "litre", "ml", "piece", "packet"]
    unit_price: float = Field(gt=0, description="price for ONE unit, e.g. 38")
    line_total: float = Field(gt=0, description="quantity x unit_price, e.g. 456")

    @model_validator(mode="after")
    def total_must_match(self):
        if abs(self.quantity * self.unit_price - self.line_total) > 1:
            raise ValueError(f"{self.quantity} x {self.unit_price} is not {self.line_total}")
        return self


tests = {
    "correct line": {"item": "Onion", "quantity": 12, "unit": "kg", "unit_price": 38, "line_total": 456},
    "price mix-up": {"item": "Onion", "quantity": 12, "unit": "kg", "unit_price": 456, "line_total": 456},
    "unknown unit": {"item": "Onion", "quantity": 12, "unit": "kgs", "unit_price": 38, "line_total": 456},
    "negative qty": {"item": "Onion", "quantity": -12, "unit": "kg", "unit_price": 38, "line_total": 456},
}

for name, data in tests.items():
    try:
        BillLine.model_validate(data)
        print(f"OK        {name}")
    except ValidationError as e:
        print(f"REJECTED  {name}: {e.errors()[0]['msg']}")