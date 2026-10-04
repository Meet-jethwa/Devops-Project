# Phase 1 contract tests for the copied serving API.
"""Phase 1 contract tests for the copied serving API."""

import importlib.util
import sys
from pathlib import Path

from fastapi.testclient import TestClient


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
spec = importlib.util.spec_from_file_location("monolith.api", ROOT / "api.py")
api = importlib.util.module_from_spec(spec)
api.__package__ = "monolith"
api.__path__ = [str(ROOT)]
spec.loader.exec_module(api)

client = TestClient(api.app)


def test_landing_and_chat_pages():
    assert client.get("/").status_code == 200
    assert client.get("/chat").status_code == 200


def test_health_contract():
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_chat_contract():
    response = client.post("/api/chat", json={"message": "How much water?", "lang": "en"})
    body = response.json()
    assert response.status_code == 200
    assert {"request_id", "intent", "confidence", "slots", "advisory", "lang"} <= body.keys()


def test_feedback_contract():
    response = client.post(
        "/api/feedback",
        json={"request_id": "test-request", "action": "accept"},
    )
    assert response.status_code == 200
    assert response.json() == {"ok": True}
