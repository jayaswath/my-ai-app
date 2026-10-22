"""Week 3 capstone: a full A/B analysis, start to finish."""

import numpy as np
import pandas as pd
from scipy import stats
from statsmodels.stats.power import NormalIndPower
from statsmodels.stats.proportion import proportion_effectsize, proportions_ztest


BASELINE = 0.22
TARGET = 0.26


def required_sample_size(baseline: float, target: float) -> int:
    """STEP 2: how many customers per group before we can trust the answer."""
    effect = proportion_effectsize(target, baseline)
    n = NormalIndPower().solve_power(
        effect_size=effect, alpha=0.05, power=0.8, ratio=1.0
    )
    return int(np.ceil(n))


def run_experiment(n: int, true_a: float, true_b: float, seed: int) -> pd.DataFrame:
    """STEP 3+4: assign customers randomly, record whether they ordered."""
    rng = np.random.default_rng(seed=seed)

    group = rng.choice(["A", "B"], size=2 * n)
    rate = np.where(group == "A", true_a, true_b)
    ordered = rng.binomial(1, rate)

    return pd.DataFrame({"group": group, "ordered": ordered})


def report(df: pd.DataFrame) -> None:
    """STEP 5: the write-up a decision-maker actually needs."""
    summary = df.groupby("group")["ordered"].agg(["count", "sum", "mean"])
    print("\n--- Results ---")
    print(summary.round(4))

    a = df[df["group"] == "A"]["ordered"]
    b = df[df["group"] == "B"]["ordered"]

    _, pvalue = proportions_ztest(
        count=[int(b.sum()), int(a.sum())],
        nobs=[len(b), len(a)],
    )

    rate_a, rate_b = a.mean(), b.mean()
    abs_lift = rate_b - rate_a
    rel_lift = abs_lift / rate_a * 100

    print("\n--- Verdict ---")
    print(f"  control (₹40 fee):  {rate_a:.2%}")
    print(f"  variant (₹25 fee):  {rate_b:.2%}")
    print(f"  absolute lift:      {abs_lift:+.2%} points")
    print(f"  relative lift:      {rel_lift:+.1f}%")
    print(f"  p-value:            {pvalue:.4f}")

    if pvalue < 0.05:
        print("  -> SIGNIFICANT: the fee change moved the needle")
    else:
        print("  -> NOT SIGNIFICANT: no evidence the fee change helped")


def main() -> None:
    print("--- STEP 1: metric ---")
    print("  completion rate = orders placed / app opens")

    n = required_sample_size(BASELINE, TARGET)
    print("\n--- STEP 2: sample size ---")
    print(f"  need {n} customers per group ({2 * n} total)")
    print(f"  at ~200 app opens/day, that is {2 * n / 200:.0f} days")

    print("\n=== SCENARIO 1: the fee change genuinely works ===")
    df = run_experiment(n=n, true_a=0.22, true_b=0.26, seed=7)
    report(df)

    print("\n=== SCENARIO 2: the fee change does nothing ===")
    df = run_experiment(n=n, true_a=0.22, true_b=0.22, seed=7)
    report(df)

    print("\n=== SCENARIO 3: real effect, but we stopped early ===")
    df = run_experiment(n=n // 4, true_a=0.22, true_b=0.26, seed=7)
    report(df)


if __name__ == "__main__":
    main()