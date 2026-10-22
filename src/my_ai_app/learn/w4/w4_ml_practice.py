import pandas as pd
from my_ai_app.database import engine
from sklearn.model_selection import train_test_split
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report, confusion_matrix, roc_auc_score
from sklearn.metrics import precision_score, recall_score, f1_score

df = pd.read_sql("SELECT * FROM ml_orders", engine)
print(df.shape)
print(df.head())

NUM = ["item_count", "order_value", "distance_km", "kitchen_load", "riders_available"]
CAT = ["branch", "platform"]

X = df[NUM + CAT]
y = df["is_late"]

print(X.shape)
print(y.value_counts())



X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, stratify=y, random_state=42
)

print(X_train.shape, X_test.shape)
print(y_train.mean(), y_test.mean())



numeric_steps = Pipeline([
    ("impute", SimpleImputer(strategy="median", add_indicator=True)),
    ("scale", StandardScaler()),
])


print(numeric_steps)

categorical_steps = Pipeline([
    ("impute", SimpleImputer(strategy="most_frequent")),
    ("encode", OneHotEncoder(handle_unknown="ignore", sparse_output=False)),
])

print(categorical_steps)

preprocessor = ColumnTransformer([
    ("num", numeric_steps, NUM),
    ("cat", categorical_steps, CAT),
])

print(preprocessor)




pipe = Pipeline([
    ("prep", preprocessor),
    ("model", LogisticRegression(max_iter=1000, random_state=42)),
])

print(pipe)

pipe.fit(X_train, y_train)
print("trained")

names = pipe.named_steps["prep"].get_feature_names_out()
coefs = pipe.named_steps["model"].coef_[0]

for name, coef in sorted(zip(names, coefs), key=lambda t: -abs(t[1])):
    print(f"{name:30s} {coef:+.3f}")

prob = pipe.predict_proba(X_test)[:, 1]
pred = pipe.predict(X_test)

print(prob[:10].round(3))
print(pred[:10])



print(confusion_matrix(y_test, pred))
print(classification_report(y_test, pred, target_names=["on time", "late"], digits=3))
print("ROC AUC:", round(roc_auc_score(y_test, prob), 3))



for cutoff in [0.50, 0.40, 0.30, 0.25, 0.20, 0.15, 0.10]:
    p2 = (prob >= cutoff).astype(int)
    print(f"{cutoff:.2f}  precision={precision_score(y_test, p2):.2f}"
          f"  recall={recall_score(y_test, p2):.2f}"
          f"  F1={f1_score(y_test, p2):.2f}")

CUTOFF = 0.20
final_pred = (prob >= CUTOFF).astype(int)

print(confusion_matrix(y_test, final_pred))
print(classification_report(y_test, final_pred, target_names=["on time", "late"], digits=3))