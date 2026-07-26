"""small utility functions for my_ai_app."""


def average(numbers: list[float]) -> float:
    """Return the mean of a list of numbers."""
    if not numbers:
        return 0.0
    return sum(numbers) / len(numbers)


def find_longest(words: list[str]) -> str | None:
    """Return the longest word in a list of words."""
    if not words:
        return None
    return max(words, key=len)


def count_words(text: str) -> dict[str, int]:
    """Return the mapping of each word"""
    count: dict[str, int] = {}
    for word in text.lower().split():
        count[word] = count.get(word, 0) + 1
    return count
