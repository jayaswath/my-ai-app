"""Conditional probability and Bayes, on kitchen problems."""


def bayes(p_b_given_a: float, p_a: float, p_b_given_not_a: float) -> float:
    """Flip a conditional probability using Bayes' theorem."""
    p_not_a = 1 - p_a
    p_b = (p_b_given_a * p_a) + (p_b_given_not_a * p_not_a)
    return (p_b_given_a * p_a) / p_b


def expected_value(outcomes: list[float], probabilities: list[float]) -> float:
    """Probability-weighted average of all outcomes."""
    return sum(o * p for o, p in zip(outcomes, probabilities, strict=True))


def main() -> None:
    """Work through three kitchen probability questions."""
    # 1. A complaint arrives. Was the order late?
    print("--- Complaint analysis ---")
    for late_rate in [0.20, 0.05, 0.02]:
        result = bayes(p_b_given_a=0.60, p_a=late_rate, p_b_given_not_a=0.05)
        print(f"  if {late_rate:.0%} of orders are late -> {result:.1%} of complaints are late orders")

    # 2. Tomorrow's prep target
    print("\n--- Demand forecast ---")
    plates = [30.0, 50.0, 80.0]
    chances = [0.2, 0.5, 0.3]
    print(f"  prep for {expected_value(plates, chances):.0f} plates")


if __name__ == "__main__":
    main()