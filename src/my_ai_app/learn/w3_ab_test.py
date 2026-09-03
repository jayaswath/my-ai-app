"""A/B testing done properly - sample size first, analyse once."""

import numpy as np
from statsmodels.stats.power import NormalIndPower
from statsmodels.stats.proportion import proportion_effectsize, proportions_ztest


def sample_size_for_rates(baseline: float, target: float) -> float:
    """How many customers per group to reliably detect this change."""
    effect = proportion_effectsize(target, baseline)
    return NormalIndPower().solve_power(
        effect_size=effect, alpha=0.05, power=0.8, ratio=1.0
    )


def analyse(conv_a: int, n_a: int, conv_b: int, n_b: int, label: str) -> None:
    """Report a test honestly: the size of the effect AND whether it's real."""
    _, pvalue = proportions_ztest(count=[conv_b, conv_a], nobs=[n_b, n_a])
    rate_a, rate_b = conv_a / n_a, conv_b / n_b
    lift = (rate_b - rate_a) / rate_a * 100

    verdict = "SIGNIFICANT" if pvalue < 0.05 else "not significant"
    print(f"\n--- {label} ---")
    print(f"  A: {rate_a:.1%} ({conv_a}/{n_a})   B: {rate_b:.1%} ({conv_b}/{n_b})")
    print(f"  relative lift: {lift:+.1f}%   p={pvalue:.4f}  -> {verdict}")


def simulate_test(true_rate_a: float, true_rate_b: float, n: int, seed: int) -> None:
    """Run a fake A/B test where we KNOW the truth, and see if we detect it."""
    rng = np.random.default_rng(seed=seed)
    conv_a = int(rng.binomial(n, true_rate_a))
    conv_b = int(rng.binomial(n, true_rate_b))
    label = f"true rates {true_rate_a:.0%} vs {true_rate_b:.0%}, n={n} per group"
    analyse(conv_a, n, conv_b, n, label)


def main() -> None:
    print("--- STEP 1: how many customers do I need? ---")
    for baseline, target in [(0.20, 0.30), (0.20, 0.24), (0.20, 0.21)]:
        n = sample_size_for_rates(baseline, target)
        rel = (target - baseline) / baseline * 100
        print(f"  {baseline:.0%} -> {target:.0%} ({rel:+.0f}% relative): {n:.0f} per group")

    print("\n--- STEP 2: run the test ---")
    simulate_test(true_rate_a=0.20, true_rate_b=0.24, n=100, seed=1)
    simulate_test(true_rate_a=0.20, true_rate_b=0.24, n=1500, seed=1)
    simulate_test(true_rate_a=0.20, true_rate_b=0.20, n=1500, seed=1)


if __name__ == "__main__":
    main()