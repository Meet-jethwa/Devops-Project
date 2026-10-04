# Advisory service smoke tests.
# It exists to verify the health and text generation endpoints.
# Analogy: check that the adviser can turn a decision into plain words.
from fastapi.testclient import TestClient

from conftest import load_service


def test_advisory_health_and_generate():
    client = TestClient(load_service("advisory_service", "services/advisory-service/main.py").app)
    assert client.get("/health").status_code == 200
    assert client.post("/generate", json={"recommendation": {"action": "irrigate"}, "lang": "en"}).status_code == 200


def test_marathi_advisory_uses_devanagari():
    client = TestClient(load_service("advisory_service_marathi", "services/advisory-service/main.py").app)
    response = client.post(
        "/generate",
        json={
            "recommendation": {
                "action": "skip_irrigation",
                "rain_expected": True,
                "fertigation": False,
            },
            "lang": "mr",
        },
    )
    assert response.status_code == 200
    assert any("\u0900" <= char <= "\u097f" for char in response.json()["advisory"])
