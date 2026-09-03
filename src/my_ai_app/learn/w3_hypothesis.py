"""Hypothesis testing: is this difference real, or just a good week?"""

import numpy as np
from scipy import stats
from statsmodels.stats.power import TTestIndPower


def compare(a: np.ndarray, b: np.ndarray, label: str) -> None:
    """Run a t-test and report it honestly - difference AND p-value."""
    result = stats.ttest_ind(b, a)
    lift = (b.mean() - a.mean()) / a.mean() * 100

    verdict = "SIGNIFICANT" if result.pvalue < 0.05 else "not significant"
    print(f"\n--- {label} ---")
    print(f"  old mean: {a.mean():.1f}   new mean: {b.mean():.1f}   lift: {lift:+.1f}%")
    print(f"  p-value:  {result.pvalue:.4f}   -> {verdict}")


def main() -> None:
    rng = np.random.default_rng(seed=42)

    # 1. A real effect, big sample - should be detected
    old = rng.normal(loc=50, scale=8, size=200)
    new = rng.normal(loc=55, scale=8, size=200)
    compare(old, new, "Real 10% lift, n=200")

    # 2. The SAME real effect, tiny sample - probably missed
    old_small = rng.normal(loc=50, scale=8, size=8)
    new_small = rng.normal(loc=55, scale=8, size=8)
    compare(old_small, new_small, "Real 10% lift, n=8")

    # 3. No effect at all, big sample - should find nothing
    a = rng.normal(loc=50, scale=8, size=200)
    b = rng.normal(loc=50, scale=8, size=200)
    compare(a, b, "No real effect, n=200")

    print("\n--- How many orders do I need? ---")
    power = TTestIndPower()
    for effect, label in [(0.2, "small (2% lift)"), (0.5, "medium (5%)"), (0.8, "large (10%)")]:
        n = power.solve_power(effect_size=effect, alpha=0.05, power=0.8)
        print(f"  {label:<18} -> {n:.0f} orders per group")


if __name__ == "__main__":
    main()