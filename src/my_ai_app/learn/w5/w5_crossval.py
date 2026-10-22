import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.model_selection import StratifiedKFold, cross_val_score
import numpy as np
from my_ai_app.database import engine
from sklearn.model_selection import TimeSeriesSplit
from sklearn.model_selection import GroupKFold

NUM = ["item_count", "order_value", "distance_km", "kitchen_load", "riders_available"]
CAT = ["branch", "platform"]

df = pd.read_sql("SELECT * FROM ml_orders", engine)
X = df[NUM + CAT]
y = df["is_late"]

numeric_steps = Pipeline([
    ("impute", SimpleImputer(strategy="median", add_indicator=True)),
    ("scale", StandardScaler()),
])
categorical_steps = Pipeline([
    ("impute", SimpleImputer(strategy="most_frequent")),
    ("encode", OneHotEncoder(handle_unknown="ignore", sparse_output=False)),
])
preprocessor = ColumnTransformer([
    ("num", numeric_steps, NUM),
    ("cat", categorical_steps, CAT),
])
pipe = Pipeline([
    ("prep", preprocessor),
    ("model", LogisticRegression(max_iter=1000, random_state=42)),
])

print(X.shape, y.shape)


cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
scores = cross_val_score(pipe, X, y, cv=cv, scoring="roc_auc")

print(scores.round(3))
print(f"mean {scores.mean():.3f}   std {scores.std():.3f}")

for i, (train_idx, test_idx) in enumerate(cv.split(X, y), start=1):
    print(f"fold {i}:  train {len(train_idx)}   test {len(test_idx)}   "
          f"late rate in test {y.iloc[test_idx].mean():.3f}")

for metric in ["roc_auc", "recall", "precision", "f1"]:
    s = cross_val_score(pipe, X, y, cv=cv, scoring=metric)
    print(f"{metric:10s} mean {s.mean():.3f}   std {s.std():.3f}")


df_sorted = df.sort_values("placed_at").reset_index(drop=True)
Xs = df_sorted[NUM + CAT]
ys = df_sorted["is_late"]

tscv = TimeSeriesSplit(n_splits=5)
ts_scores = cross_val_score(pipe, Xs, ys, cv=tscv, scoring="roc_auc")

print(ts_scores.round(3))
print(f"mean {ts_scores.mean():.3f}   std {ts_scores.std():.3f}")

for i, (tr, te) in enumerate(tscv.split(Xs), start=1):
    print(f"fold {i}:  train {len(tr):5d}  test {len(te):5d}   "
          f"train ends {df_sorted.loc[tr[-1], 'placed_at'].date()}   "
          f"test starts {df_sorted.loc[te[0], 'placed_at'].date()}")



groups = df["customer_id"]
gkf = GroupKFold(n_splits=5)
g_scores = cross_val_score(pipe, X, y, cv=gkf, groups=groups, scoring="roc_auc")

print(g_scores.round(3))
print(f"mean {g_scores.mean():.3f}   std {g_scores.std():.3f}")

print(f"{'method':20s} {'mean':>7s} {'std':>7s}")
print(f"{'StratifiedKFold':20s} {scores.mean():7.3f} {scores.std():7.3f}")
print(f"{'TimeSeriesSplit':20s} {ts_scores.mean():7.3f} {ts_scores.std():7.3f}")
print(f"{'GroupKFold':20s} {g_scores.mean():7.3f} {g_scores.std():7.3f}")