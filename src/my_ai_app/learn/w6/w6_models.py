import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import StratifiedKFold, cross_val_score
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.tree import DecisionTreeClassifier
from xgboost import XGBClassifier
from sklearn.metrics import roc_auc_score
from sklearn.model_selection import train_test_split

from my_ai_app.database import engine

NUM = ["item_count", "order_value", "distance_km", "kitchen_load", "riders_available"]
CAT = ["branch", "platform"]

df = pd.read_sql("SELECT * FROM ml_orders", engine)
X, y = df[NUM + CAT], df["is_late"]


def prep() -> ColumnTransformer:
    """The same prep station. Only the model on the end changes."""
    return ColumnTransformer([
        ("num", Pipeline([
            ("impute", SimpleImputer(strategy="median", add_indicator=True)),
            ("scale", StandardScaler()),
        ]), NUM),
        ("cat", Pipeline([
            ("impute", SimpleImputer(strategy="most_frequent")),
            ("encode", OneHotEncoder(handle_unknown="ignore", sparse_output=False)),
        ]), CAT),
    ])


models = {
    "logistic regression": LogisticRegression(max_iter=1000, class_weight="balanced", random_state=42),
    "decision tree":       DecisionTreeClassifier(max_depth=5, class_weight="balanced", random_state=42),
    "random forest":       RandomForestClassifier(n_estimators=200, class_weight="balanced",
                                                  random_state=42, n_jobs=-1),
    "XGBoost":             XGBClassifier(n_estimators=300, max_depth=4, learning_rate=0.1,
                                         scale_pos_weight=4.3, random_state=42,
                                         n_jobs=-1, eval_metric="logloss"),
}

cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
for name, m in models.items():
    pipe = Pipeline([("prep", prep()), ("model", m)])
    s = cross_val_score(pipe, X, y, cv=cv, scoring="roc_auc")
    print(f"{name:22s} AUC {s.mean():.3f}  (+/- {s.std():.3f})")

X_tr, X_te, y_tr, y_te = train_test_split(X, y, test_size=0.2, stratify=y, random_state=42)

for depth in [3, 5, None]:
    p = Pipeline([("prep", prep()),
                  ("model", DecisionTreeClassifier(max_depth=depth, class_weight="balanced", random_state=42))])
    p.fit(X_tr, y_tr)
    tr = roc_auc_score(y_tr, p.predict_proba(X_tr)[:, 1])
    te = roc_auc_score(y_te, p.predict_proba(X_te)[:, 1])
    print(f"max_depth={str(depth):5s}  train {tr:.3f}  test {te:.3f}")


p = Pipeline([("prep", prep()),
              ("model", RandomForestClassifier(n_estimators=200, class_weight="balanced",
                                               random_state=42, n_jobs=-1))])
p.fit(X_tr, y_tr)

names = p.named_steps["prep"].get_feature_names_out()
imp = p.named_steps["model"].feature_importances_

for n, i in sorted(zip(names, imp), key=lambda t: -t[1])[:8]:
    print(f"{n:36s} {i:.3f}")