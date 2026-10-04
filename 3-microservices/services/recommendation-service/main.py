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
    rain = SIMULATED_CONTEXT["rain_expected"]
    moisture = SIMULATED_CONTEXT["soil_moisture_pct"]
    action = "skip_irrigation" if rain or moisture >= 55 else "irrigate"
    return {"action": action, "when": "morning", "duration_hours": 2 if action == "irrigate" else 0,
            "rain_expected": rain, "fertigation": query.intent.lower() == "fertilizer use",
            "sensor_weather": SIMULATED_CONTEXT, "demo_data": True}
