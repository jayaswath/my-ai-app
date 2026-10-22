import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

from my_ai_app.database import engine

NUM = ["item_count", "order_value", "distance_km", "kitchen_load", "riders_available"]
CAT = ["branch", "platform"]

df = pd.read_sql("SELECT * FROM ml_orders", engine)
y = df["is_late"]

print("customers:", df["customer_id"].nunique())
print("median orders per customer:", df["customer_id"].value_counts().median())

def build(num_cols: list[str]) -> Pipeline:
    """Same station as always. Only the numeric column list changes."""
    return Pipeline([
        ("prep", ColumnTransformer([
            ("num", Pipeline([
                ("impute", SimpleImputer(strategy="median", add_indicator=True)),
                ("scale", StandardScaler()),
            ]), num_cols),
            ("cat", Pipeline([
                ("impute", SimpleImputer(strategy="most_frequent")),
                ("encode", OneHotEncoder(handle_unknown="ignore", sparse_output=False)),
            ]), CAT),
        ])),
        ("model", LogisticRegression(max_iter=2000, random_state=42)),
    ])


def score(frame: pd.DataFrame, num_cols: list[str], label: str) -> None:
    """Split, fit, and print train and test AUC side by side."""
    pipe = build(num_cols)
    X = frame[num_cols + CAT]
    X_tr, X_te, y_tr, y_te = train_test_split(X, y, test_size=0.2, stratify=y, random_state=42)
    pipe.fit(X_tr, y_tr)
    tr = roc_auc_score(y_tr, pipe.predict_proba(X_tr)[:, 1])
    te = roc_auc_score(y_te, pipe.predict_proba(X_te)[:, 1])
    print(f"{label:46s} train={tr:.3f}  test={te:.3f}")


print("ready")

score(df, NUM, "A  no customer feature at all")

leaky = df.copy()
leaky["cust_avg"] = leaky.groupby("customer_id")["is_late"].transform("mean")

score(leaky, NUM + ["cust_avg"], "B  LEAKY - averaged over all 8,000 rows")

train_idx, _ = train_test_split(df.index, test_size=0.2, stratify=y, random_state=42)

prior = y.loc[train_idx].mean()
means = df.loc[train_idx].groupby("customer_id")["is_late"].mean()

honest = df.copy()
honest["cust_avg"] = honest["customer_id"].map(means).fillna(prior)

score(honest, NUM + ["cust_avg"], "C  honest - averaged over TRAIN rows only")