import time


def fetch_data(name: str, delay: float) -> str:
    """Simulate a slow API call."""
    print(f"Starting {name}...")
    time.sleep(delay)
    print(f"Finished {name}")
    return f"{name} result"


def main() -> None:
    """Run three fake API calls one after another."""
    start = time.perf_counter()

    fetch_data("call-1", 2)
    fetch_data("call-2", 2)
    fetch_data("call-3", 2)

    elapsed = time.perf_counter() - start
    print(f"Total: {elapsed:.2f}s")


if __name__ == "__main__":
    main()
