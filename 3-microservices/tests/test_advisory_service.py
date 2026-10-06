# Advisory service smoke tests.
# It exists to verify the health and text generation endpoints.
# Analogy: check that the adviser can turn a decision into plain words.
import json

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


def test_sugarcane_definition_handles_common_misspelling():
    client = TestClient(load_service("advisory_service_definition", "services/advisory-service/main.py").app)
    response = client.post(
        "/generate",
        json={"message": "what is sugercane", "recommendation": {"action": "skip_irrigation"}, "lang": "en"},
    )
    assert response.status_code == 200
    assert "tropical grass" in response.json()["advisory"]


def test_gemini_prompt_contains_question_and_language(monkeypatch):
    module = load_service("advisory_service_prompt", "services/advisory-service/main.py")
    captured = {}

    class Response:
        def read(self):
            return '{"candidates":[{"content":{"parts":[{"text":"उत्तर"}]}}]}'.encode()

        def __enter__(self):
            return self

        def __exit__(self, *args):
            return False

    def fake_urlopen(request, timeout):
        captured["body"] = request.data.decode("utf-8")
        return Response()

    monkeypatch.setenv("GEMINI_API_KEY", "test-key")
    monkeypatch.setenv("GEMINI_MODEL", "gemini-3.8-flash")
    monkeypatch.setattr(module, "urlopen", fake_urlopen)

    text, source = module.generate_gemini_advisory(
        "ड्रिप और फ्लड सिंचाई में क्या अंतर है?",
        {"action": "skip_irrigation"},
        "hi",
        "fallback",
    )

    assert source == "gemini"
    assert text == "उत्तर"
    prompt = json.loads(captured["body"])["contents"][0]["parts"][0]["text"]
    assert "ड्रिप और फ्लड सिंचाई" in prompt
    assert "language code 'hi'" in prompt


def test_unrelated_question_does_not_use_irrigation_fallback():
    client = TestClient(load_service("advisory_service_unrelated", "services/advisory-service/main.py").app)
    response = client.post(
        "/generate",
        json={"message": "what is plant?", "recommendation": {"action": "skip_irrigation"}, "lang": "en"},
    )
    assert response.status_code == 200
    assert "living organism" in response.json()["advisory"]


def test_yellow_leaves_have_relevant_fallback():
    client = TestClient(load_service("advisory_service_yellow", "services/advisory-service/main.py").app)
    response = client.post(
        "/generate",
        json={"message": "Leaves are turning yellow, why?", "recommendation": {"action": "skip_irrigation"}, "lang": "en"},
    )
    assert "Yellow leaves" in response.json()["advisory"]


def test_sugarcane_cutting_harvest_advice():
    client = TestClient(load_service("advisory_service_cutting", "services/advisory-service/main.py").app)
    response = client.post(
        "/generate",
        json={"message": "when can i cut my sugercane ?", "recommendation": {"action": "skip_irrigation"}, "lang": "en"},
    )
    assert response.status_code == 200
    advisory = response.json()["advisory"]
    # Verify that it is NOT the repetitive irrigation message
    assert "Soil moisture is adequate" not in advisory
    assert any(term in advisory.lower() for term in ["harvest", "cut", "maturity", "months", "brix"])


def test_issue_follow_up_context():
    client = TestClient(load_service("advisory_service_context", "services/advisory-service/main.py").app)
    session_id = "test-session-diag"
    # Turn 1: Yellow leaves
    client.post(
        "/generate",
        json={"message": "Leaves are turning yellow, why?", "recommendation": {"action": "skip_irrigation"}, "lang": "en", "session_id": session_id},
    )
    # Turn 2: Follow up "what is the issue?"
    response = client.post(
        "/generate",
        json={"message": "what is the issue?", "recommendation": {"action": "skip_irrigation"}, "lang": "en", "session_id": session_id},
    )
    assert response.status_code == 200
    advisory = response.json()["advisory"]
    assert "Soil moisture is adequate" not in advisory
    assert any(term in advisory.lower() for term in ["nitrogen", "yellow", "virus", "deficiency", "aeration", "issue"])
