# Recommendation service smoke tests.
# It exists to verify the health and recommendation endpoints.
# Analogy: check that the field decision desk gives one answer.
from fastapi.testclient import TestClient

from conftest import load_service


def test_recommendation_health_and_call():
    client = TestClient(load_service("recommendation_service", "services/recommendation-service/main.py").app)
    assert client.get("/health").status_code == 200
    assert client.post("/recommend", json={"intent": "Water Management", "slots": {}}).status_code == 200
