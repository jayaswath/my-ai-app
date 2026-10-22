import numpy as np
import pandas as pd

from my_ai_app.database import engine

df = pd.read_sql("SELECT * FROM ml_orders", engine)

rng = np.random.default_rng(7)
dist = df["distance_km"].fillna(0)
df["delivery_minutes"] = (
    18
    + 1.1 * df["kitchen_load"]
    + 3.2 * dist
    - 0.9 * df["riders_available"]
    + rng.normal(0, 5, len(df))
).clip(lower=5).round(1)

print(df["delivery_minutes"].describe().round(1))