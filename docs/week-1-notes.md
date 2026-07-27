# AI Engineer Roadmap — Week 1 Notes
### Production Python Foundations

**Days 1–7 · `my-ai-app`**

From an empty folder to a containerised, typed, tested, CI-guarded web service.

---

## How to use these notes

Each day follows the same nine sections:

| Section | What it answers |
|---|---|
| **1. What it is** | Plain-English definition |
| **2. Why we use it** | The problem it solves |
| **3. Where you will use it** | In this roadmap, and in KitchenOS |
| **4. Setup** | Installation and config |
| **5. Syntax reference** | Every keyword, explained |
| **6. Commands** | Copy-paste ready |
| **7. What breaks** | Mistakes and traps |
| **8. What you built** | Your actual Day-N output |
| **9. Quick recall** | Five questions to test yourself |

At the end: cheat sheets, an error dictionary of the problems you actually hit, a glossary,
your own questions answered, and a one-page-per-day summary for revision.

---

## Week 1 at a glance

```
Day 1  ──  Environment      uv, pyproject.toml, package structure
Day 2  ──  Version control  Git, GitHub, .gitignore
Day 3  ──  Code quality     type hints, ruff, mypy
Day 4  ──  Testing          pytest, parametrize, fixtures
Day 5  ──  Concurrency      async / await, asyncio, httpx
Day 6  ──  The service      FastAPI, Pydantic, dependency injection
Day 7  ──  Shipping         Docker, GitHub Actions CI
```

**Deliverable:** a Dockerised FastAPI service with 15 passing tests and green CI.

---
---

# DAY 1 — Environment & Project Structure

> **One line:** Give every project its own sealed box of Python and libraries.

---

## 1. What it is

A **virtual environment** is a private Python installation belonging to one project only.

**`uv`** is the tool that creates and manages it — a modern replacement for `pip` + `venv`,
roughly 10× faster.

**`pyproject.toml`** is the settings file that records what your project needs, so anyone can
rebuild your exact setup with one command.

---

## 2. Why we use it

**The problem:**

```
Project A needs pandas 1.5
Project B needs pandas 2.2

Install one globally  →  the other breaks
```

**The bigger problem** — "works on my machine." Without a recorded dependency list, your app
runs on your laptop and dies on the server, because the server has different library versions.

| Without | With |
|---|---|
| Libraries shared across all projects | Isolated per project |
| Versions drift silently | Locked in `uv.lock` |
| Setup instructions live in your head | One command rebuilds everything |

---

## 3. Where you will use it

| When | Use |
|---|---|
| **Every project, forever** | This is not optional tooling |
| **Week 7** | PyTorch + CUDA versions are notoriously version-sensitive |
| **Week 14** | Fine-tuning stacks (`peft`, `bitsandbytes`, `transformers`) must match exactly |
| **Day 7** | Docker reads `pyproject.toml` and `uv.lock` to build your image |
| **KitchenOS** | Your Python 3.14 vs Railway's 3.11 mismatch was exactly this problem |

---

## 4. Setup

**Install uv:**

```powershell
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

Close and reopen the terminal, then:

```powershell
uv --version
```

**Create the project:**

```powershell
uv init my-ai-app
cd my-ai-app
code .
```

---

## 5. Syntax reference

### `pyproject.toml`

```toml
[project]
name = "my-ai-app"
version = "0.1.0"
description = "My first production Python service"
requires-python = ">=3.11"
dependencies = []

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"
```

| Line | Meaning |
|---|---|
| `[project]` | A **section header**. TOML groups settings in square brackets. |
| `name` | Project name — used if you ever publish it |
| `version` | Bumped as you make changes |
| `requires-python = ">=3.11"` | Refuses to install on older Python, with a clear error |
| `dependencies = []` | Your libraries. `[]` = empty list. **Never edit by hand.** |
| `[build-system]` | Declares this an installable package, not loose scripts |
| `hatchling` | The build backend that packages your code |

> **Why `[build-system]` matters:** without it, `tests/` cannot import from `src/`.
> This is what makes `from my_ai_app.utils import average` work.

### Folder structure

```
my-ai-app/
├── src/
│   └── my_ai_app/          ← underscores, not hyphens
│       ├── __init__.py     ← empty, but must exist
│       └── main.py
├── tests/
├── pyproject.toml
├── uv.lock                 ← auto-generated, always commit it
└── .gitignore
```

| Item | Why |
|---|---|
| `src/` layout | Prevents accidentally importing from the working directory instead of the installed package |
| `my_ai_app` | Python cannot import names containing hyphens |
| `__init__.py` | Tells Python "this folder is a package." Stays empty forever. |
| `uv.lock` | Exact versions of every dependency **and their dependencies** |

### A basic module

```python
def greet(name: str) -> str:
    """Return a greeting for the given name."""
    return f"Hello, {name}!"


if __name__ == "__main__":
    print(greet("AI Engineer"))
```

| Part | Meaning |
|---|---|
| `name: str` | **Type hint** — this parameter should be text |
| `-> str` | This function returns text |
| `"""..."""` | **Docstring** — documentation inside the code |
| `f"...{name}..."` | **f-string** — the `{}` is replaced by the variable's value |
| `if __name__ == "__main__":` | Run this **only** when the file is executed directly, not when imported |

---

## 6. Commands

```powershell
uv init <name>              # create a new project
uv add <package>            # install a library AND record it
uv add --dev <package>      # a dev tool — never ships to production
uv sync                     # rebuild the environment from the lockfile
uv run python -m my_ai_app.main   # run a module inside the environment
uv run <any-command>        # run anything inside the environment
```

### The `-m` pattern

```
src/my_ai_app/fetch_urls.py   →   uv run python -m my_ai_app.fetch_urls
```

Drop `src/`, replace slashes with dots, remove `.py`.

`-m` runs the file **as a module inside your installed package**, which is why imports resolve.

---

## 7. What breaks

### ❌ Calling a function before it is defined

```python
if __name__ == "__main__":
    result = add(5, 3)      # 💥 NameError — add doesn't exist yet

def add(a: int, b: int) -> int:
    return a + b
```

**Python reads top to bottom and executes as it goes.** `def` is an *action*, not a
declaration. The function exists only from the moment Python reaches that line.

> **Rule: define everything first, run things last.**
> The `if __name__ == "__main__":` block always goes at the bottom.

### ❌ Hyphens in the package folder

`my-ai-app/` cannot be imported. Must be `my_ai_app/`.

### ❌ Editing `dependencies` by hand

Use `uv add`. It resolves versions and updates `uv.lock` at the same time.

### ⚠️ Forgetting `[build-system]`

Everything works until Day 4, when tests suddenly cannot import your code.

---

## 8. What you built

- `my-ai-app` project with isolated `.venv`
- `pyproject.toml` with Python version pinned to 3.11+
- `src/` layout with a proper importable package
- `greet()` and `add()` — your first typed functions
- Output: `Hello, AI Engineer!` / `The sum is: 8`

---

## 9. Quick recall

1. Why must `__init__.py` exist if it is always empty?
2. What is the difference between `pyproject.toml` and `uv.lock`?
3. Why does `add(5, 3)` fail when `def add` is below it?
4. What does `-m` do that a direct file path does not?
5. Why `--dev` for pytest but not for fastapi?

---
---

# DAY 2 — Git & GitHub

> **One line:** A time machine for your code, plus a public backup that doubles as your CV.

---

## 1. What it is

**Git** records snapshots of your project. Every snapshot ("commit") is recoverable forever.

**GitHub** is the internet copy — backup, collaboration, and your portfolio.

They are **not** the same thing. Git works entirely offline; GitHub is one place to store it.

---

## 2. Why we use it

| Problem | What Git gives you |
|---|---|
| "I broke it and can't undo" | Roll back to any commit |
| "What changed and when?" | Full annotated history |
| "I want to try something risky" | Branch, experiment, throw it away |
| "My laptop died" | Everything is on GitHub |
| "Prove you can build things" | A public, dated commit history |

**For you specifically:** recruiters open your GitHub before your CV. 21 weeks of daily
commits is a stronger signal than any certificate.

---

## 3. Where you will use it

Every single day of this roadmap, and every project after it.

| When | Use |
|---|---|
| End of every session | `add → commit → push` |
| **Week 4+** | Branches for ML experiments you may throw away |
| **Day 7** | GitHub Actions triggers on every push |
| **KitchenOS** | Railway auto-deploys when you push to `main` |

---

## 4. Setup

```powershell
git config --global user.name "Your Name"
git config --global user.email "your@email.com"
```

Use the **same email** as your GitHub account — that is how commits link to your profile.

```powershell
git config --global --list       # verify
```

---

## 5. Syntax reference

### The three zones

```
  Working Directory        Staging Area           Repository
   (your edits)      →     (selected)      →     (saved forever)
                  git add              git commit
```

The middle step exists so you can commit **one logical change** instead of dumping
everything at once.

### The core loop

```powershell
git status                          # what changed?
git add .                           # stage everything
git add src/my_ai_app/utils.py      # stage one file
git commit -m "feat: add utils"     # save permanently
git push                            # upload to GitHub
```

### Conventional commits

```
feat:      a new feature
fix:       a bug fix
docs:      documentation
test:      tests
refactor:  restructuring, no behaviour change
chore:     config, dependencies, tooling
```

**Write for future-you.** `"update"` tells you nothing in three months.
`"fix: handle empty input in greet()"` tells you everything.

### `.gitignore`

```gitignore
# Virtual environment
.venv/
venv/

# Python cache
__pycache__/
*.pyc

# Secrets — NEVER commit these
.env
*.key

# Tool caches
.mypy_cache/
.ruff_cache/
.pytest_cache/

# Editor / OS
.vscode/
.DS_Store
```

| Pattern | Meaning |
|---|---|
| `.venv/` | Trailing `/` = the whole folder |
| `*.pyc` | `*` = wildcard: any file ending in `.pyc` |
| `#` | A comment |

