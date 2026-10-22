from pathlib import Path

import joblib
import pandas as pd
from sklearn.model_selection import train_test_split

from my_ai_app.database import engine
from my_ai_app.learn.w7_layer1 import CAT, NUM, TARGET, build_pipe, build_prep

MODEL_FILE = Path("data/delay_model.joblib")

df = pd.read_sql("SELECT * FROM ml_orders", engine)
X, y = df[NUM + CAT], df[TARGET]
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, stratify=y, random_state=42
)

pipe = build_pipe(build_prep())
pipe.fit(X_train, y_train)

joblib.dump(pipe, MODEL_FILE)
print("saved:", MODEL_FILE, "-", MODEL_FILE.stat().st_size, "bytes")

loaded = joblib.load(MODEL_FILE)

same = (loaded.predict_proba(X_test)[:, 1] == pipe.predict_proba(X_test)[:, 1]).all()
print("loaded model gives identical predictions:", same)
print("first 5:", loaded.predict_proba(X_test)[:5, 1].round(3))