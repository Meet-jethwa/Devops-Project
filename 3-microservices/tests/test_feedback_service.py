# Feedback service smoke tests.
# It exists to verify the health endpoint when PostgreSQL is unavailable in unit tests.
# Analogy: check that the feedback clerk can report the database status.
from fastapi.testclient import TestClient

from conftest import load_service


def test_feedback_health():
    client = TestClient(load_service("feedback_service", "services/feedback-service/main.py").app)
    assert client.get("/health").status_code == 200
