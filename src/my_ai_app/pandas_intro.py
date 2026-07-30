import numpy as np
import pandas as pd


def main() -> None:
    """Explore a small DataFrame end to end."""
    df = pd.DataFrame(
        {
            "customer": ["Ravi", "Priya", "Ravi", "Anand", "Meera"],
            "city": ["Chennai", "Bengaluru", "Chennai", "Chennai", "Hyderabad"],
            "dish": ["Biryani", "Dosa", "Dosa", "Biryani", "Biryani"],
            "amount": [250.0, 120.0, 120.0, 250.0, 300.0],
        }
    )

    print("--- head ---")
    print(df.head())

    print("\n--- shape ---")
    print(df.shape)

    print("\n--- info ---")
    df.info()

    print("\n--- describe ---")
    print(df.describe())

    # 1. New columns (vectorized, no loop)
    df["gst"] = df["amount"] * 0.05
    df["total"] = df["amount"] + df["gst"]
    df["tier"] = np.where(df["amount"] >= 250, "high", "low")

    print("\n--- with gst, total, tier ---")
    print(df)

    # 2. Filter: Chennai orders above 200
    chennai_high = df[(df["city"] == "Chennai") & (df["amount"] > 200)]
    print("\n--- Chennai orders above 200 ---")
    print(chennai_high)

    # 3 + 4. Group by city, then flatten the index
    by_city = (
        df.groupby("city")
        .agg(
            orders=("amount", "count"),
            revenue=("amount", "sum"),
            avg_order=("amount", "mean"),
        )
        .reset_index()
    )
    print("\n--- by city ---")
    print(by_city)

    # 5. Merge customer phone numbers (Meera deliberately missing)
    customers = pd.DataFrame(
        {
            "customer": ["Ravi", "Priya", "Anand"],
            "phone": ["9840011111", "9840022222", "9840033333"],
        }
    )
    merged = df.merge(customers, on="customer", how="left")
    print("\n--- merged with customers ---")
    print(merged[["customer", "city", "amount", "phone"]])

    # 6. Nulls introduced by the left join
    print("\n--- null counts ---")
    print(merged.isna().sum())

    # Bonus: sort, rename
    top = merged.sort_values("total", ascending=False).rename(
        columns={"total": "order_value"}
    )
    print("\n--- sorted by value ---")
    print(top[["customer", "dish", "order_value"]])


if __name__ == "__main__":
    main()
