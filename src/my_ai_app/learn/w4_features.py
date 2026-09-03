"""Preprocessing and model, sealed in one object.

The whole point: fit() only ever sees training rows, so no summary
statistic can leak backwards from the test set into the model.
"""

from __future__ import annotations
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report, roc_auc_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

from my_ai_app.database import engine

NUMERIC_COLS = ["item_count", "order_value", "distance_km", "kitchen_load", "riders_available"]
CATEGORICAL_COLS = ["branch", "platform"]
TARGET = "is_late"


def load_orders() -> pd.DataFrame:
    """Pull the docket book off the shelf."""
    return pd.read_sql("SELECT * FROM ml_orders", engine)


def build_preprocessor() -> ColumnTransformer:
    """Two prep stations. Numbers go to one board, labels to the other."""
    numeric_pipe = Pipeline(
        steps=[
            ("impute", SimpleImputer(strategy="median")),
            ("scale", StandardScaler()),
        ]
    )
    categorical_pipe = Pipeline(
        steps=[
            ("impute", SimpleImputer(strategy="most_frequent")),
            ("encode", OneHotEncoder(handle_unknown="ignore", sparse_output=False)),
        ]
    )
    return ColumnTransformer(
        transformers=[
            ("num", numeric_pipe, NUMERIC_COLS),
            ("cat", categorical_pipe, CATEGORICAL_COLS),
        ],
        remainder="drop",       # order_id and placed_at are NOT features today
    )


def build_pipeline() -> Pipeline:
    """The recipe card: prep steps and cooking on one piece of paper."""
    return Pipeline(
        steps=[
            ("prep", build_preprocessor()),
            ("model", LogisticRegression(max_iter=1000, random_state=42)),
        ]
    )

def add_time_features(df: pd.DataFrame) -> pd.DataFrame:
    """Read the clock off the docket. Never hand a raw timestamp to a model."""
    df = df.copy()                       # never mutate the caller's frame
    ts = df["placed_at"]
    df["hour"] = ts.dt.hour
    df["dayofweek"] = ts.dt.dayofweek    # Monday = 0
    df["is_weekend"] = (ts.dt.dayofweek >= 5).astype(int)
    # 23:00 and 00:00 are one hour apart. As plain numbers they are 23 apart.
    # Put the clock face back on a circle.
    df["hour_sin"] = np.sin(2 * np.pi * df["hour"] / 24)
    df["hour_cos"] = np.cos(2 * np.pi * df["hour"] / 24)
    return df


def main() -> None:
    """Fit once, then read the station back to see what it learned."""
    df = load_orders()

    X = df[NUMERIC_COLS + CATEGORICAL_COLS]   # DataFrame — note double brackets
    y = df[TARGET]                            # Series   — single brackets

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, stratify=y, random_state=42
    )
    print(f"train {X_train.shape}  test {X_test.shape}")
    print(f"late rate  train {y_train.mean():.3f}  test {y_test.mean():.3f}")

    pipe = build_pipeline()
    pipe.fit(X_train, y_train)

    y_pred = pipe.predict(X_test)
    y_prob = pipe.predict_proba(X_test)[:, 1]

    print(f"\nROC AUC: {roc_auc_score(y_test, y_prob):.3f}")
    print(classification_report(y_test, y_pred, target_names=["on time", "late"], digits=3))

    names = pipe.named_steps["prep"].get_feature_names_out()
    coefs = pipe.named_steps["model"].coef_[0]
    print(f"{len(names)} columns after preprocessing\n")
    for name, coef in sorted(zip(names, coefs), key=lambda t: -abs(t[1])):
        print(f"{name:28s} {coef:+.3f}")


if __name__ == "__main__":
    main()