> ⚠️ **This is a security control, not housekeeping.**
> From Week 11 you will have API keys in `.env`. Committed to a public repo, bots find them
> within minutes and drain your account. This happens to people daily.

### Branching

```powershell
git checkout -b feat/new-idea    # create and switch
# ... make changes, commit ...
git checkout main                # switch back
git merge feat/new-idea          # bring changes in
git branch -d feat/new-idea      # delete when done
```

### Connecting to GitHub

```powershell
git remote add origin https://github.com/USER/REPO.git
git branch -M main
git push -u origin main
```

| Part | Meaning |
|---|---|
| `remote` | A server copy of the repository |
| `origin` | Conventional nickname for your main remote |
| `-M main` | Rename the branch to `main` (GitHub's default) |
| `-u` | Remember this destination — future pushes are just `git push` |

---

## 6. Commands

```powershell
git status                     # current state
git log --oneline              # compact history
git diff                       # unstaged changes
git diff --staged              # staged changes
git remote -v                  # where does this push to?
git rev-parse --show-toplevel  # WHICH REPO AM I IN?
git checkout -- <file>         # discard changes to a file
git reset HEAD~1               # undo last commit, keep changes
```

---

## 7. What breaks

### ❌ Running Git in the wrong folder

**This happened to you.** A stray `.git` existed at `C:\Users\Lenovo`, so `git add .` was
trying to index your entire home directory.

**Why:** if Git finds no repo in the current folder, it walks **upward** until it finds one.

**The habit that prevents it — two commands before any commit:**

```powershell
git rev-parse --show-toplevel   # which repo am I actually in?
git status                       # what am I about to commit?
```

### ❌ `git push --force`

The one command that can genuinely destroy history. Never use it on a shared branch.
Plain `git push` cannot.

### ❌ Committing secrets

Once pushed to a public repo, assume the key is compromised — even if you delete it later.
It stays in the history. **Rotate the key, don't just remove the file.**

### ⚠️ `index.lock` left behind

An interrupted Git command leaves a lock file that blocks everything. See the Error
Dictionary at the end.

---

## 8. What you built

- `my-ai-app` repository, live at `github.com/jayaswath/my-ai-app`
- `.gitignore` protecting secrets and caches
- First commit: `feat: initial project setup with uv`
- Diagnosed and removed a stray repository at your home folder
- **Also learned:** how to read `src refspec main does not match any` (it means *no commits exist*)

---

## 9. Quick recall

1. What is the difference between Git and GitHub?
2. Why does the staging area exist — why not commit directly?
3. What does Git do when there is no `.git` in the current folder?
4. Why is committing a `.env` file worse than it first appears?
5. What does `-u` do in `git push -u origin main`?

---
---

# DAY 3 — Type Hints, Ruff & Mypy

> **One line:** Labels on your data, plus two tools that read them and catch your mistakes.

---

## 1. What it is

**Type hints** declare what kind of data goes into and out of a function.

**Ruff** is a linter *and* formatter — finds bugs and style problems, fixes most automatically.

**Mypy** reads your type hints and verifies you are honouring them.

```
Ruff  →  checks STYLE and obvious bugs
Mypy  →  checks LOGIC against your type hints
```

---

## 2. Why we use it

Python does not enforce type hints at runtime. `add("5", "3")` still runs and returns `"53"`.

**The hints exist so tools can catch that before you run anything.**

| Without | With |
|---|---|
| Bug found after a 20-minute training run | Bug found in 0.2 seconds |
| Editor autocomplete guesses | Editor knows exactly what's available |
| "What does this function return?" — read the code | It's in the signature |
| Formatting arguments in code review | Zero — ruff decides |

---

## 3. Where you will use it

| When | Use |
|---|---|
| **Day 6** | FastAPI generates your entire API documentation from type hints |
| **Day 6** | Pydantic uses them to validate incoming JSON |
| **Week 6** | Catching a function that returns a DataFrame when you expected an array |
| **Week 11** | Structured LLM outputs are defined as typed Pydantic models |
| **Every day** | Ruff runs before every commit |

> Type hints are not a "nice to have" in this stack. FastAPI and Pydantic are **built on them.**

---

## 4. Setup

```powershell
uv add --dev ruff mypy
```

**Config** — in `pyproject.toml`:

```toml
[tool.ruff]
line-length = 88
target-version = "py311"

[tool.ruff.lint]
select = ["E", "F", "I", "N", "UP", "B"]

[tool.mypy]
python_version = "3.11"
strict = true
```

| Setting | Meaning |
|---|---|
| `line-length = 88` | Wrap past 88 characters — the community standard |
| `select = [...]` | Which rule families to enforce |
| `strict = true` | Mypy's harshest mode. Painful for a week, then free safety. |

**Rule families:**

| Code | Catches |
|---|---|
| `E` | Style errors — spacing, indentation |
| `F` | **Real bugs** — undefined names, unused imports |
| `I` | Unsorted imports (auto-fixed) |
| `N` | Bad naming — `myVar` instead of `my_var` |
| `UP` | Outdated syntax — modernises it |
| `B` | Common Python traps |

---

## 5. Syntax reference

### Basic annotations

```python
name: str = "Swath"
count: int = 5
score: float = 9.5
active: bool = True
```

### Containers

```python
scores: list[float] = [8.1, 9.4]
config: dict[str, int] = {"epochs": 10}
point: tuple[float, float] = (1.5, 2.5)
tags: set[str] = {"ai", "ml"}
```

| Syntax | Meaning |
|---|---|
| `list[float]` | A list containing floats |
| `dict[str, int]` | Keys are text, values are whole numbers |
| `tuple[float, float]` | Exactly two floats, in order |

### The union — `|`

```python
def find_user(user_id: int) -> str | None:
    """Return the username, or None if not found."""
    ...
```

`str | None` = **either** text **or** nothing.

> You will use this constantly. Any function that can fail returns `None`, and mypy will
> demand you declare it.

### Functions

```python
def average(numbers: list[float]) -> float:
    """Return the mean. Returns 0.0 if the list is empty."""
    if not numbers:
        return 0.0
    return sum(numbers) / len(numbers)
```

| Detail | Why |
|---|---|
| `-> float` | Declares the return type |
| `return 0.0` **not** `return 0` | You promised a float. Mypy strict rejects the int. |
| `if not numbers:` | An empty list is "falsy" — cleaner than `len(numbers) == 0` |

### Empty containers need annotations

```python
counts: dict[str, int] = {}     # ✅ mypy strict requires this
counts = {}                     # ❌ nothing to infer from
```

### `None` return

```python
def main() -> None:
    """Does something, returns nothing."""
    print("done")
```

---

## 6. Commands

```powershell
uv run ruff check .              # find problems
uv run ruff check . --fix        # find AND fix
uv run ruff format .             # format all files
uv run ruff format --check .     # report bad formatting, change nothing (for CI)
uv run mypy src                  # type-check
```

**The daily sequence:**

```powershell
uv run ruff check . --fix
uv run ruff format .
uv run mypy src
uv run pytest
```

---

## 7. What breaks

### ❌ Lying about return types

```python
def get_name() -> str:
    return 42          # 💥 mypy: Incompatible return value type
```

Python runs this happily and breaks somewhere far away later. Mypy catches it before
execution.

### ❌ Forgetting `| None`

```python
def find_longest(words: list[str]) -> str:
    if not words:
        return None    # 💥 mypy: Incompatible return value
```

Fix the signature to `-> str | None`.

### ❌ `""` when you mean `None`

**This was your actual Day-4 bug.**

```python
return ""      # "the longest word is an empty string" — a real answer
return None    # "there is no answer"
```

Different meanings, different bugs downstream. Something checks `if result:` and silently
skips valid data.

> **Week 12 version of the same trap:** did the retriever find *no* documents (`None`),
> or find a document that *is* empty (`""`)? Different problems, different fixes.

### ⚠️ Mypy strict is loud at first

Expect 20+ errors on an existing project. Fix them once; they don't come back.

---

## 8. What you built

- Ruff and mypy configured in strict mode
- `utils.py` — three fully typed functions:
  - `average(numbers: list[float]) -> float`
  - `find_longest(words: list[str]) -> str | None`
  - `count_words(text: str) -> dict[str, int]`
- Watched ruff auto-delete unused imports
- Watched mypy catch a function returning `42` where it promised `str`

---

## 9. Quick recall

1. Does Python enforce type hints at runtime? Then what is the point?
2. What does `str | None` mean, and when do you need it?
3. Why does `counts: dict[str, int] = {}` need the annotation when `counts = {"a": 1}` doesn't?
4. What is the difference between `ruff check` and `ruff format`?
5. Why does CI use `ruff format --check` instead of `ruff format`?

---
---

# DAY 4 — pytest

> **One line:** Code that checks your code, automatically.

---

## 1. What it is

Right now you verify your work by running a file and reading the output with your eyes.
That works for 3 functions. It collapses at 30.

A **test** is a small function that calls your code with a known input and asserts a known
answer.

```
Manual testing     →  You, clicking, remembering, missing things
pytest             →  One command, every rule re-verified, 0.3 seconds
```

---

## 2. Why we use it

| Problem | What pytest gives you |
|---|---|
| "Did my change break something else?" | Answer in under a second |
| Only checking what you remember to check | Every rule checked, every time |
| Edge cases discovered by users | Edge cases pinned down by you |
| Afraid to touch old code | Freedom to refactor |

**The deepest reason:** tests are *decisions, written down.*

When you assert `find_longest([]) is None`, you have permanently decided that empty input
returns nothing — and no future edit can silently change that.

**Honest note:** pytest is not mandatory. Your code runs without it. But "no tests" is not
"no testing" — it means *manual* testing, by you, slowly, incompletely. The cost appears
later, when you start avoiding code you're afraid to touch. That is how projects quietly
stop improving.

---

## 3. Where you will use it

| When | Use |
|---|---|
| **Now** | Utility functions and API endpoints |
| **Week 6** | Data leakage, shape mismatches in ML pipelines |
| **Week 12** | Fixtures that spin up a temporary vector database |
| **Week 18** | **LLM eval suites** — 100 questions, known-good answers, scored automatically |
| **KitchenOS** | GST math, dish profit, stock deduction — where bugs cost real rupees |

> **Week 18 is why this matters most.** LLMs are non-deterministic — the same prompt gives
> different output. "Run it and look" stops working. Your eval suite *is* a pytest suite:
> same `assert`, same `parametrize`, same fixtures you are learning now.

---

## 4. Setup

```powershell
uv add --dev pytest pytest-cov
```

```toml
[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py"]
addopts = "-v"
```

| Setting | Meaning |
|---|---|
| `testpaths` | Only look inside `tests/` |
| `python_files` | A file counts only if it starts with `test_` |
| `addopts = "-v"` | Verbose — print each test name |

> ⚠️ **Naming is not optional.** Files must start with `test_`, functions must start with
> `test_`. Otherwise pytest silently skips them — and a skipped test looks exactly like a
> passing one.

---

## 5. Syntax reference

### The entire framework

```python
assert <something_that_should_be_true>
```

True → pass. False → fail. That is the whole mechanism.

### A basic test

```python
from my_ai_app.utils import average


def test_average_returns_mean() -> None:
    """average() computes the arithmetic mean."""
    assert average([2.0, 4.0, 6.0]) == 4.0
```

| Part | Why |
|---|---|
| `test_` prefix | How pytest finds it |
| `-> None` | Tests return nothing; mypy strict requires you to say so |
| Docstring | Becomes your failure message at 1am |

### `parametrize` — same test, many inputs

```python
import pytest


@pytest.mark.parametrize(
    ("selling_price", "cost", "expected"),
    [
        (250.0, 100.0, 150.0),   # normal case
        (250.0,   0.0, 250.0),   # free ingredients
        (100.0, 150.0, -50.0),   # loss
        (100.0, 100.0,   0.0),   # break-even
    ],
)
def test_calculate_profit(
    selling_price: float, cost: float, expected: float
) -> None:
    """Profit is selling price minus cost."""
    assert calculate_profit(selling_price, cost) == expected
```

| Part | Meaning |
|---|---|
| `@` | A **decorator** — wraps the function below with extra behaviour |
| `("selling_price", "cost", "expected")` | Parameter **names** as strings — must match the signature |
| Each tuple | **One separate test run** |
| Test name `[250.0-100.0-150.0]` | pytest joins the values with hyphens |

**Where do the numbers come from?** You invent them. You pick the input, work out the correct
answer **by hand from the business rule**, and write both down. You are the source of truth.

```python
# ❌ Useless — always passes, even if the function is completely wrong
assert calculate_profit(250, 100) == calculate_profit(250, 100)

# ✅ You supply the expected value
assert calculate_profit(250, 100) == 150
```

**How to choose which inputs?** Group them into classes that behave differently, then test
one from each. Testing 220 *and* 1000 adds nothing — both are "normal amounts."

| Class | Why it differs | Example |
|---|---|---|
| Normal | The everyday case | `1000.0` |
| Zero / empty | Division and discount edges | `0.0` |
| Rounds down | 2.4998 → 2.50? | `99.99` |
| Rounds up | 0.025 → 0.03 | `1.0` |
| Decimals | Real order amounts | `250.50` |
| Invalid | Should it error, or return zero? | `-100.0` |

> **What if you don't write a case?** Nothing happens. No warning. The suite passes, having
> never tried that input. **Tests only prove what you wrote down.** They are samples, not
> proofs. 3–5 well-chosen cases per function catches most real bugs.

### Fixtures — shared setup

```python
@pytest.fixture
def inventory() -> list[dict[str, float | str]]:
    """Sample kitchen inventory for tests."""
    return [
        {"name": "rice", "qty": 50.0, "price": 60.0},
        {"name": "oil", "qty": 10.0, "price": 140.0},
    ]


def test_total_value(inventory: list[dict[str, float | str]]) -> None:
    """Total value is quantity times price, summed."""
    assert total_value(inventory) == 4400.0
```

**How the wiring works:**

```
      test asks for a parameter named "inventory"
                        │
                        ▼
      pytest looks for a @fixture with that exact name
                        │
                        ▼
      pytest calls it, takes the return value
                        │
                        ▼
      pytest passes it into the test
```

Matching is **by name**. You never call the fixture yourself.

### The critical property — fresh every test

```python
@pytest.fixture
def cart() -> list[str]:
    return []


def test_add_item(cart: list[str]) -> None:
    cart.append("biryani")
    assert len(cart) == 1


def test_cart_starts_empty(cart: list[str]) -> None:
    assert len(cart) == 0        # ✅ passes — brand-new list
```

A plain global would fail the second test. Fixtures make shared-state bugs structurally
impossible.

### `yield` — setup *and* teardown

```python
from collections.abc import Iterator


@pytest.fixture
def db_session() -> Iterator[Session]:
    """Provide a session and close it afterwards."""
    session = SessionLocal()
    yield session          # ← the test runs here
    session.close()        # ← runs after, even if the test failed
```

**`yield` is like `return`, but pauses instead of finishing:**

```
1. code before yield runs      →  session created
2. yield hands the value to the test
3. THE TEST RUNS
4. test finishes (pass or fail)
5. code after yield runs       →  session closed
```

### Fixture scope

```python
@pytest.fixture(scope="session")
def embedding_model() -> SentenceTransformer:
    """Load once for the entire test run."""
    return SentenceTransformer("all-MiniLM-L6-v2")
```

| Scope | Runs once per |
|---|---|
| `function` *(default)* | Every test |
| `module` | File |
| `session` | Entire run |

**Tradeoff:** wider scope is faster but shared. Use `session` only for expensive
**read-only** things like loaded models. Week 13: this turns a 4-minute suite into 20 seconds.

### `conftest.py` — sharing fixtures across files

A fixture defined in `test_utils.py` is invisible to `test_api.py`. To share it, move it to
`tests/conftest.py`:

```python
# tests/conftest.py
import pytest


@pytest.fixture
def sample_inventory() -> list[dict[str, float]]:
    """Available to EVERY test file automatically."""
    return [{"qty": 50.0, "price": 60.0}]
```

**No import needed.** pytest finds `conftest.py` automatically. This is where your database
fixtures and loaded models will live from Week 6 onward.

### `pytest.approx()` — comparing floats

```python
assert 0.1 + 0.2 == 0.3            # ❌ FAILS
assert 0.1 + 0.2 == pytest.approx(0.3)   # ✅ passes
```

**Why:** floats are stored in binary and cannot represent 0.1 exactly. `0.1 + 0.2` is
actually `0.30000000000000004`.

```python
assert model_accuracy == pytest.approx(0.85, abs=0.01)   # within ±0.01
assert loss == pytest.approx(0.5, rel=0.05)              # within 5%
```

> **You will need this from Week 4 onward.** Every ML metric, loss value, and embedding
> similarity is a float. Exact equality will fail for reasons that have nothing to do with
> your code being wrong.

### `pytest.raises()` — testing that errors happen

So far you have only tested success. This tests failure:

```python
def test_divide_by_zero_raises() -> None:
    """Dividing by zero raises ZeroDivisionError."""
    with pytest.raises(ZeroDivisionError):
        1 / 0


def test_invalid_dish_raises_with_message() -> None:
    """A missing dish raises ValueError naming the dish."""
    with pytest.raises(ValueError, match="not found"):
        get_dish("nonexistent")
```

| Part | Meaning |
|---|---|
| `with pytest.raises(X):` | The test **passes** if `X` is raised, **fails** if nothing is raised |
| `match="not found"` | The error message must contain this text |

> **Why it matters:** "this input should be rejected" is a real requirement. Without
> `pytest.raises`, you can only test the happy path — and the happy path is not where bugs live.

### `monkeypatch` — testing without the real thing

**The Week 11 problem:** your function calls an LLM API. Every test run costs money and takes
10 seconds. Multiply by 50 tests, run 20 times a day.

**The solution — replace the real call with a fake:**

```python
def test_summarise_uses_llm_response(monkeypatch: pytest.MonkeyPatch) -> None:
    """summarise() returns the model's text."""

    def fake_llm_call(prompt: str) -> str:
        return "This is a fake summary."

    monkeypatch.setattr("my_ai_app.llm.call_model", fake_llm_call)

    result = summarise("some long document")
    assert result == "This is a fake summary."
```

| Part | Meaning |
|---|---|
| `monkeypatch` | A built-in fixture — no import, just name it as a parameter |
| `setattr(target, replacement)` | Swap the real function for the fake one |
| Automatic undo | The real function is restored after the test |

**This is called *mocking*.** You are testing *your* logic, not the API's. Whether the LLM
works is not your test's problem — whether you handle its response correctly is.

> **Critical in Weeks 11–16.** Without mocking, your test suite is slow, expensive, flaky,
> and fails whenever the network hiccups.

---

## 6. Commands

```powershell
uv run pytest                                       # everything
uv run pytest tests/test_utils.py                   # one file
uv run pytest -k "gst"                              # only tests matching "gst"
uv run pytest -x                                    # stop at first failure
uv run pytest --cov=src --cov-report=term-missing   # coverage + missing lines
uv run pytest -q                                    # quiet output
```

---

## 7. What breaks

### ❌ Looping inside a test

```python
def test_all_cases() -> None:
    for price, cost, expected in cases:
        assert calculate_profit(price, cost) == expected
```

**Stops at the first failure** — you never see cases 2 and 3. And the error doesn't say which
case broke. Three fix-rerun cycles instead of one.

> **Rule: never loop inside a test. Use `parametrize`.**

### ❌ Shared global state

```python
CART: list[str] = []      # every test mutates the same object
```

Tests pass alone, fail together — or pass in the order you wrote them and fail when pytest
reorders. Hours lost. **Use a fixture.**

### ❌ Computing the expected value with the code under test

Proves nothing. You must supply the answer by hand.

### ❌ Wrong file or function name

`utils_test.py` or `check_average()` are **silently ignored**.

### ⚠️ Chasing 100% coverage

Cover logic that can be wrong. Skip plumbing.
Your Day-4 result was **correct**: `utils.py` 100%, `main.py` 0%.

---

## 8. What you built

- `tests/test_utils.py` — 8 tests
- Covered: normal cases, empty input, case-insensitivity, tie-breaking
- `utils.py` at **100% coverage**
- **Caught a real bug:** `find_longest([])` returned `""` instead of `None`

That last one is the entire point. The test was right, the code was wrong, and you found out
in 0.3 seconds instead of from a user.

---

## 9. Quick recall

1. Why must the expected value be calculated by hand?
2. What happens if you name a file `utils_test.py`?
3. Why is `parametrize` better than a `for` loop inside one test?
4. What does `yield` do in a fixture that `return` cannot?
5. Why will `assert loss == 0.5` fail even when your code is correct?

---
---

# DAY 5 — async / await

> **One line:** Stop standing around while you wait.

---

## 1. What it is

Your code spends most of its life **waiting** — for a database, an API, a file.

Normal Python waits *stupidly*: it stops everything and stares at the wall.

```
Sync:   [call: 2s] → [call: 2s] → [call: 2s]           = 6 seconds

Async:  [call: 2s]
        [call: 2s]   all at once                        = 2 seconds
        [call: 2s]
```

### The waiter analogy

**Synchronous — a bad waiter:**

Takes table 1's order. Walks to the kitchen. **Stands there watching the chef cook for 15
minutes.** Brings the food. Only then goes to table 2.

→ Three tables = 45 minutes.

**Asynchronous — a good waiter:**

Takes table 1's order, hands it to the kitchen. Immediately takes table 2's. Then table 3's.
Delivers each as it becomes ready.

→ Three tables = ~16 minutes. **One waiter. Not three.**

> **The insight people miss:** async is *not* multiple workers. It is one worker who stops
> standing around.

---

## 2. Why we use it

**Async only helps when you are waiting:**

| Type | Meaning | Async helps? |
|---|---|---|
| **I/O-bound** | Waiting on network, disk, database | ✅ Massively |
| **CPU-bound** | Actually computing — math, training | ❌ Not at all |

Async does not make anything faster. It stops you from *idling*. If the CPU is genuinely
busy, there is no idle time to reclaim.

---

## 3. Where you will use it

| When | Use |
|---|---|
| **Day 6** | Every FastAPI endpoint is `async def` |
| **Week 11** | LLM calls take 2–10 seconds — this is *the* concurrency problem in AI |
| **Week 12** | Embedding 500 documents in parallel instead of one at a time |
| **Week 15** | Agents calling several tools simultaneously |
| **Weeks 7–10** | ❌ Almost none — model training is CPU/GPU-bound |
| **KitchenOS** | Your chatbot context-builder makes 6 sequential DB queries |

### The KitchenOS case, concretely

Your `build_kitchen_context()` gathers inventory, dishes, orders, wastage, and suppliers
before every chatbot reply. Say each query takes 200ms.

**Synchronous:** 6 × 200ms = **1200ms of pure waiting**, every message.

**Asynchronous:**

```python
user, inventory, dishes, orders, wastage, suppliers = await asyncio.gather(
    get_user(db, user_id),
    get_inventory(db, user_id),
    get_dishes(db, user_id),
    get_orders(db, user_id),
    get_wastage(db, user_id),
    get_suppliers(db, user_id),
)
```

**~200ms.** Six times faster. Same database, same queries.

### The scenario that decides whether a product survives

Ten kitchen owners message your chatbot at once. Each Groq call takes 3 seconds.

```
SYNC endpoint                    ASYNC endpoint
─────────────                    ──────────────
User 1:  waits  3s  ✅            All 10 users: ~3s each  ✅
User 2:  waits  6s
User 3:  waits  9s
   ...
User 10: waits 30s  ← gone
```

**This is not optimisation. It is the difference between a product and a demo.**

---

## 4. Setup

Nothing to install — `asyncio` is built in.

For HTTP:

```powershell
uv add httpx
```

`httpx` is `requests` with async support.

---

## 5. Syntax reference

### `async def` — creates a coroutine

```python
async def get_data() -> str:
    return "hello"


result = get_data()
print(result)
# <coroutine object get_data at 0x000001C4>
# RuntimeWarning: coroutine 'get_data' was never awaited
```

**Calling an async function does not run it.** It builds a *coroutine* — a description of
work, paused before its first line.

> Think of `async def` as writing a recipe. `await` is cooking it.

> ⚠️ **That warning is the #1 async bug.** It always means a missing `await`.

### `await` — the yield point

```python
result = await get_data()      # ✅ now it runs
```

`await` means: *"I'm about to wait. Take control back and do something useful. Wake me when
my result arrives."*

That handoff is what makes concurrency possible. Without `await`, there is no moment where
the program can switch tasks.

```python
async def fetch_dish(dish_id: int) -> dict:
    print(f"  → requesting dish {dish_id}")
    await asyncio.sleep(2)              # ← control released HERE
    print(f"  ← got dish {dish_id}")
    return {"id": dish_id}
```

At `await`, this function steps aside. Something else runs. Two seconds later it resumes at
the exact next line, local variables intact.

### `asyncio.run()` — the event loop

```python
if __name__ == "__main__":
    asyncio.run(main())
```

Starts the **event loop** — a scheduler that:

```
1. Runs a coroutine until it hits `await`
2. Parks it, notes what it's waiting for
3. Runs the next ready coroutine
4. When a result arrives, resumes that coroutine where it paused
```

One loop, one thread, many paused tasks.

> **Exactly one `asyncio.run()` per program**, at the very top. Calling it inside async code
> crashes with "event loop is already running."

### `asyncio.gather()` — run many, wait for all

```python
results = await asyncio.gather(
    fetch_data("call-1", 2),
    fetch_data("call-2", 2),
    fetch_data("call-3", 2),
)
```

Results come back **in the order you passed them**, not the order they finished. That
guarantee is why `gather` is the default choice.

### `return_exceptions=True` — surviving failures

```python
results = await asyncio.gather(*tasks)                       # one failure kills all
results = await asyncio.gather(*tasks, return_exceptions=True)   # failures become values

for result in results:
    if isinstance(result, Exception):
        print(f"failed: {result}")
    else:
        print(f"ok: {result}")
```

> **Week 12:** embedding 500 documents. Document #237 is corrupt. Without this, you lose all
> 500 and start over. With it, you get 499 embeddings and one identified failure.

### `asyncio.create_task()` — fire and forget

```python
async def send_order(order_id: int) -> dict:
    """Save the order, notify WhatsApp in the background."""
    asyncio.create_task(send_whatsapp_alert(order_id))   # don't wait
    return await save_to_db(order_id)                    # respond immediately
```

The owner gets confirmation instantly; the alert sends in the background.

> ⚠️ **Obscure trap:** hold a reference, or the garbage collector may kill the task mid-flight.
> ```python
> _background: set[asyncio.Task] = set()
> task = asyncio.create_task(send_alert(order_id))
> _background.add(task)
> task.add_done_callback(_background.discard)
> ```

### `async with` — async cleanup

```python
async with httpx.AsyncClient() as client:
    tasks = [fetch_status(client, url) for url in urls]
    results = await asyncio.gather(*tasks)
```

Guarantees the connection pool closes even if something throws.

### `*tasks` — unpacking

```python
tasks = [coro_a, coro_b, coro_c]
await asyncio.gather(*tasks)      # becomes gather(coro_a, coro_b, coro_c)
```

The `*` unpacks a list into separate arguments.

### Always set a timeout

```python
response = await client.get(url, timeout=10.0)
```

A hung request without a timeout hangs **forever**. In Week 11 this is what stops one slow
LLM call from freezing your whole app.

---

## 6. Commands

```powershell
uv run python -m my_ai_app.demo_sync      # 6.01s
uv run python -m my_ai_app.demo_async     # 2.00s
uv run python -m my_ai_app.fetch_urls     # real HTTP
```

---

## 7. What breaks

### ❌ Forgetting `await`

```python
result = fetch_data("x", 1)        # ❌ a coroutine object, not the result
result = await fetch_data("x", 1)  # ✅
```

### ❌ Blocking inside async — the catastrophic one

```python
async def handler() -> None:
    time.sleep(3)          # ❌ freezes the ENTIRE event loop
    await asyncio.sleep(3) # ✅
```

`time.sleep` blocks the **loop itself**, not just this coroutine. All ten users freeze. You
now have async complexity with zero async benefit.

| ❌ Blocks the loop | ✅ Releases it |
|---|---|
| `time.sleep()` | `await asyncio.sleep()` |
| `requests.get()` | `await httpx.AsyncClient().get()` |
| `open()` / `.read()` | `await aiofiles.open()` |
| Sync SQLAlchemy | Async SQLAlchemy / `asyncpg` |

> **Real risk for KitchenOS:** `async def` endpoints calling *synchronous* SQLAlchemy get
> zero concurrency benefit while paying full complexity cost.

### ❌ Async on CPU work

```python
async def train_model() -> None:
    model.fit(X, y)        # 10 minutes of pure CPU — async gains nothing
```

Use multiprocessing. `await` needs an idle moment to exploit; there isn't one.

### ⚠️ Nested `asyncio.run()`

Crashes. One per program, at the top.

---

## 8. What you built

- `demo_sync.py` — 3 calls, **6.01s**
- `demo_async.py` — same 3 calls, **2.00s**
- `fetch_urls.py` — real concurrent HTTP with `httpx`
- Result: 3 × 200 OK in 3.73s (sequential would be 6s+)
- **Also learned:** how to read server logs, and that `503` was httpbin's problem, not yours

---

## 9. Quick recall

1. Why does calling an `async def` function not run it?
2. What does `await` actually hand back, and to whom?
3. Why is `time.sleep()` inside `async def` worse than useless?
4. When does `asyncio.gather` return results out of order?
5. Why is async useless during Week 10's model training?

---
---

# DAY 6 — FastAPI & Pydantic

> **One line:** Turn Python functions into a web service, with a guard at the door.

---

## 1. What it is

**FastAPI** turns Python functions into HTTP endpoints.

**Pydantic** validates every piece of data coming in and going out.

```
Request  →  Pydantic validates  →  your function  →  Pydantic validates  →  Response
                    │                                        │
              422 if invalid                        filters extra fields
           (your code never runs)
```

---

## 2. Why we use it

**Without Pydantic:** a user sends `{"quantity": "ten"}` and your code crashes four functions
deep with a confusing error — or worse, writes bad data to your database.

**With Pydantic:** they get a clear 422 listing every problem, and your code never runs.

| Benefit | How |
|---|---|
| Input validation | Automatic, from type hints |
| API documentation | Generated, always current |
| Editor autocomplete | Real objects, not dicts |
| Concurrency | `async def` endpoints |
| Output safety | `response_model` filters internal fields |

---

## 3. Where you will use it

| When | Use |
|---|---|
| **Week 11** | **Pydantic forces LLMs to return valid JSON** |
| **Week 13** | RAG API — query in, cited answer out |
| **Week 15** | Agent tool schemas are Pydantic models |
| **Week 20** | Your capstone's entire public interface |
| **KitchenOS** | Already using it — but likely without `response_model` or `Field` constraints |

> **This is not a web skill you are borrowing.** In Week 11, the same `BaseModel` you write
> today becomes the schema that constrains model output. Structured LLM outputs *are*
> Pydantic.

---

## 4. Setup

```powershell
uv add fastapi uvicorn[standard]
```

| Package | Role |
|---|---|
| `fastapi` | Defines *what* happens |
| `uvicorn` | The server that handles HTTP |
| `[standard]` | Extras — faster event loop, websockets |

**Run:**

```powershell
uv run uvicorn my_ai_app.api:app --reload
```

| Part | Meaning |
|---|---|
| `my_ai_app.api` | Module path (dots) |
| `:app` | The variable name inside that file |
| `--reload` | Restart on save — **development only** |

Then open **http://127.0.0.1:8000/docs**

---

## 5. Syntax reference

### The app

```python
from fastapi import FastAPI

app = FastAPI(
    title="My AI App",
    description="Learning production Python",
    version="0.1.0",
)


@app.get("/health")
async def health() -> dict[str, str]:
    """Return service status."""
    return {"status": "ok"}
```

| Part | Meaning |
|---|---|
| `@app.get("/health")` | Registers this function as the handler for `GET /health` |
| Function name | Irrelevant to the URL |
| `async def` | Runs on the event loop — serves many users concurrently |
| `-> dict[str, str]` | Used to build docs and serialise to JSON |

### Pydantic models

```python
from pydantic import BaseModel, Field


class DishRequest(BaseModel):
    """Incoming data for creating a dish."""

    name: str = Field(min_length=1, max_length=100)
    selling_price: float = Field(gt=0, description="Price in rupees")
    cost: float = Field(ge=0)


class DishResponse(BaseModel):
    """Dish data returned to the client."""

    name: str
    selling_price: float
    cost: float
    profit: float
    margin_percent: float
```

| Part | Meaning |
|---|---|
| `(BaseModel)` | Inheriting this is what makes it validated |
| `Field(...)` | Constraints **beyond** the type |
| `gt=0` | Greater than zero — price cannot be ₹0 |
| `ge=0` | Greater than **or equal** — cost *can* be zero |

**Constraint vocabulary:** `gt` · `ge` · `lt` · `le` · `min_length` · `max_length` · `pattern`

> **Why two models?** Request and Response are different shapes. Keeping them separate means
> you can never accidentally leak an internal field — a password hash, an owner ID — into a
> response.

### An endpoint with validation

```python
@app.post("/dishes", response_model=DishResponse, status_code=201)
async def create_dish(dish: DishRequest) -> DishResponse:
    """Calculate profit and margin for a dish."""
    profit = dish.selling_price - dish.cost
    margin = (profit / dish.selling_price) * 100

    return DishResponse(
        name=dish.name,
        selling_price=dish.selling_price,
        cost=dish.cost,
        profit=round(profit, 2),
        margin_percent=round(margin, 2),
    )
```

| Part | Meaning |
|---|---|
| `dish: DishRequest` | **This one annotation does everything** — reads the body, validates, hands you a typed object |
| `response_model=` | Validates outgoing data, filters extra fields |
| `status_code=201` | "Created" — correct for POST |
| `dish.selling_price` | Dot access. It's an object, not a dict. |

### Validation in action

**Bad request:**

```json
{ "name": "", "selling_price": -50, "cost": 100 }
```

**Response — 422, and your function never executed:**

```json
{
  "detail": [
    { "loc": ["body", "name"], "msg": "String should have at least 1 character" },
    { "loc": ["body", "selling_price"], "msg": "Input should be greater than 0" }
  ]
}
```

> Note it reports **both** errors, not just the first — the client fixes everything in one
> round trip.

### Path parameters and errors

```python
from fastapi import HTTPException

DISHES: dict[int, str] = {1: "Biryani", 2: "Dosa"}


@app.get("/dishes/{dish_id}")
async def get_dish(dish_id: int) -> dict[str, str]:
    """Return a dish by ID."""
    if dish_id not in DISHES:
        raise HTTPException(status_code=404, detail=f"Dish {dish_id} not found")
    return {"name": DISHES[dish_id]}
```

| Part | Meaning |
|---|---|
| `{dish_id}` in the path | A **path parameter** — matched to the function parameter by name |
| `dish_id: int` | Converts the URL string to int; returns 422 for `/dishes/abc` automatically |
| `raise HTTPException` | The correct way to error. Don't `return` an error dict. |

> ⚠️ **Route order matters.** `GET /dishes` must be declared **above** `GET /dishes/{dish_id}`.
> FastAPI matches top-down; reversed, `/dishes` would try to parse `"dishes"` as an int.

### Dependency injection — `Depends`

```python
from typing import Annotated
from fastapi import Depends, Header


async def verify_token(x_api_key: Annotated[str, Header()]) -> str:
    """Reject requests without a valid API key."""
    if x_api_key != "secret-dev-key":
        raise HTTPException(status_code=401, detail="Invalid API key")
    return x_api_key


@app.get("/protected")
async def protected_route(
    token: Annotated[str, Depends(verify_token)],
) -> dict[str, str]:
    """An endpoint requiring authentication."""
    return {"message": "You're in"}
```

| Part | Meaning |
|---|---|
| `Annotated[str, Header()]` | A string, sourced from an HTTP header |
| `x_api_key` → `X-API-Key` | FastAPI converts the name automatically |
| `Depends(verify_token)` | Run this **before** the endpoint. If it raises, the endpoint never runs. |

> **This is the same mechanism as a pytest fixture** — a setup function whose result is
> injected by name. In KitchenOS it's how your DB session arrives. In Week 13 it's how you
> inject a loaded embedding model.
>
> **The point:** the guard runs before the handler, every time, and you cannot forget to call it.

### Testing endpoints

```python
from fastapi.testclient import TestClient

from my_ai_app.api import app

client = TestClient(app)


def test_health_returns_ok() -> None:
    """Health endpoint reports service status."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_create_dish_rejects_negative_price() -> None:
    """Negative prices are rejected before reaching the handler."""
    response = client.post(
        "/dishes",
        json={"name": "Biryani", "selling_price": -50, "cost": 100},
    )
    assert response.status_code == 422
```

`TestClient` calls your endpoints **in-process** — no server, no network, no port.
Runs in milliseconds.

> **That second test is worth appreciating.** You are testing a behaviour you never wrote
> code for. Pydantic provides it; the test locks it in.

---

## 6. Commands

```powershell
uv run uvicorn my_ai_app.api:app --reload           # dev server
uv run uvicorn my_ai_app.api:app --host 0.0.0.0     # accept external connections
```

| URL | What |
|---|---|
| `/docs` | Swagger UI — interactive, generated from type hints |
| `/redoc` | Alternative documentation view |
| `/openapi.json` | The raw API schema |

---

## 7. What breaks

### ❌ Route order

Specific paths must come before parameterised ones.

### ❌ Returning an error dict instead of raising

```python
return {"error": "not found"}              # ❌ status is still 200
raise HTTPException(404, "not found")      # ✅
```

### ❌ Reusing one model for request and response

Leaks internal fields. Two models, always.

### ⚠️ JSON has no integer keys

```python
DISHES: dict[int, str] = {1: "Biryani"}
# response.json() == {"1": "Biryani"}     ← STRING key
```

You would never predict this. A test pins it down.

### ⚠️ `--reload` in production

Slow and leaks memory. Development only.

---

## 8. What you built

- 7 endpoints: `/health`, `/dishes` (list), `/dishes/{id}`, `/dishes` (POST), `/gst`, `/protected`
- 4 Pydantic schemas with `Field` constraints
- API-key auth via `Depends`
- 15 tests total, all passing
- Auto-generated Swagger docs at `/docs`

---

## 9. Quick recall

1. What does `dish: DishRequest` do that would otherwise take 20 lines?
2. Why separate `DishRequest` and `DishResponse`?
3. Why must `GET /dishes` come before `GET /dishes/{dish_id}`?
4. How is `Depends()` the same idea as a pytest fixture?
5. Why does `response.json()` return `{"1": ...}` when your dict has `1` as an int key?

---
---

# DAY 7 — Docker & CI

> **One line:** Ship the machine along with the code, and let a robot check your work.

---

## PART A — DOCKER

## 1. What it is

Your app works on your laptop because of *your* Python, *your* libraries, *your* OS. The
server has none of that.

**Docker packages everything into one box** that runs identically anywhere.

| Image | Container |
|---|---|
| The blueprint | A running instance |
| Built once | Started many times |
| Like a class | Like an object |

---

## 2. Why we use it

```
Without Docker:  "works on my machine"  🤷
With Docker:     the machine ships with the code
```

**For you specifically:** in Week 14 you will have CUDA versions, PyTorch builds, and model
dependencies that are genuinely painful to reproduce. Docker makes that a one-line rebuild
instead of a two-day reinstall.

---

## 3. Where you will use it

| When | Use |
|---|---|
| **Week 6** | Deploying your first ML product |
| **Week 14** | Pinning CUDA + PyTorch + transformers versions |
| **Week 17** | Running vLLM inference servers |
| **Week 20** | Capstone deployment |
| **KitchenOS** | Already using it — Railway builds from your Dockerfile |

---

## 4. Setup

Install **Docker Desktop**, restart, then:

```powershell
docker --version
docker run hello-world
```

---

## 5. Syntax reference

### `.dockerignore`

```dockerignore
.venv/
__pycache__/
*.pyc
.git/
.github/
tests/
.pytest_cache/
.mypy_cache/
.ruff_cache/
.env
```

Same idea as `.gitignore`, different purpose. Everything **not** listed gets copied into the
image. Without this you would ship your entire `.venv` and `.git` history — 500MB instead of
150MB.

> ⚠️ **But do not exclude build inputs.** `README.md` must stay, because `pyproject.toml`
> references it and hatchling reads it during install. *(This was your actual Day-7 error.)*

### The Dockerfile

```dockerfile
# ---------- Stage 1: build ----------
FROM python:3.11-slim AS builder

COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

WORKDIR /app

ENV UV_COMPILE_BYTECODE=1
ENV UV_LINK_MODE=copy

COPY pyproject.toml uv.lock README.md ./
COPY src ./src

RUN uv sync --frozen --no-dev


# ---------- Stage 2: runtime ----------
FROM python:3.11-slim

WORKDIR /app

COPY --from=builder /app/.venv /app/.venv
COPY --from=builder /app/src /app/src

ENV PATH="/app/.venv/bin:$PATH"

EXPOSE 8000

CMD ["uvicorn", "my_ai_app.api:app", "--host", "0.0.0.0", "--port", "8000"]
```

| Instruction | Meaning |
|---|---|
| `FROM python:3.11-slim` | Base image. `slim` = ~150MB vs ~1GB for full. |
| `AS builder` | Names this stage so stage 2 can copy from it |
| `WORKDIR /app` | Working directory inside the container |
| `UV_COMPILE_BYTECODE=1` | Pre-compile `.pyc` — faster startup |
| `UV_LINK_MODE=copy` | Hardlinks break across Docker layers |
| `COPY pyproject.toml uv.lock` **first** | **Layer caching** — see below |
| `--frozen` | Install exactly the lockfile; don't update it |
| `--no-dev` | Skip pytest, ruff, mypy. **Test tools don't ship.** |
| `COPY --from=builder` | Take only the finished venv from stage 1 |
| `ENV PATH=` | Put the venv's binaries first, so `uvicorn` resolves |
| `EXPOSE 8000` | **Documentation only.** It does not open a port. |
| `CMD [...]` | What runs when the container starts |

### Why dependencies are copied before code

```
Docker caches each layer.

COPY pyproject.toml  →  layer A
RUN uv sync          →  layer B   ← expensive
COPY src             →  layer C   ← changes constantly

Edit your code  →  only layer C rebuilds. B is reused.
Copy everything at once  →  every edit triggers a full reinstall.
```

### Why two stages

```
Stage 1  needs uv, build tools, compilers
Stage 2  needs none of them

Discarding them:
  • cuts image size roughly in half
  • removes tools an attacker could use
```

### `--host 0.0.0.0` is mandatory

Inside a container, `127.0.0.1` means "only this container." You would never reach it.

---

## 6. Commands

```powershell
docker build -t my-ai-app .            # build; -t = tag, . = build context
docker run -p 8000:8000 my-ai-app      # run with port mapping
docker run -d -p 8000:8000 my-ai-app   # detached (background)
docker ps                              # running containers
docker ps -a                           # including stopped
docker logs <id>                       # container output
docker stop <id>
docker images                          # list images
docker system prune                    # reclaim disk space
```

### Port mapping

```
-p 8080:8000
    │     │
    │     └── container port (never changes)
    └──────── host port (your laptop)
```

The container always serves on 8000 internally. `-p` decides where you reach it.

> In Week 17 you will run several model servers this way — same container port, different
> host ports.

---

## PART B — GITHUB ACTIONS (CI)

## 1. What it is

**Continuous Integration.** Every push, GitHub runs your quality checks automatically.

**What actually happens — there is no magic:**

```
1. You push
2. GitHub sees .github/workflows/ci.yml exists
3. GitHub rents a brand-new, EMPTY Linux computer
4. Downloads ONLY the files you committed
5. Installs dependencies from scratch (uv.lock)
6. Runs YOUR ruff, YOUR mypy, YOUR tests
7. Any command fails  →  red ✗ + email
```

> **GitHub knows nothing about your code.** It runs the checks *you already wrote*.
> CI adds **automation** and **a clean machine** — not intelligence.

---

## 2. Why we use it

| Value | Why it matters |
|---|---|
| **You forget. CI doesn't.** | It's 11pm, the fix is one line, you push it. CI still checks. |
| **The machine is empty** | Your laptop has accumulated state — packages, env vars, uncommitted files. If your code only works because of that, only a fresh VM can tell you. |
| **Missing files** | Added `httpx` but never committed `uv.lock`? Your laptop is fine. CI fails immediately. |
| **Regression** | Week 12: you tweak chunking. CI reruns every test from week 1 in 20 seconds. |

---

## 3. Where you will use it

| When | Use |
|---|---|
| **Every push, from now on** | Four gates: lint, format, types, tests |
| **Week 6** | Add a step that trains and validates model metrics |
| **Week 18** | **Add LLM evals — block the merge if answer quality drops** |
| **Week 20** | Auto-deploy on green |

---

## 4. Setup

The path is **mandatory and exact**:

```
my-ai-app/
└── .github/
    └── workflows/
        └── ci.yml
```

```powershell
mkdir .github\workflows
New-Item .github\workflows\ci.yml
```

> Misspell either folder and nothing runs — no error, just silence.
> The filename is free; `ci.yml` is convention. GitHub runs every `.yml` it finds there.

---

## 5. Syntax reference

```yaml
name: CI

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  quality:
    runs-on: ubuntu-latest

    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Install uv
        uses: astral-sh/setup-uv@v5
        with:
          enable-cache: true

      - name: Install dependencies
        run: uv sync --dev

      - name: Lint
        run: uv run ruff check .

      - name: Format check
        run: uv run ruff format --check .

      - name: Type check
        run: uv run mypy src

      - name: Tests
        run: uv run pytest --cov=src
```

| Key | Meaning |
|---|---|
| `name:` | Shows in the Actions tab |
| `on:` | Triggers — every push to `main`, every PR into it |
| `jobs:` → `quality:` | A job. The name is yours to choose. |
| `runs-on: ubuntu-latest` | A **fresh** Linux VM, every run |
| `steps:` | Each step either `uses` an action or `run`s a command |
| `actions/checkout@v4` | Clones your repo into the VM. Without it there is no code. |
| `enable-cache: true` | Caches dependencies — CI drops from ~90s to ~20s |
| `ruff format --check` | **Reports** bad formatting instead of fixing it |

> **Why `--check`?** CI must judge your code, never modify it.

> ⚠️ **YAML indentation is significant.** Two spaces, never tabs. The #1 source of YAML errors.

---

## 6. Reading the result

Repo → **Actions** tab.

```
✅ green check  →  all four gates passed
❌ red X        →  click it, open the failing step, read the log
```

---

## 7. What breaks

### ❌ `.dockerignore` excluding a build input

Your actual error:

```
CopyIgnoredFile: Attempting to Copy file "README.md"
that is excluded by .dockerignore (line 11)
```

`.dockerignore` excludes what the **image** doesn't need at runtime. But anything the
**build** reads must stay.

### ❌ Port already allocated

Another process holds it — usually a `uvicorn` still running in another terminal.

```powershell
docker ps                        # a container?
netstat -ano | findstr :8000     # what holds it?
docker run -p 8080:8000 my-ai-app   # or just use another host port
```

### ❌ Forgetting `--host 0.0.0.0`

The container starts fine and is completely unreachable.

### ❌ Wrong workflow path

`.github/workflow/` (singular) → silently nothing.

### ⚠️ CI passes locally but fails on GitHub

**That is CI doing its job.** Something on your laptop isn't in the repo. Check `uv.lock`
and `.gitignore`.

---

## 8. What you built

- Multi-stage `Dockerfile` — ~200MB image
- `.dockerignore`
- Container running your API, reachable at `localhost:8080/docs`
- `.github/workflows/ci.yml` — four gates
- **CI #1: green ✅ in 22 seconds**

---

## 9. Quick recall

1. What is the difference between an image and a container?
2. Why copy `pyproject.toml` before `src/`?
3. Why does stage 2 start with a fresh `FROM`?
4. In `-p 8080:8000`, which number is the container's?
5. What can CI catch that your laptop never can — and why?

---
---
---

# APPENDIX A — Command Cheat Sheet

## uv

```powershell
uv init <name>                   # create a project
uv add <pkg>                     # install + record a library
uv add --dev <pkg>               # dev tool (never ships)
uv sync                          # rebuild env from lockfile
uv sync --frozen --no-dev        # production install
uv run <command>                 # run anything inside the env
uv run python -m my_ai_app.main  # run a module
uv --version
```

## Git

```powershell
git status                       # what changed
git add .                        # stage everything
git commit -m "feat: ..."        # save
git push                         # upload
git log --oneline                # history
git diff                         # unstaged changes
git remote -v                    # where does this push to
git rev-parse --show-toplevel    # WHICH REPO AM I IN
git checkout -b feat/name        # new branch
git merge feat/name              # merge it in
git reset HEAD~1                 # undo last commit, keep changes
```

## Quality (the daily four)

```powershell
uv run ruff check . --fix
uv run ruff format .
uv run mypy src
uv run pytest
```

## pytest

```powershell
uv run pytest                                       # all
uv run pytest tests/test_utils.py                   # one file
uv run pytest -k "gst"                              # matching name
uv run pytest -x                                    # stop at first failure
uv run pytest -q                                    # quiet
uv run pytest --cov=src --cov-report=term-missing   # coverage
```

## FastAPI

```powershell
uv run uvicorn my_ai_app.api:app --reload
```

## Docker

```powershell
docker build -t my-ai-app .
docker run -p 8000:8000 my-ai-app
docker run -d -p 8080:8000 my-ai-app
docker ps
docker logs <id>
docker stop <id>
docker images
docker system prune
```

## Windows troubleshooting

```powershell
netstat -ano | findstr :8000     # what holds a port
taskkill /PID <pid> /F           # kill it
taskkill /F /IM git.exe          # kill stuck git
Remove-Item -Force .git\index.lock
Test-Path <path>                 # does it exist
type <file>                      # print file contents
dir <folder>                     # list files
```

---
---

# APPENDIX B — Syntax Cheat Sheet

## Type hints

```python
name: str
count: int
score: float
active: bool

scores: list[float]
config: dict[str, int]
point: tuple[float, float]
tags: set[str]

result: str | None                 # either text or nothing
counts: dict[str, int] = {}        # empty containers NEED annotation

def f(x: int) -> str: ...
def g() -> None: ...
```

## pytest

```python
def test_name() -> None:
    assert actual == expected

@pytest.mark.parametrize(("a", "b"), [(1, 2), (3, 4)])
def test_many(a: int, b: int) -> None: ...

@pytest.fixture
def data() -> list[int]:
    return [1, 2, 3]

@pytest.fixture
def db() -> Iterator[Session]:
    s = make_session()
    yield s
    s.close()

@pytest.fixture(scope="session")
def model(): ...

assert value == pytest.approx(0.3)
assert value == pytest.approx(0.85, abs=0.01)

with pytest.raises(ValueError, match="not found"):
    do_thing()

def test_x(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr("module.function", fake_function)
```

## async

```python
async def f() -> str: ...              # defines a coroutine
result = await f()                     # runs it
asyncio.run(main())                    # starts the event loop (once)
await asyncio.gather(a(), b(), c())    # concurrent, ordered results
await asyncio.gather(*tasks, return_exceptions=True)
asyncio.create_task(background())      # fire and forget
async with httpx.AsyncClient() as c: ...
await asyncio.sleep(2)                 # NOT time.sleep
```

## FastAPI

```python
app = FastAPI(title="...", version="0.1.0")

@app.get("/path")
@app.post("/path", response_model=Model, status_code=201)
@app.get("/path/{item_id}")

raise HTTPException(status_code=404, detail="...")

def handler(item: RequestModel) -> ResponseModel: ...
def handler(x: Annotated[str, Header()]) -> ...:
def handler(x: Annotated[str, Depends(func)]) -> ...:
```

## Pydantic

```python
class Model(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    price: float = Field(gt=0)
    cost: float = Field(ge=0)
    tag: str | None = None
```

**Constraints:** `gt` `ge` `lt` `le` `min_length` `max_length` `pattern`

## Dockerfile

```dockerfile
FROM image AS stage
WORKDIR /app
ENV KEY=value
COPY source dest
COPY --from=stage source dest
RUN command
EXPOSE port
CMD ["executable", "arg"]
```

## GitHub Actions

```yaml
name: CI
on:
  push:
    branches: [main]
jobs:
  jobname:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: command
```

---
---

# APPENDIX C — Error Dictionary

*Every error you actually hit in Week 1, what it meant, and the fix.*

---

### `NameError: name 'add' is not defined`

**Meaning:** you called a function before Python reached its `def`.

**Cause:** Python reads top to bottom. `def` is an action, not a declaration.

**Fix:** move all `def` blocks **above** `if __name__ == "__main__":`.

---

### `Another git process seems to be running... index.lock: File exists`

**Meaning:** an interrupted Git command left a lock file behind.

**Fix:**
```powershell
# 1. Close VS Code (its Git extension often holds the lock)
taskkill /F /IM git.exe
Remove-Item -Force .git\index.lock
Test-Path .git\index.lock     # must print False
```

---

### `error: src refspec main does not match any`

**Meaning:** **you have no commits to push.** Not a push problem.

**Fix:** run `git log --oneline` first. If it's empty, the real failure happened earlier —
usually the commit itself failed.

---

### `fatal: Unable to create 'C:/Users/Lenovo/.git/index.lock'`

**Meaning:** ⚠️ **read the path.** A Git repo existed at your entire home folder, not your
project. Every command was operating on Downloads, Documents, AppData, everything.

**Cause:** when Git finds no repo in the current folder, it walks **upward** until it finds one.

**Fix:**
```powershell
Remove-Item -Recurse -Force C:\Users\Lenovo\.git   # deletes tracking only, not files
cd C:\Users\Lenovo\my-ai-app
git init
```

**Prevention — before any commit:**
```powershell
git rev-parse --show-toplevel
git status
```

---

### `error: remote origin already exists`

**Meaning:** harmless. The remote is set. Verify it:
```powershell
git remote -v
git remote set-url origin <correct-url>    # if wrong
```

---

### `collected 0 items` (pytest)

**Meaning:** pytest found no file matching `test_*.py` in `testpaths`.

**Causes:** file not created · wrong folder · wrong name (`utils_test.py` is ignored).

---

### `ImportError: cannot import name 'average' from 'my_ai_app.utils'`

**Meaning:** the file exists but the function isn't in it. *(A missing file gives
`ModuleNotFoundError` instead.)*

