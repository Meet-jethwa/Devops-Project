# Recommendation service smoke tests.
# It exists to verify the health and recommendation endpoints.
# Analogy: check that the field decision desk gives one answer.
from fastapi.testclient import TestClient

from conftest import load_service


def test_recommendation_health_and_call():
    client = TestClient(load_service("recommendation_service", "services/recommendation-service/main.py").app)
    assert client.get("/health").status_code == 200
    assert client.post("/recommend", json={"intent": "Water Management", "slots": {}}).status_code == 200


def test_fertilizer_has_no_irrigation_hours():
    client = TestClient(load_service("recommendation_service_fertilizer", "services/recommendation-service/main.py").app)
    response = client.post(
        "/recommend",
        json={"intent": "Fertilizer Use", "slots": {"STAGE": "tillering"}},
    )
    body = response.json()
    assert body["fertigation"] is True
    assert body["duration_hours"] == 0


def test_weather_slot_checks_moisture_first():
    client = TestClient(load_service("recommendation_service_weather", "services/recommendation-service/main.py").app)
    response = client.post(
        "/recommend",
        json={"intent": "Water Management", "slots": {"WEATHER": "rain"}},
    )
    body = response.json()
    assert body["action"] == "skip_irrigation"
    assert "moisture" in body["reason"].lower()
