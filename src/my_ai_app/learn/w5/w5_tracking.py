from pathlib import Path

import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import precision_score, recall_score, roc_auc_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

from my_ai_app.database import engine

NUM = ["item_count", "order_value", "distance_km", "kitchen_load", "riders_available"]
CAT = ["branch", "platform"]
RUNS_FILE = Path("data/runs.csv")

df = pd.read_sql("SELECT * FROM ml_orders", engine)
X, y = df[NUM + CAT], df["is_late"]
X_tr, X_te, y_tr, y_te = train_test_split(X, y, test_size=0.2, stratify=y, random_state=42)

print(X_tr.shape, X_te.shape)

def build_pipe(C: float, class_weight: str | None) -> Pipeline:
    """One prep card, with the two dials left adjustable."""
    return Pipeline([
        ("prep", ColumnTransformer([
            ("num", Pipeline([
                ("impute", SimpleImputer(strategy="median", add_indicator=True)),
                ("scale", StandardScaler()),
            ]), NUM),
            ("cat", Pipeline([
                ("impute", SimpleImputer(strategy="most_frequent")),
                ("encode", OneHotEncoder(handle_unknown="ignore", sparse_output=False)),
            ]), CAT),
        ])),
        ("model", LogisticRegression(C=C, class_weight=class_weight,
                                     max_iter=1000, random_state=42)),
    ])


print(build_pipe(1.0, "balanced").named_steps["model"])

def log_run(name: str, C: float, class_weight: str | None, cutoff: float) -> dict:
    """Cook one version, taste it, write the line on the pad."""
    pipe = build_pipe(C, class_weight)
    pipe.fit(X_tr, y_tr)

    prob = pipe.predict_proba(X_te)[:, 1]
    pred = (prob >= cutoff).astype(int)

    return {
        "run": name,
        "C": C,
        "class_weight": str(class_weight),
        "cutoff": cutoff,
        "auc": round(roc_auc_score(y_te, prob), 4),
        "precision": round(precision_score(y_te, pred, zero_division=0), 4),
        "recall": round(recall_score(y_te, pred), 4),
    }


print(log_run("test", 1.0, "balanced", 0.5))

runs = [
    log_run("week4-baseline",   1.0,  None,       0.50),
    log_run("week4-tuned",      1.0,  None,       0.20),
    log_run("balanced-default", 1.0, "balanced",  0.50),
    log_run("balanced-0.40",    1.0, "balanced",  0.40),
    log_run("low-C-balanced",   0.01, "balanced", 0.40),
    log_run("high-C-balanced", 100.0, "balanced", 0.40),
]

results = pd.DataFrame(runs)
RUNS_FILE.parent.mkdir(exist_ok=True)
results.to_csv(RUNS_FILE, index=False)

print(results.to_string(index=False))

loaded = pd.read_csv(RUNS_FILE)
print(loaded.sort_values("recall", ascending=False).to_string(index=False))