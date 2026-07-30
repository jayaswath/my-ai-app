from pathlib import Path

import pandas as pd


def posts_to_frame(posts: list[dict]) -> pd.DataFrame:
    """Convert raw API posts into a cleaned DataFrame."""
    df = pd.DataFrame(posts)

    df = df.rename(columns={"id": "external_id", "userId": "user_id"})

    df["title"] = df["title"].str.strip()
    df["body"] = df["body"].str.replace("\n", " ", regex=False).str.strip()

    df["title_words"] = df["title"].str.split().str.len()
    df["body_words"] = df["body"].str.split().str.len()
    df["is_long"] = df["body_words"] > 30

    return df.drop_duplicates(subset=["external_id"])


def authors_to_frame(users: list[dict]) -> pd.DataFrame:
    """Convert raw API users into a cleaned DataFrame."""
    rows = [
        {
            "external_id": u["id"],
            "name": u["name"].strip(),
            "username": u["username"],
            "email": u["email"].lower(),
            "company": u.get("company", {}).get("name"),
            "city": u.get("address", {}).get("city"),
        }
        for u in users
    ]
    return pd.DataFrame(rows).drop_duplicates(subset=["external_id"])


def save_snapshot(df: pd.DataFrame, filename: str) -> Path:
    """Write a DataFrame to Parquet under data/ and return the path."""
    Path("data").mkdir(exist_ok=True)
    path = Path("data") / filename
    df.to_parquet(path, index=False)
    return path