**Causes:** file empty · unsaved · name mismatch · function in the wrong file.

---

### `ModuleNotFoundError: No module named 'httpx'`

**Meaning:** package not installed.

**Fix:** `uv add httpx`

**How to read a traceback:** last line = what went wrong · above it = where ·
`<frozen runpy>` lines = Python internals, ignore.

---

### `AssertionError: assert '' == None`

**Meaning:** the test is right, the code is wrong.

**Your case:** `find_longest([])` returned `""` instead of `None`.

**Why it matters:** `""` means "the answer is an empty string." `None` means "there is no
answer." Different bugs downstream.

---

### `503 Service Unavailable` (httpbin)

**Meaning:** their server, not your code. httpbin's free demo is notoriously flaky.

**Fix:** use `postman-echo.com` instead.

---

### `CopyIgnoredFile: Attempting to Copy file "README.md" that is excluded by .dockerignore`

**Meaning:** the file is both ignored and copied.

**Fix:** remove it from `.dockerignore`. `pyproject.toml` references `README.md`, and
hatchling reads it during install — it's a **build input**, not documentation.

---

### `Bind for 0.0.0.0:8000 failed: port is already allocated`

**Meaning:** something else holds the port.

**Fix:**
```powershell
docker ps                              # a container?
netstat -ano | findstr :8000           # what process?
taskkill /PID <pid> /F
docker run -p 8080:8000 my-ai-app      # or just use another host port
```

