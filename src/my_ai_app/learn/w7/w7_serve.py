from pathlib import Path

import joblib
import pandas as pd
from fastapi import FastAPI
from pydantic import BaseModel

MODEL_FILE = Path("data/delay_model.joblib")
CUTOFF = 0.5

app = FastAPI(title="Delivery delay predictor")
model = joblib.load(MODEL_FILE)


class Order(BaseModel):
    """What the kitchen sends in: one order, at the moment it is placed."""
    item_count: int
    order_value: float
    distance_km: float | None = None
    kitchen_load: int
    riders_available: int
    branch: str
    platform: str


@app.post("/predict-delay")
def predict_delay(order: Order) -> dict:
    """Take one ticket through the window, read the notebook, send an answer back."""
    row = pd.DataFrame([order.model_dump()]).astype({"distance_km": float})
    prob = float(model.predict_proba(row)[0, 1])
    return {"late_probability": round(prob, 3), "warning": prob >= CUTOFF}