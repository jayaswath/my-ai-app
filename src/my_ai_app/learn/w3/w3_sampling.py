"""Sampling, the CLT, and how confident you're allowed to be."""

import numpy as np
from scipy import stats


def sample_means(population: np.ndarray, n: int, trials: int) -> np.ndarray:
    """Take many samples, return the mean of each."""
    rng = np.random.default_rng(seed=0)
    return np.array(
        [rng.choice(population, size=n, replace=False).mean() for _ in range(trials)]
    )


def confidence_interval(
    sample: np.ndarray, confidence: float = 0.95
) -> tuple[float, float]:
    """The range likely to contain the true population mean."""
    return stats.t.interval(
        confidence,
        df=len(sample) - 1,
        loc=np.mean(sample),
        scale=stats.sem(sample),
    )


def main() -> None:
    rng = np.random.default_rng(seed=42)

    # A realistic order-value population: right-skewed, not normal
    population = rng.exponential(scale=200, size=10_000)
    true_mean = population.mean()

    print(f"TRUE population mean: {true_mean:.1f}")
    print(f"population skew:      {stats.skew(population):.2f}  (0 = symmetric)")

    print("\n--- The CLT: sample means become normal ---")
    for n in [5, 30, 200]:
        means = sample_means(population, n=n, trials=500)
        print(f"  n={n:<4} skew of sample means: {stats.skew(means):+.2f}")

    print("\n--- More data = tighter interval ---")
    for n in [50, 200, 800]:
        sample = rng.choice(population, size=n, replace=False)
        low, high = confidence_interval(sample)
        print(f"  n={n:<4} mean {np.mean(sample):6.1f}  95% CI [{low:.1f}, {high:.1f}]  width {high - low:.1f}")


if __name__ == "__main__":
    main()