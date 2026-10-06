# Phase 3 gateway: compose the HTTP microservices into the frontend contract.
"""Public API gateway with bounded downstream calls and graceful degradation."""

import os
import uuid
from typing import Any

import httpx
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

TIMEOUT = float(os.getenv("DOWNSTREAM_TIMEOUT_SECONDS", "15.0"))
SERVICES = {
    "nlp": os.getenv("NLP_URL", "http://nlp-service:8000"),
    "recommendation": os.getenv("RECOMMENDATION_URL", "http://recommendation-service:8000"),
    "advisory": os.getenv("ADVISORY_URL", "http://advisory-service:8000"),
    "feedback": os.getenv("FEEDBACK_URL", "http://feedback-service:8000"),
}
LANGUAGES = ["en", "hi", "mr", "gu", "pa", "kn"]
SUGGESTION_LABELS = {"en": "You can ask next", "hi": "आप आगे यह पूछ सकते हैं"}
app = FastAPI(title="FLoraAI Phase 3 Gateway", version="3.0.0")


@app.middleware("http")
async def request_log(request: Request, call_next):
    response = await call_next(request)
    print(
        f"request_id={request.headers.get('X-Request-ID', '-')} "
        f"path={request.url.path} status={response.status_code}",
        flush=True,
    )
    return response


class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=500)
    lang: str = Field(default="en")
    session_id: str = Field(default="", max_length=100)


class FeedbackRequest(BaseModel):
    request_id: str = Field(min_length=1, max_length=100)
    action: str = Field(pattern="^(accept|override)$")
    override_text: str | None = Field(default=None, max_length=500)


async def call(path: str, payload: dict[str, Any], request_id: str = "") -> dict[str, Any] | None:
    """Call a private service; returning None is the deliberate degraded path."""
    try:
        async with httpx.AsyncClient(timeout=TIMEOUT) as client:
            response = await client.post(path, json=payload,
                                         headers={"X-Request-ID": request_id} if request_id else None)
            response.raise_for_status()
            return response.json()
    except (httpx.HTTPError, ValueError):
        return None


def fallback(lang: str) -> dict[str, Any]:
    text = {
        "hi": "यह डेमो सलाह है। खेत की नमी जाँचें और स्थानीय कृषि विशेषज्ञ से पुष्टि करें।",
        "mr": "हा डेमो सल्ला आहे. जमिनीतील ओलावा तपासा आणि स्थानिक तज्ज्ञांचा सल्ला घ्या.",
    }.get(lang, "Check field moisture and confirm the decision with a local agronomist.")
    return {"intent": "General Query", "confidence": 0.0, "slots": [],
            "advisory": text, "advisory_source": "template", "demo_data": True, "suggestions": [],
            "suggestions_label": SUGGESTION_LABELS.get(lang, SUGGESTION_LABELS["en"])}


@app.get("/health")
@app.get("/api/health")
async def health() -> dict[str, Any]:
    return {"status": "ok", "service": "gateway", "languages": LANGUAGES}


@app.post("/api/chat")
async def chat(payload: ChatRequest, request: Request) -> JSONResponse:
    lang = payload.lang.lower().strip()
    request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
    if lang not in LANGUAGES:
        return JSONResponse(status_code=422, content={"detail": "Unsupported language selection."})
    nlp_response = await call(
        f"{SERVICES['nlp']}/analyze",
        {"message": payload.message, "lang": lang},
        request_id,
    )
    degraded = nlp_response is None
    nlp = nlp_response
    nlp = nlp or {"intent": "General Query", "confidence": 0.0, "slots": {}}
    recommendation = await call(
        f"{SERVICES['recommendation']}/recommend",
        {"intent": nlp["intent"], "slots": nlp["slots"]},
        request_id,
    )
    degraded = degraded or recommendation is None
    recommendation = recommendation or {"action": "monitor", "when": "today", "duration_hours": 0,
                                        "rain_expected": False, "fertigation": False, "demo_data": True}
    advisory = await call(
        f"{SERVICES['advisory']}/generate",
        {"message": payload.message, "recommendation": recommendation, "lang": lang, "session_id": payload.session_id},
        request_id,
    )
    degraded = degraded or advisory is None
    result = fallback(lang) if advisory is None else {
        "intent": nlp.get("intent", "General Query"),
        "confidence": round(float(nlp.get("confidence", 0)), 4),
        "slots": [{"label": key, "text": value} for key, value in nlp.get("slots", {}).items()],
        "advisory": advisory.get("advisory", fallback(lang)["advisory"]),
        "advisory_source": advisory.get("advisory_source", "template"),
        "demo_data": bool(recommendation.get("demo_data", True)),
        "suggestions": advisory.get("suggestions", []),
        "suggestions_label": advisory.get("suggestions_label", SUGGESTION_LABELS.get(lang, SUGGESTION_LABELS["en"])),
    }
    result["degraded"] = degraded
    return JSONResponse(content={"request_id": request_id, **result, "lang": lang}, headers={"X-Request-ID": request_id})


@app.post("/api/feedback")
async def feedback(payload: FeedbackRequest, request: Request) -> JSONResponse:
    record = payload.model_dump()
    result = await call(f"{SERVICES['feedback']}/feedback", record,
                        request.headers.get("X-Request-ID", ""))
    if result is None or not result.get("ok", False):
        return JSONResponse(status_code=202, content={"ok": True, "degraded": True})
    return JSONResponse(content={"ok": True, "degraded": False})
