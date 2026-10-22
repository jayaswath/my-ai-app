"""Descriptive stats on real order data - is 'typical' actually typical?"""

import numpy as np


def describe(orders: np.ndarray, label: str) -> None:
    """Print the full picture, not just one misleading number."""
    print(f"\n--- {label} ---")
    print(f"mean:   {np.mean(orders):.1f}")
    print(f"median: {np.median(orders):.1f}")
    print(f"std:    {np.std(orders):.1f}")
    print(f"90th percentile: {np.percentile(orders, 90):.1f}")


def main() -> None:
    normal_orders = np.array([120, 250, 90, 300, 120, 150, 200, 110, 180, 140])
    with_outlier = np.append(normal_orders, 35000)

    describe(normal_orders, "Without the catering order")
    describe(with_outlier, "With the catering order")


if __name__ == "__main__":
    main()