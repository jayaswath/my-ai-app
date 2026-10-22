"""Correlation, regression, and why 'related' isn't 'causes'."""

import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression


def build_data(n: int = 300, seed: int = 42) -> pd.DataFrame:
    """Fake delivery data with a KNOWN confounder: busy nights.

    Busy nights cause BOTH slow delivery and bad ratings. Delivery
    time itself has only a small real effect.
    """
    rng = np.random.default_rng(seed=seed)

    is_busy = rng.binomial(1, 0.3, size=n)

    delivery = 25 + 15 * is_busy + rng.normal(0, 5, size=n)
    order_value = 200 + rng.normal(0, 60, size=n)

    # rating depends mostly on BUSY, only slightly on delivery time
    rating = 4.6 - 0.8 * is_busy - 0.01 * delivery + rng.normal(0, 0.3, size=n)
    rating = np.clip(rating, 1, 5)

    return pd.DataFrame(
        {
            "delivery_minutes": delivery,
            "order_value": order_value,
            "is_busy": is_busy,
            "rating": rating,
        }
    )


def main() -> None:
    df = build_data()

    print("--- Correlation matrix ---")
    print(df.corr().round(3))

    print("\n--- Simple regression: rating ~ delivery_minutes ---")
    X = df[["delivery_minutes"]]
    y = df["rating"]
    simple = LinearRegression().fit(X, y)
    print(f"  slope: {simple.coef_[0]:+.4f} stars per minute")
    print(f"  R2:    {simple.score(X, y):.3f}")

    print("\n--- Multiple regression: add is_busy ---")
    X2 = df[["delivery_minutes", "is_busy"]]
    multi = LinearRegression().fit(X2, y)
    for name, coef in zip(X2.columns, multi.coef_, strict=True):
        print(f"  {name:20} {coef:+.4f}")
    print(f"  R2:    {multi.score(X2, y):.3f}")

    print("\n--- Prediction ---")
    new = pd.DataFrame({"delivery_minutes": [20, 40, 60], "is_busy": [0, 1, 1]})
    for mins, busy, pred in zip(
        new["delivery_minutes"], new["is_busy"], multi.predict(new), strict=True
    ):
        print(f"  {mins} min, busy={busy} -> predicted rating {pred:.2f}")


if __name__ == "__main__":
    main()