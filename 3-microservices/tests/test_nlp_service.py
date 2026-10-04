# NLP service smoke tests.
# It exists to verify the health and analyze endpoints.
# Analogy: check that the translator is open and understands one sentence.
from fastapi.testclient import TestClient

from conftest import load_service


def test_nlp_health_and_analyze():
    client = TestClient(load_service("nlp_service", "services/nlp-service/main.py").app)
    assert client.get("/health").status_code == 200
    assert client.post("/analyze", json={"message": "When should I irrigate?", "lang": "en"}).status_code == 200
