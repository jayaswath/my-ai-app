from fastapi.testclient import TestClient

from my_ai_app.api import app

client = TestClient(app)


def test_health_returns_ok() -> None:
    """Health endpoint reports service status."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_list_dishes_returns_all() -> None:
    """Listing dishes returns every entry."""
    response = client.get("/dishes")
    assert response.status_code == 200
    assert response.json() == {"1": "Biryani", "2": "Dosa"}


def test_create_dish_calculates_profit() -> None:
    """Profit and margin are computed correctly."""
    response = client.post(
        "/dishes",
        json={"name": "Biryani", "selling_price": 250, "cost": 100},
    )
    assert response.status_code == 201
    assert response.json()["profit"] == 150.0
    assert response.json()["margin_percent"] == 60.0


def test_create_dish_rejects_negative_price() -> None:
    """Negative prices are rejected before reaching the handler."""
    response = client.post(
        "/dishes",
        json={"name": "Biryani", "selling_price": -50, "cost": 100},
    )
    assert response.status_code == 422


def test_gst_splits_normal_amount() -> None:
    """A ₹1000 order splits into ₹25 CGST and ₹25 SGST."""
    response = client.post("/gst", json={"amount": 1000})
    assert response.status_code == 200
    body = response.json()
    assert body["cgst"] == 25.0
    assert body["sgst"] == 25.0
    assert body["total"] == 1050.0


def test_gst_handles_zero_amount() -> None:
    """A zero amount produces zero tax."""
    response = client.post("/gst", json={"amount": 0})
    assert response.status_code == 200
    assert response.json()["total"] == 0.0


def test_gst_rejects_negative_amount() -> None:
    """Negative amounts are rejected by validation."""
    response = client.post("/gst", json={"amount": -100})
    assert response.status_code == 422
