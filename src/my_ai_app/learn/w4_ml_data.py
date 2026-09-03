"""Generate a fake order book for the delivery-delay model.

Nothing here is real. The lateness rule is written by hand at the bottom,
which is why a model can find it. Real kitchens are not this obliging.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from my_ai_app.database import engine

N_ORDERS = 8_000
SEED = 42
BRANCHES = ["Indiranagar", "Koramangala", "HSR Layout", "Whitefield"]
PLATFORMS = ["swiggy", "zomato", "direct"]
BASES = ["Chicken", "Paneer", "Mutton", "Egg", "Veg", "Prawn"]
FORMS = ["Biryani", "Curry", "Fried Rice", "Noodles", "Roll", "Tikka", "Kebab", "Thali", "Pulao", "Momos"]
SLOW_FORMS = {"Biryani", "Tikka", "Kebab", "Thali"}          # tandoor and dum, not a wok
DISHES = [f"{b} {f}" for b in BASES for f in FORMS]           # 6 x 10 = 60
SLOW = [d for d in DISHES if d.split(" ", 1)[1] in SLOW_FORMS]
FAST = [d for d in DISHES if d.split(" ", 1)[1] not in SLOW_FORMS]


def generate_orders(n: int = N_ORDERS, seed: int = SEED) -> pd.DataFrame:
    """Write out 8,000 dockets by hand, then decide which ones ran late."""
    rng = np.random.default_rng(seed)

    # --- when the order was placed -------------------------------------
    # Real kitchens have two spikes a day. Weight the hour pool so lunch
    # and dinner appear more often than 4pm.
    start = pd.Timestamp("2025-01-01")
    day_offset = rng.integers(0, 90, size=n)
    hour_pool = np.array([11, 12, 13, 13, 14, 19, 20, 20, 21, 22, 9, 16, 23])
    hour = rng.choice(hour_pool, size=n)
    minute = rng.integers(0, 60, size=n)
    placed_at = (
        start
        + pd.to_timedelta(day_offset, unit="D")
        + pd.to_timedelta(hour, unit="h")
        + pd.to_timedelta(minute, unit="m")
    )

    # --- who and where -------------------------------------------------
    branch = rng.choice(BRANCHES, size=n, p=[0.30, 0.35, 0.20, 0.15])
    platform = rng.choice(PLATFORMS, size=n, p=[0.45, 0.40, 0.15])

    # --- the basket ----------------------------------------------------
    item_count = rng.integers(1, 9, size=n)
    order_value = (item_count * rng.normal(220, 60, size=n)).round(2).clip(80, None)

    # --- distance, with a deliberate hole ------------------------------
    # Pickup orders have no delivery distance. That NaN is not dirty data,
    # it is a real fact about the order, and the imputer has to handle it.
    distance_km = rng.gamma(shape=2.0, scale=1.6, size=n).round(2).clip(0.3, 14)
    is_pickup = (platform == "direct") & (rng.random(n) < 0.55)
    distance_km = np.where(is_pickup, np.nan, distance_km)

    # --- how busy the kitchen was at that moment -----------------------
    is_peak = np.isin(hour, [12, 13, 20, 21]).astype(int)
    kitchen_load = rng.poisson(6 + 9 * is_peak, size=n).clip(0, 40)
    riders_available = rng.poisson(7 - 2 * is_peak, size=n).clip(0, 20)

    # --- the hand-written lateness rule --------------------------------
    # Whitefield is far from everything; HSR runs tight. Read the signs:
    # busier kitchen and longer distance push late UP, more riders pulls
    # it DOWN, and pickup barely goes late because nobody has to drive.
    branch_effect = (
        pd.Series(branch)
        .map({"Indiranagar": 0.0, "Koramangala": 0.35, "HSR Layout": -0.2, "Whitefield": 0.5})
        .to_numpy()
    )
    dist_filled = np.where(np.isnan(distance_km), 0.0, distance_km)

    logit = (
        -3.1
        + 0.11 * kitchen_load
        + 0.18 * dist_filled
        - 0.16 * riders_available
        + 0.45 * is_peak
        + branch_effect
        + 0.05 * item_count
        - 1.4 * is_pickup.astype(float)
        + rng.normal(0, 0.5, size=n)      # nothing is perfectly predictable
    )
    prob_late = 1 / (1 + np.exp(-logit))
    is_late = (rng.random(n) < prob_late).astype(int)

    # --- columns added after the label, on a separate dice cup ---------
    # seed+1 leaves the seed-42 stream untouched, so nothing above changes.
    rng2 = np.random.default_rng(seed + 1)

    # Big peak-hour orders lean toward the slow section of the menu.
    # dish never touches is_late directly - it rides along on item_count
    # and is_peak, which is exactly how a real confounder behaves.
    p_slow = 1 / (1 + np.exp(-(0.30 * (item_count - 4) + 0.50 * is_peak - 0.20)))
    pick_slow = rng2.random(n) < p_slow
    dish = np.where(pick_slow, rng2.choice(SLOW, n), rng2.choice(FAST, n))

    customer_id = rng2.integers(1, 2001, size=n)   # deliberately meaningless
    order_size = pd.cut(item_count, bins=[0, 2, 5, 8], labels=["small", "medium", "large"])

    return pd.DataFrame(
        {
            "order_id": np.arange(1, n + 1),
            "placed_at": placed_at,
            "branch": branch,
            "platform": platform,
            "item_count": item_count,
            "order_value": order_value,
            "distance_km": distance_km,
            "kitchen_load": kitchen_load,
            "riders_available": riders_available,
            "is_late": is_late,
            "dish": dish,                          # <-- add
            "customer_id": customer_id,            
            "order_size": order_size.astype(str),  
        }
    )


def write_orders() -> None:
    """Replace the table wholesale. This is a snapshot, not app state."""
    df = generate_orders()
    df.to_sql("ml_orders", engine, if_exists="replace", index=False)
    print(f"wrote {len(df):,} rows to ml_orders")
    print(f"late rate: {df['is_late'].mean():.3f}")
    print(f"missing distance_km: {df['distance_km'].isna().sum()}")


if __name__ == "__main__":
    write_orders()