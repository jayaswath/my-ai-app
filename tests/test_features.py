from __future__ import annotations

import pandas as pd

from my_ai_app.learn.w4.w4_features import (
    CATEGORICAL_COLS,
    NUMERIC_COLS,
    TARGET,
    build_pipeline,
)
from my_ai_app.learn.w4.w4_ml_data import generate_orders


def test_generator_is_reproducible() -> None:
    """Same seed, same dockets."""
    pd.testing.assert_frame_equal(generate_orders(n=200), generate_orders(n=200))


def test_pipeline_survives_missing_values() -> None:
    """Pickup orders have no distance. The station must not stop."""
    df = generate_orders(n=500)
    assert df["distance_km"].isna().any()
    pipe = build_pipeline()
    pipe.fit(df[NUMERIC_COLS + CATEGORICAL_COLS], df[TARGET])
    assert len(pipe.predict(df[NUMERIC_COLS + CATEGORICAL_COLS])) == 500


def test_unseen_category_does_not_crash() -> None:
    """A new aggregator launches on Tuesday."""
    df = generate_orders(n=500)
    x, y = df[NUMERIC_COLS + CATEGORICAL_COLS], df[TARGET]
    pipe = build_pipeline()
    pipe.fit(x, y)
    unseen = x.head(1).copy()
    unseen["platform"] = "magicpin"
    assert len(pipe.predict(unseen)) == 1
