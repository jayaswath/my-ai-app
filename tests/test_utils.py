import pytest

from my_ai_app.utils import average, count_words, find_longest


def test_average_returns_mean() -> None:
    """average() computes the arithmatic mean"""
    assert average([2.0, 4.0, 6.0]) == 4.0


def test_average_empty_list_returns_zero() -> None:
    """average() returns 0.0 for an empty list"""
    assert average([]) == 0.0


@pytest.mark.parametrize(
    ("words", "expected"),
    [
        (["ai", "engineer"], "engineer"),
        (["a", "bb", "ccc"], "ccc"),
        ([], None),
        (["same", "size"], "same"),
    ],
)
def test_find_longest(words: list[str], expected: str | None) -> None:
    """find_longest() returns the longest word, or None when empty."""
    assert find_longest(words) == expected


@pytest.fixture
def sample_text() -> str:
    """Reusable text for word-counting tests."""
    return "the cat and the hat"


def test_count_words_counts_repeats(sample_text: str) -> None:
    """Repeated words are counted correctly."""
    assert count_words(sample_text)["the"] == 2


def test_count_words_is_case_insensitive() -> None:
    """Different casings collapse into one key."""
    assert count_words("The THE the") == {"the": 3}
