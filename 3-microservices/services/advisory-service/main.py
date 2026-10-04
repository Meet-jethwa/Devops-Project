# Phase 3 advisory service: small, localized and explainable template generation.
"""Render safe advisory text from recommendation and extracted slots."""

from typing import Any
import json
import os
from urllib.error import HTTPError, URLError
from urllib.request import Request as UrlRequest, urlopen
from fastapi import FastAPI, Request
from pydantic import BaseModel

app = FastAPI(title="Advisory service", version="3.0.0")
TEMPLATES = {
    "en": {"irrigate": "Irrigate the sugarcane field for {hours} hours in the {when}.",
           "skip_irrigation": "Skip irrigation for now and check soil moisture again.",
           "monitor": "Monitor field moisture and consult a local agronomist."},
    "hi": {"irrigate": "{when} गन्ने के खेत में {hours} घंटे सिंचाई करें।",
           "skip_irrigation": "अभी सिंचाई रोकें और मिट्टी की नमी जाँचें।",
           "monitor": "खेत की नमी देखें और स्थानीय कृषि विशेषज्ञ से सलाह लें।"},
}


class AdviceRequest(BaseModel):
    message: str = ""
    recommendation: dict[str, Any] = {}
    lang: str = "en"


def generate_gemini_advisory(
    recommendation: dict[str, Any], lang: str, fallback: str
) -> tuple[str, str]:
    """Generate localized text and report whether Gemini or fallback won."""
    api_key = os.getenv("GEMINI_API_KEY", "").strip()
    model = os.getenv("GEMINI_MODEL", "gemini-2.5-flash").strip()
    gemini_timeout = float(os.getenv("GEMINI_TIMEOUT_SECONDS", "2.0"))
    if not api_key:
        return fallback, "template"
    prompt = (
        "Write one short, clear sugarcane irrigation advisory in language code "
        f"'{lang}'. Use only this recommendation: "
        f"{json.dumps(recommendation, ensure_ascii=False)}. Sensor and weather "
        "values are simulated demo values. Do not invent measurements, doses, "
        "or guarantees. Return only the advisory text."
    )
    body = json.dumps({
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {"temperature": 0.2, "maxOutputTokens": 180},
    }).encode("utf-8")
    url = (
        "https://generativelanguage.googleapis.com/v1beta/models/"
        f"{model}:generateContent?key={api_key}"
    )
    try:
        request = UrlRequest(url, data=body, headers={"Content-Type": "application/json"}, method="POST")
        with urlopen(request, timeout=gemini_timeout) as response:
            result = json.loads(response.read().decode("utf-8"))
        text = result["candidates"][0]["content"]["parts"][0]["text"].strip()
        return (text, "gemini") if text else (fallback, "template")
    except (HTTPError, URLError, TimeoutError, KeyError, IndexError, ValueError) as exc:
        print(f"[Gemini] Advisory generation unavailable: {exc}", flush=True)
        return fallback, "template"


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
def health() -> dict[str, str]:
    return {"status": "ok", "service": "advisory-service"}


@app.post("/generate")
def advise(request: AdviceRequest, http_request: Request) -> dict[str, Any]:
    lang = request.lang if request.lang in TEMPLATES else "en"
    message = request.message.lower()
    if any(term in message for term in ["what is sugarcane", "what's sugarcane", "sugarcane meaning"]):
        local_text = {
            "en": "Sugarcane is a tall tropical grass grown mainly for its sweet juice, which is processed into sugar and other products. It needs warm weather, sunlight, and carefully managed water.",
            "hi": "गन्ना एक लंबी उष्णकटिबंधीय घास है जिसे मुख्य रूप से मीठे रस के लिए उगाया जाता है। इसी रस से चीनी और अन्य उत्पाद बनाए जाते हैं। इसे गर्म मौसम, धूप और सही जल प्रबंधन की आवश्यकता होती है।",
        }.get(lang, "Sugarcane is a tall tropical grass grown mainly for its sweet juice, which is processed into sugar and other products.")
        advisory, source = generate_gemini_advisory(
            {"topic": "sugarcane", "question": request.message},
            lang,
            local_text,
        )
        return {
            "advisory": advisory,
            "advisory_source": source,
            "suggestions": [],
            "suggestions_label": "You can ask next" if lang == "en" else "आप आगे यह पूछ सकते हैं",
        }
    action = request.recommendation.get("action", "monitor")
    template = TEMPLATES[lang].get(action, TEMPLATES[lang]["monitor"])
    text = template.format(hours=request.recommendation.get("duration_hours", 0),
                           when=request.recommendation.get("when", "today"))
    advisory, source = generate_gemini_advisory(request.recommendation, lang, text)
    print(
        f"request_id={http_request.headers.get('X-Request-ID', '-')} "
        f"advisory_source={source}",
        flush=True,
    )
    return {"advisory": advisory, "advisory_source": source,
            "suggestions": [], "suggestions_label": "You can ask next" if lang == "en" else "आप आगे यह पूछ सकते हैं"}
