import mlflow
import mlflow.sklearn
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import f1_score, precision_score, recall_score, roc_auc_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

from my_ai_app.database import engine

mlflow.set_tracking_uri("file:./mlruns")
mlflow.set_experiment("delivery-delay")

print("tracking to ./mlruns")


NUM = ["item_count", "order_value", "distance_km", "kitchen_load", "riders_available"]
CAT = ["branch", "platform"]

df = pd.read_sql("SELECT * FROM ml_orders", engine)
X, y = df[NUM + CAT], df["is_late"]
X_tr, X_te, y_tr, y_te = train_test_split(X, y, test_size=0.2, stratify=y, random_state=42)


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


print(X_tr.shape, X_te.shape)