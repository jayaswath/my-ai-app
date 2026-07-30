import pandas as pd
import polars as pl

from my_ai_app.config import settings
from my_ai_app.database import engine

QUERY = """
    SELECT
        o.id,
        c.name AS customer,
        o.city,
        o.dish,
        o.amount,
        o.ordered_at
    FROM orders o
    JOIN customers c ON o.customer_id = c.id
    ORDER BY o.ordered_at
"""


def load_orders() -> pd.DataFrame:
    """Load all orders with customer names into a DataFrame."""
    return pd.read_sql(QUERY, engine)


def add_time_features(df: pd.DataFrame) -> pd.DataFrame:
    """Add date-derived columns."""
    df = df.copy()
    df["date"] = df["ordered_at"].dt.date
    df["hour"] = df["ordered_at"].dt.hour
    df["day_name"] = df["ordered_at"].dt.day_name()
    df["is_weekend"] = df["ordered_at"].dt.dayofweek >= 5
    return df


def revenue_by_dish(df: pd.DataFrame) -> pd.DataFrame:
    """Revenue and order count per dish, highest revenue first."""
    return (
        df.groupby("dish")
        .agg(revenue=("amount", "sum"), orders=("amount", "count"))
        .reset_index()
        .sort_values("revenue", ascending=False)
    )


def revenue_by_dish_polars() -> pl.DataFrame:
    """Same aggregation, written in Polars."""
    uri = settings.database_url.replace("postgresql+psycopg://", "postgresql://")
    df = pl.read_database_uri(QUERY, uri)
    return (
        df.group_by("dish")
        .agg(
            pl.col("amount").sum().alias("revenue"),
            pl.len().alias("orders"),
        )
        .sort("revenue", descending=True)
    )


def main() -> None:
    """Load, transform, aggregate, and save order data."""
    df = load_orders()
    df = add_time_features(df)

    print("--- with time features ---")
    print(df[["customer", "dish", "amount", "day_name", "hour", "is_weekend"]])

    print("\n--- revenue by dish (pandas) ---")
    print(revenue_by_dish(df))

    df.to_parquet("data/orders.parquet", index=False)
    print("\nSaved to data/orders.parquet")

    reloaded = pd.read_parquet("data/orders.parquet")
    print("\n--- dtypes after Parquet round-trip ---")
    print(reloaded.dtypes)

    print("\n--- revenue by dish (polars) ---")
    print(revenue_by_dish_polars())


if __name__ == "__main__":
    main()
