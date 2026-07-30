import pandas as pd

from my_ai_app.transform import authors_to_frame, posts_to_frame


def test_posts_renames_api_fields() -> None:
    """The API says 'userId'; our table says 'user_id'."""
    df = posts_to_frame([{"id": 1, "userId": 5, "title": "T", "body": "B"}])
    assert "external_id" in df.columns
    assert "user_id" in df.columns
    assert "userId" not in df.columns


def test_posts_strips_newlines_from_body() -> None:
    """Post bodies arrive with literal newlines. They must not survive."""
    df = posts_to_frame([{"id": 1, "userId": 1, "title": "T", "body": "a\nb\nc"}])
    assert "\n" not in df.loc[0, "body"]


def test_posts_counts_words() -> None:
    """Word counts are derived, not guessed."""
    df = posts_to_frame(
        [{"id": 1, "userId": 1, "title": "one two three", "body": "a b c d"}]
    )
    assert df.loc[0, "title_words"] == 3
    assert df.loc[0, "body_words"] == 4


def test_posts_drops_duplicate_ids() -> None:
    """Two rows claiming the same external_id would break the upsert."""
    df = posts_to_frame(
        [
            {"id": 1, "userId": 1, "title": "A", "body": "x"},
            {"id": 1, "userId": 1, "title": "B", "body": "y"},
        ]
    )
    assert len(df) == 1


def test_authors_flattens_nested_json() -> None:
    """company.name and address.city become flat columns."""
    df = authors_to_frame(
        [
            {
                "id": 3,
                "name": "Clementine Bauch",
                "username": "Samantha",
                "email": "Nathan@Yesenia.NET",
                "address": {"city": "McKenziehaven"},
                "company": {"name": "Romaguera-Jacobson"},
            }
        ]
    )
    assert df.loc[0, "company"] == "Romaguera-Jacobson"
    assert df.loc[0, "city"] == "McKenziehaven"


def test_authors_survives_missing_nested_fields() -> None:
    """A real API will omit fields. We must not crash."""
    df = authors_to_frame([{"id": 1, "name": "X", "username": "x", "email": "x@y.com"}])
    assert pd.isna(df.loc[0, "company"])
    assert pd.isna(df.loc[0, "city"])


def test_authors_lowercases_email() -> None:
    """Emails are matched case-insensitively downstream."""
    df = authors_to_frame(
        [{"id": 1, "name": "X", "username": "x", "email": "MiXeD@Case.COM"}]
    )
    assert df.loc[0, "email"] == "mixed@case.com"
