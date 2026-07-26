from my_ai_app.utils import average, count_words, find_longest


def greet(name: str) -> str:
    """Return a greeting for the given name."""
    return f"Hello, {name}!"


def add(a: int, b: int) -> int:
    """Return the sum of two numbers."""
    return a + b


if __name__ == "__main__":
    print(greet("AI Engineer"))

    result = add(5, 3)
    print(f"The sum is: {result}")

    print(average([8.0, 9.5, 7.5]))
    print(find_longest(["ai", "engineer", "roadmap"]))
    print(count_words("the cat and the hat"))
