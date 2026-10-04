# Phase 3 recommendation service: inputs are explicitly simulated demo data.
"""Deterministic recommendation from labelled simulated sensor/weather values."""

from typing import Any
from fastapi import FastAPI, Request
from pydantic import BaseModel, Field

app = FastAPI(title="Recommendation service", version="3.0.0")
SIMULATED_CONTEXT = {"soil_moisture_pct": 38, "rain_expected": False, "temperature_c": 29,
                     "source": "SIMULATED SENSOR/WEATHER DICTIONARY"}


class Query(BaseModel):
    intent: str = "General Query"
    slots: dict[str, str] = {}


@app.middleware("http")
async def request_log(request: Request, call_next):
    response = await call_next(request)
    print(
        f"request_id={request.headers.get('X-Request-ID', '-')} "
        f"path={request.url.path} status={response.status_code}",
        flush=True,
    )
    return response


@app.get("/health")
def health() -> dict[str, Any]:
    return {"status": "ok", "service": "recommendation-service", "demo_data": True}


@app.post("/recommend")
def recommend(query: Query) -> dict[str, Any]:
    normalized_intent = query.intent.lower()
    normalized_slots = {key.upper(): str(value).lower() for key, value in query.slots.items()}
    fertilizer = any(term in normalized_intent for term in
                     ("fertilizer", "fertiliser", "fertigation", "nutrient"))
    weather_slot = any(key in normalized_slots for key in ("RAIN", "WEATHER"))
    rain = SIMULATED_CONTEXT["rain_expected"] or weather_slot
    moisture = SIMULATED_CONTEXT["soil_moisture_pct"]
    if fertilizer:
        action = "skip_irrigation"
        duration = 0
        reason = "Give fertilizer guidance without choosing irrigation hours."
    elif rain:
        action = "skip_irrigation"
        duration = 0
        reason = "Check soil moisture first because rain or weather information was provided."
    elif moisture < 20:
        action = "irrigate"
        duration = 4
        reason = "Simulated soil moisture is low."
    elif moisture >= 35:
        action = "skip_irrigation"
        duration = 0
        reason = "Simulated soil moisture is adequate."
    else:
        action = "irrigate"
        duration = 2
        reason = "Use the simulated soil-moisture rule."
    return {"action": action, "when": "morning", "duration_hours": duration,
            "rain_expected": rain, "fertigation": fertilizer,
            "reason": reason,
            "sensor_weather": SIMULATED_CONTEXT, "demo_data": True}
