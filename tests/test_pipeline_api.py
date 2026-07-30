from fastapi.testclient import TestClient

from my_ai_app.api import app

client = TestClient(app)


def test_stats_returns_counts() -> None:
    """The summary board reports what's on the shelves."""
    response = client.get("/stats")
    assert response.status_code == 200
    body = response.json()
    assert body["total_posts"] > 0
    assert body["total_authors"] > 0


def test_posts_respects_limit() -> None:
    """A customer gets exactly as many items as they asked for."""
    response = client.get("/posts?limit=5")
    assert response.status_code == 200
    assert len(response.json()) == 5


def test_posts_offset_returns_different_rows() -> None:
    """Asking for the next tray gives different items."""
    first = client.get("/posts?limit=3&offset=0").json()
    second = client.get("/posts?limit=3&offset=3").json()
    assert [p["external_id"] for p in first] != [p["external_id"] for p in second]


def test_limit_above_maximum_rejected() -> None:
    """The house rule holds - no one orders the whole warehouse."""
    response = client.get("/posts?limit=5000")
    assert response.status_code == 422


def test_unknown_author_returns_404() -> None:
    """A supplier not in the book gets an honest answer."""
    response = client.get("/authors/999999")
    assert response.status_code == 404


def test_author_filter_returns_only_that_author() -> None:
    """?author_id=3 means only author 3's posts."""
    response = client.get("/posts?author_id=3")
    assert response.status_code == 200
    assert all(p["user_id"] == 3 for p in response.json())


def test_response_model_hides_internal_fields() -> None:
    """fetched_at and the internal id never leave the kitchen."""
    body = client.get("/posts?limit=1").json()[0]
    assert "fetched_at" not in body
    assert set(body) == {"external_id", "user_id", "title", "body"}
