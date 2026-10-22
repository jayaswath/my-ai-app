import pandas as pd

from my_ai_app.database import engine

df = pd.read_sql("SELECT * FROM ml_orders", engine)

df["hour"] = df["placed_at"].dt.hour
df["is_peak"] = df["hour"].isin([12, 13, 20, 21]).astype(int)

print(df[["placed_at", "hour", "is_peak"]].head(5))
print(df.groupby("is_peak")["is_late"].mean().round(3))