---

### `GET /docs. HTTP/1.1" 404 Not Found`

**Meaning:** read the URL carefully — there's a **trailing period**. No route named `/docs.`
exists.

**Lesson:** the log told you the request *arrived* and the route *missed*. Everything else
was fine.

*(`GET /favicon.ico 404` is normal — the browser asking for a tab icon.)*

---
---

# APPENDIX D — Your Questions, Answered

*The doubts you raised during Week 1, kept because they were good ones.*

---

### "Are those numbers in the test file assumptions?"

**Yes — you invent them, deliberately.**

You pick the input, work out the correct answer **by hand from the business rule**, and write
both down. The test's job is to check that the code agrees with you. You are the oracle.

Never compute the expected value using the code you're testing — that always passes, even
when the function is completely wrong.

---

### "What if I don't write a case — say, amount 220?"

**Nothing happens.** No error, no warning. The suite passes, having never tried 220.

**Tests only prove what you wrote down.** They are samples, not proofs.

But 220 belongs to the same behaviour class as 1000 — both are "normal amounts." Testing both
adds nothing. Test one input **per behaviour**, not per number. 3–5 well-chosen cases per
function catches most real bugs.

*(There is a tool called **Hypothesis** that generates thousands of random inputs and hunts
for ones that break your rules. Not now — but it exists for when parametrize isn't enough.)*

---

### "Is pytest mandatory? My code runs without it."

**Not mandatory.** Python doesn't care. KitchenOS is live with no tests.

But "no tests" isn't "no testing" — it's **manual** testing, by you, clicking through the app.
You're already doing it. It's just slow, forgettable, and only covers what you thought to check.

**The cost shows up later:** at 50 functions, "did my change break anything?" becomes
unanswerable — and you start avoiding code you're afraid to touch.

**For AI it stops being optional.** LLMs are non-deterministic. There is no "run it and look."
Week 18's eval suite is a pytest suite.

---

### "Normal file and test file are different — how does this work in production?"

```
src/my_ai_app/   ← YOUR APP. Ships. Runs 24/7.
tests/           ← NEVER ships. Laptop and CI only.
```

| Moment | Runs? |
|---|---|
| While coding | ✅ `uv run pytest` |
| Before pushing | ✅ |
| After pushing | ✅ automatic (CI) |
| Deploying | ❌ |
| Serving users | ❌ |

**Tests are a gate you pass through on the way to deploying — never something that deploys
with you.** That's what `uv add --dev` and `uv sync --no-dev` encode.

---

### "How did GitHub know something would break?"

**It doesn't know anything.** GitHub rents an empty Linux machine, downloads only what you
committed, and runs the checks *you already wrote*.

CI adds two things, neither of them intelligence:

1. **Automation** — you forget; it doesn't
2. **A clean machine** — your laptop has accumulated state it can never tell you about

---

### "Should I add pytest to KitchenOS now?"

**No — around Week 6.**

Right now you'd be learning pytest *and* fighting import paths *and* setting up a test
database, inside a codebase not structured for testing. Three hard things at once, none of
them the thing you're trying to learn.

By Week 6 you'll have written ~40 tests and it becomes a two-hour job instead of two days.

**One thing to do now:** next time you touch KitchenOS's GST function, notice that you verify
it by clicking through the UI. Just notice it.

---

### "Should I deploy to Railway now?"

**No.** You've already deployed on Railway — the step teaches you nothing new. Docker and CI
were the new parts, and both run locally.

**Week 6**, when you have a real ML product worth putting online.

---

### "Mini-GPT — am I building something like Claude?"

**No, and you can't.** Frontier models cost $50–100M in compute and teams of 100+.

**What you *can* do — and will:**

| | Claude | Your Week 10 GPT |
|---|---|---|
| Parameters | Hundreds of billions | ~10 million |
| Training data | Trillions of tokens | ~1 MB |
| Hardware | Thousands of GPUs | Free Colab |
| Time | Months | ~20 minutes |

**The architecture is identical.** Same attention, same embeddings, same training loop. Go-kart
and Formula 1 — different scale, same physics.

---

### "Then why download Llama in Week 14 if I built a GPT in Week 10?"

**Week 10** = building an engine from raw metal. You now understand engines.

**Week 14** = you need to actually drive somewhere. You don't forge a new engine — you take a
working one and tune it.

| | Week 10 | Week 14 |
|---|---|---|
| Starting weights | Random noise | Already knows language |
| You train | Everything | Just LoRA adapters |
| Purpose | **Understanding** | **A working product** |

Week 10 makes Week 14 make sense. Without it, LoRA is magic you copy from a tutorial.

---

### "If I use Llama, am I just using someone else's API?"

**No.** Three different things:

| | What it is | Yours? |
|---|---|---|
| **API** (Groq, Claude) | Model on *their* computer. You send text, get text. | ❌ Renting |
| **Downloading** (Hugging Face) | Model file on *your* disk. You modify its weights. | ✅ Owning |
| **From scratch** (Week 10) | You write the architecture. Random weights. | ✅ Built by you |

You used Groq's `llama-versatile` API — that was renting. Week 14 is owning. Same model name,
completely different thing. **No API key, no account, runs on free Colab.**

---
---

# APPENDIX E — Glossary

| Term | Meaning |
|---|---|
| **Virtual environment** | A private Python installation for one project |
| **Package** | A folder Python can import from — needs `__init__.py` |
| **Lockfile** | Exact versions of every dependency, and *their* dependencies |
| **Type hint** | A label declaring what kind of data something is |
| **Linter** | A tool that finds problems in code |
| **Formatter** | A tool that standardises spacing and layout |
| **Static analysis** | Checking code without running it |
| **Decorator** (`@`) | Wraps the function below it with extra behaviour |
| **Fixture** | A pytest setup function, injected into tests by name |
| **Parametrize** | Run one test function many times with different inputs |
| **Mocking** | Replacing a real dependency with a fake one during tests |
| **Coverage** | The percentage of your code that tests actually execute |
| **Regression** | A bug reintroduced into previously working code |
| **Coroutine** | A pausable function created by `async def` |
| **Event loop** | The scheduler that runs and resumes coroutines |
| **I/O-bound** | Limited by waiting (network, disk) — async helps |
| **CPU-bound** | Limited by computation — async does not help |
| **Concurrency** | Many tasks in progress, interleaved |
| **Parallelism** | Many tasks running at literally the same instant |
| **Endpoint** | A URL your API responds to |
| **Path parameter** | A variable inside the URL: `/dishes/{id}` |
| **Schema** | The declared shape of data |
| **Serialisation** | Converting Python objects to JSON |
| **Dependency injection** | The framework supplies what your function needs |
| **Status code** | 200 ok · 201 created · 401 unauthorised · 404 not found · 422 invalid |
| **Image** | A Docker blueprint |
| **Container** | A running instance of an image |
| **Layer** | One cached step of a Docker build |
| **Multi-stage build** | Build in one image, ship from a clean one |
| **Port mapping** | `host:container` — where you reach the container |
| **CI** | Continuous Integration — automated checks on every push |
| **Workflow** | A CI configuration file |
| **Runner** | The fresh VM that executes CI |

---
---

# APPENDIX F — One Page Per Day

*For revision. Read this when you need to remember, not learn.*

---

### DAY 1 — Environment

```
uv init <name>        create project
uv add <pkg>          install + record
uv run python -m my_ai_app.main
```

`pyproject.toml` = what you need · `uv.lock` = exact versions
`src/my_ai_app/` = underscores · `__init__.py` = empty but required
`[build-system]` = makes tests able to import your code

**⚠️ Define functions ABOVE `if __name__ == "__main__":`**

---

### DAY 2 — Git

```
git add .  →  git commit -m "feat: ..."  →  git push
```

Working Dir → *(git add)* → Staging → *(git commit)* → Repository

Prefixes: `feat:` `fix:` `docs:` `test:` `refactor:` `chore:`

**⚠️ Before every commit:**
```
git rev-parse --show-toplevel     which repo am I in?
git status                        what am I committing?
```

`.gitignore` protects `.env` — a leaked key is found by bots in minutes.

---

### DAY 3 — Quality

```
uv run ruff check . --fix     find and fix
uv run ruff format .          standardise layout
uv run mypy src               verify type hints
```

`list[float]` · `dict[str, int]` · `str | None`
Empty containers need annotations: `counts: dict[str, int] = {}`

Ruff = **style**. Mypy = **logic**.
`""` ≠ `None` — "empty answer" vs "no answer".

---

### DAY 4 — pytest

```
uv run pytest
uv run pytest --cov=src --cov-report=term-missing
```

`assert x == y` is the whole framework.
Files `test_*.py`, functions `test_*()` — or silently skipped.

`@pytest.mark.parametrize` — one test, many inputs, independent results
`@pytest.fixture` — shared setup, fresh every test
`yield` in a fixture — setup, run test, teardown
`conftest.py` — fixtures shared across files
`pytest.approx()` — comparing floats
`pytest.raises()` — testing that errors happen
`monkeypatch` — fake the LLM so tests are free and fast

**Never loop inside a test. Never compute the expected value with the code under test.**

---

### DAY 5 — async

```
async def f()             creates a coroutine (does NOT run)
await f()                 runs it, releases control while waiting
asyncio.run(main())       starts the event loop — ONCE
asyncio.gather(a, b, c)   concurrent, results in order
```

**I/O-bound → async helps. CPU-bound → it does not.**

⚠️ `time.sleep()` inside `async def` freezes the **entire** loop.
⚠️ Missing `await` → "coroutine was never awaited".
✅ Always set `timeout=`.

10 users × 3s LLM call: sync = 30s for the last one. Async = 3s for all.

---

### DAY 6 — FastAPI

```
uv run uvicorn my_ai_app.api:app --reload
→ http://127.0.0.1:8000/docs
```

`@app.get` `@app.post` · `dish: DishRequest` does all validation
`response_model=` filters output · `raise HTTPException(404, "...")`
`Depends()` = pytest fixture, for endpoints
`TestClient(app)` = test endpoints with no server

⚠️ `/dishes` must be declared before `/dishes/{id}`
⚠️ Two models — one for request, one for response
⚠️ JSON has no int keys: `{1: "x"}` → `{"1": "x"}`

---

### DAY 7 — Docker + CI

```
docker build -t my-ai-app .
docker run -p 8080:8000 my-ai-app     # host:container
```

Image = blueprint · Container = running instance
Copy `pyproject.toml` **before** `src/` → layer caching
Two stages → half the size, no build tools shipped
`--host 0.0.0.0` is **mandatory** inside containers

`.github/workflows/ci.yml` — exact path, two-space YAML

**CI = a fresh empty Linux VM running the checks you already wrote.**
No magic. Just automation you can't forget, and a machine that can't lie to you.

---
---

# WEEK 1 CHECKLIST

You can now do these unaided:

- [ ] Create an isolated Python project with `uv`
- [ ] Explain what `pyproject.toml` and `uv.lock` each do
- [ ] Structure a package so tests can import it
- [ ] Use Git confidently — and verify which repo you're in first
- [ ] Write type hints, including `str | None` and generic containers
- [ ] Run ruff and mypy, and read what they tell you
- [ ] Write a test with `assert`
- [ ] Use `parametrize` instead of copy-pasting tests
- [ ] Use a fixture instead of a global
- [ ] Explain the difference between I/O-bound and CPU-bound
- [ ] Write `async def` / `await` and know why it helps
- [ ] Recognise that `time.sleep()` in async code is a bug
- [ ] Build a FastAPI endpoint with Pydantic validation
- [ ] Test an endpoint with `TestClient`
- [ ] Write a multi-stage Dockerfile and explain why it's two stages
- [ ] Run your app in a container
- [ ] Set up CI that runs four quality gates on every push
- [ ] Read a traceback bottom-up
- [ ] Read a server log and tell whether the problem is yours

---

## What Week 1 actually gave you

Not "Python basics." A **workflow**:

```
write code
   ↓
ruff  →  format  →  mypy  →  pytest        four gates, locally
   ↓
git push
   ↓
CI runs the same four gates on a clean machine
   ↓
Docker packages it identically for anywhere
```

That loop does not change for the next 20 weeks. Weeks 2–6 add data and models to it. Weeks
11–16 add LLMs. Week 18 adds evals as a fifth gate.

**Everything else is content. This is the machine that carries it.**

---

**Next: Week 2 — SQL, Postgres, Pandas, Polars, and building a real ETL pipeline.**
