import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import StratifiedKFold, train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.model_selection import GridSearchCV
from my_ai_app.database import engine
from sklearn.metrics import classification_report
from sklearn.metrics import precision_score, recall_score

NUM = ["item_count", "order_value", "distance_km", "kitchen_load", "riders_available"]
CAT = ["branch", "platform"]

df = pd.read_sql("SELECT * FROM ml_orders", engine)
X = df[NUM + CAT]
y = df["is_late"]

X_tune, X_final, y_tune, y_final = train_test_split(
    X, y, test_size=0.2, stratify=y, random_state=42
)

print(f"tuning set {X_tune.shape}   locked drawer {X_final.shape}")

numeric_steps = Pipeline([
    ("impute", SimpleImputer(strategy="median", add_indicator=True)),
    ("scale", StandardScaler()),
])
categorical_steps = Pipeline([
    ("impute", SimpleImputer(strategy="most_frequent")),
    ("encode", OneHotEncoder(handle_unknown="ignore", sparse_output=False)),
])
pipe = Pipeline([
    ("prep", ColumnTransformer([
        ("num", numeric_steps, NUM),
        ("cat", categorical_steps, CAT),
    ])),
    ("model", LogisticRegression(max_iter=1000, random_state=42)),
])

print(pipe.named_steps.keys())

param_grid = {
    "model__C": [0.01, 0.1, 1.0, 10.0],
    "model__class_weight": [None, "balanced"],
    "prep__num__impute__strategy": ["median", "mean"],
}

for k, v in param_grid.items():
    print(f"{k:36s} {v}")
print("combinations:", 4 * 2 * 2)



cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
search = GridSearchCV(pipe, param_grid, cv=cv, scoring="roc_auc", n_jobs=-1)
search.fit(X_tune, y_tune)

print("best score:", round(search.best_score_, 3))
print("best params:")
for k, v in search.best_params_.items():
    print(f"   {k} = {v}")

best = search.best_estimator_
print("=== balanced, default 0.5 cut-off ===")
print(classification_report(y_final, best.predict(X_final),
                            target_names=["on time", "late"], digits=3))

results = pd.DataFrame(search.cv_results_)
cols = ["param_model__C", "param_model__class_weight",
        "param_prep__num__impute__strategy", "mean_test_score", "std_test_score"]
print(results[cols].sort_values("mean_test_score", ascending=False).head(8).to_string(index=False))



prob = best.predict_proba(X_final)[:, 1]
for cutoff in [0.70, 0.60, 0.50, 0.40, 0.30]:
    p = (prob >= cutoff).astype(int)
    print(f"{cutoff:.2f}  precision={precision_score(y_final, p):.3f}  "
          f"recall={recall_score(y_final, p):.3f}")