"""The whole first layer of machine learning, in one file.

Table  ->  X and y  ->  fill blanks  ->  encode words  ->  scale numbers
       ->  train    ->  predict      ->  score

Run:  uv run python -m my_ai_app.learn.w7_layer1
"""

from __future__ import annotations

import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report, confusion_matrix
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

from my_ai_app.database import engine

# ── SEGMENT 3 ──────────────────────────────────────────────────────────
# Three lists of NAMES. No data here yet - just words on paper.
# The shopping list, not the shopping.
NUM = ["item_count", "order_value", "distance_km", "kitchen_load", "riders_available"]
CAT = ["branch", "platform"]
TARGET = "is_late"


def load() -> pd.DataFrame:
    """SEGMENT 1+2 - pull the dockets off the shelf and look at them.

    read_sql runs the query on Postgres and hands back a DataFrame.
    dtypes tells you which columns are numbers and which are words -
    that is what decides NUM vs CAT. Careful: order_id and customer_id
    are int64 but they are NAMES, not quantities. They stay out.
    """
    df = pd.read_sql("SELECT * FROM ml_orders", engine)
    print("table:", df.shape)
    print(df.dtypes.to_string())
    return df


def split_x_y(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.Series]:
    """SEGMENT 4+5 - facts in one pile, answers in the other.

    A LIST inside df[...] gives a DataFrame (many columns).
    A single STRING gives a Series (one column).
    Then count the blanks, because blanks crash sklearn, and count the
    categories, because that tells you how many columns one-hot will make.
    """
    X = df[NUM + CAT]          # list  -> DataFrame, 7 columns
    y = df[TARGET]             # string -> Series

    print("\nX:", X.shape, " y:", y.shape)
    print("\nblanks per column:")
    print(X.isna().sum().to_string())
    print("\nbranch:", X["branch"].nunique(), "values   platform:", X["platform"].nunique(), "values")
    return X, y


def build_prep() -> ColumnTransformer:
    """SEGMENTS 6+7+8+9 - the prep card. Three fixes, packed into one object.

    NUMBERS go down one path:
      impute  - 637 distances are blank because those were pickups. Fill each
                with the median (2.64 km). add_indicator sticks a 0/1 flag on
                saying "this was blank" - because blank MEANS pickup, and
                pickups are rarely late. 5 columns in, 6 out.
      scale   - order_value runs in hundreds, item_count runs 1-8. The model
                would hear the big numbers louder just because rupees are
                bigger units. Scaling rewrites every column as "how many
                spreads from average", so all columns speak one language.

    WORDS go down the other path:
      impute  - fill blanks with the commonest value. "median" is meaningless
                for text, so most_frequent.
      encode  - the model does arithmetic and cannot multiply "Koramangala".
                One tick-box per value, exactly one ticked per row.
                4 branches + 3 platforms = 7 columns.
                handle_unknown="ignore" means a new branch gives all zeros
                instead of crashing.

    ColumnTransformer is the router: it sends each group down its own path
    and glues the results back side by side.  6 + 7 = 13 columns out.
    """
    numeric_steps = Pipeline([
        ("impute", SimpleImputer(strategy="median", add_indicator=True)),
        ("scale", StandardScaler()),
    ])
    categorical_steps = Pipeline([
        ("impute", SimpleImputer(strategy="most_frequent")),
        ("encode", OneHotEncoder(handle_unknown="ignore", sparse_output=False)),
    ])
    return ColumnTransformer([
        ("num", numeric_steps, NUM),      # "num" is my choice - it becomes the num__ prefix
        ("cat", categorical_steps, CAT),
    ])


def build_pipe(prep: ColumnTransformer) -> Pipeline:
    """SEGMENT 10a - prep card plus model, on one object.

    This is what makes leakage impossible by accident: when you call
    fit(X_train, y_train), every step inside only ever sees training rows.
    The medians and the scaling averages are learned from training data
    alone, then merely APPLIED to the test data.

    class_weight="balanced" tells it a late order matters as much as an
    on-time one, even though only 19% are late. Without it the model stays
    quiet and misses almost everything.
    """
    return Pipeline([
        ("prep", prep),
        ("model", LogisticRegression(max_iter=1000, class_weight="balanced", random_state=42)),
    ])


def main() -> None:
    df = load()
    X, y = split_x_y(df)

    prep = build_prep()
    print("\nafter prep:", prep.fit_transform(X).shape, "  (was", X.shape[1], "columns)")
    print(list(prep.get_feature_names_out()))

    # SEGMENT 10b - hide 20% so there is something honest to mark against.
    # stratify=y keeps the same 19% late rate on both sides.
    # random_state=42 means the same split every run.
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, stratify=y, random_state=42
    )
    print(f"\ntrain {X_train.shape}   test {X_test.shape}")

    # SEGMENT 10c - THIS is where everything actually runs.
    # Everything above only described what to do.
    pipe = build_pipe(prep)
    pipe.fit(X_train, y_train)

    # SEGMENT 11 - the model outputs a NUMBER between 0 and 1, not a word.
    # [:, 1] keeps the "chance of late" column.
    # predict() is just predict_proba()[:, 1] >= 0.5 - that 0.5 is a
    # default nobody checked against this problem.
    prob = pipe.predict_proba(X_test)[:, 1]
    pred = pipe.predict(X_test)
    print("\nfirst 8 scores: ", prob[:8].round(3))
    print("first 8 verdicts:", pred[:8])

    # SEGMENT 12 - mark the exam. FIRST time y_test is touched.
    # Order matters: truth first, guesses second.
    print("\n", confusion_matrix(y_test, pred), sep="")
    print("   rows = truth, columns = what the model said\n")
    print(classification_report(y_test, pred, target_names=["on time", "late"], digits=3))

    # Read the weights back. Sign = direction, size = strength.
    # Trailing underscore means "learned during fit".
    names = pipe.named_steps["prep"].get_feature_names_out()
    coefs = pipe.named_steps["model"].coef_[0]
    print("what it learned (biggest effect first):")
    for n, c in sorted(zip(names, coefs), key=lambda t: -abs(t[1])):
        print(f"  {n:36s} {c:+.3f}")


if __name__ == "__main__":
    main()