# FastAPI logic tier: inference and feedback only; frontend files are never served here.
import os

import psycopg

from collections import defaultdict, deque
from datetime import datetime, timezone
import json
import re
import sys
from pathlib import Path
from time import monotonic
from uuid import uuid4

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError

from pydantic import BaseModel, Field
from gemini import generate_advisory

PROJECT_ROOT = Path("/workspace")

RESULTS_DIR = PROJECT_ROOT / "results"


try:
    from src.pipeline import AdvisoryPipeline

    PIPELINE = AdvisoryPipeline()
    MODEL_LOADED = PIPELINE.intent_model is not None
except Exception:
    PIPELINE = None
    MODEL_LOADED = False

app = FastAPI(title="FLoraAI Advisory API", version="1.0.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost",
        "http://localhost:8000",
        "http://127.0.0.1",
        "http://127.0.0.1:8000",
    ],
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"],
)

_request_times = defaultdict(deque)
_WINDOW_SECONDS = 60
_MAX_REQUESTS = 30
SUPPORTED_LANGUAGES = ["en", "hi", "mr", "gu", "pa", "kn"]
SUGGESTION_LABELS = {
    "en": "You can ask next",
    "hi": "आप आगे यह पूछ सकते हैं",
    "mr": "तुम्ही पुढे हे विचारू शकता",
    "gu": "તમે આગળ આ પૂછી શકો છો",
    "pa": "ਤੁਸੀਂ ਅੱਗੇ ਇਹ ਪੁੱਛ ਸਕਦੇ ਹੋ",
    "kn": "ನೀವು ಮುಂದೆ ಇದನ್ನು ಕೇಳಬಹುದು",
}


class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=500)
    lang: str = Field(default="en")
    session_id: str = Field(default="", max_length=100)


class FeedbackRequest(BaseModel):
    request_id: str = Field(min_length=1, max_length=100)
    action: str = Field(pattern="^(accept|override)$")
    override_text: str | None = Field(default=None, max_length=500)


def clean_text(value: str) -> str:
    return re.sub(r"[\x00-\x1f\x7f]", "", value).strip()


def check_rate_limit(request: Request) -> None:
    client_ip = request.client.host if request.client else "unknown"
    now = monotonic()
    timestamps = _request_times[client_ip]
    while timestamps and now - timestamps[0] > _WINDOW_SECONDS:
        timestamps.popleft()
    if len(timestamps) >= _MAX_REQUESTS:
        raise HTTPException(status_code=429, detail="Too many requests. Please wait a moment.")
    timestamps.append(now)


def slot_spans(message: str, slots: dict) -> list[dict]:
    spans = []
    occupied = []
    for label, text in slots.items():
        if not text:
            continue
        match = re.search(re.escape(str(text)), message, flags=re.IGNORECASE)
        if not match:
            continue
        start, end = match.span()
        if any(start < other_end and end > other_start for other_start, other_end in occupied):
            continue
        occupied.append((start, end))
        spans.append({"label": label, "text": str(text), "start": start, "end": end})
    return sorted(spans, key=lambda item: item["start"])


def next_suggestions(message: str, lang: str) -> list[str]:
    """Return localized follow-up questions related to the current topic."""
    query = message.lower()
    topic = "general"
    rain_terms = [
        "rain", "rainfall", "बारिश", "वर्षा",           # en, hi
        "पाऊस", "पावसा",                                   # mr
        "વરસાદ",                                            # gu
        "ਮੀਂਹ",                                            # pa
        "ಮಳೆ",                                              # kn
    ]
    fertilizer_terms = [
        "urea", "fertilizer", "fertiliser", "dap", "npk", "खाद", "उर्वरक",  # en, hi
        "खत",                                                                  # mr
        "ખાતર",                                                                # gu
        "ਖਾਦ",                                                                 # pa
        "ಗೊಬ್ಬರ", "ರಸಗೊಬ್ಬರ",                                               # kn
    ]
    irrigation_terms = [
        "drip", "flood", "irrigation method", "सिंचाई",   # en, hi
        "सिंचन",                                            # mr
        "સિંચાઈ",                                           # gu
        "ਸਿੰਚਾਈ",                                           # pa
        "ನೀರಾವರಿ",                                          # kn
    ]
    if any(word in query for word in rain_terms):
        topic = "rain"
    elif any(word in query for word in fertilizer_terms):
        topic = "fertilizer"
    elif any(word in query for word in irrigation_terms):
        topic = "irrigation"

    suggestions = {
        "en": {
            "rain": ["How do I check soil moisture after rain?", "When should I restart irrigation?", "What are signs of excess water?"] ,
            "fertilizer": ["How should I apply fertilizer safely?", "What are signs of nutrient deficiency?", "Can I fertigate through drip irrigation?"],
            "irrigation": ["How often should I check field moisture?", "Which method suits sandy soil?", "How can I reduce water loss?"],
            "general": ["When should I irrigate after rain?", "How much urea for tillering stage?", "Drip vs flood irrigation?"],
        },
        "hi": {
            "rain": ["बारिश के बाद मिट्टी की नमी कैसे जांचें?", "सिंचाई कब शुरू करनी चाहिए?", "अधिक पानी के लक्षण क्या हैं?"],
            "fertilizer": ["खाद सुरक्षित तरीके से कैसे डालें?", "पोषक तत्वों की कमी के लक्षण क्या हैं?", "क्या ड्रिप से फर्टिगेशन कर सकते हैं?"],
            "irrigation": ["खेत की नमी कितनी बार जांचें?", "रेतीली मिट्टी के लिए कौन-सी विधि ठीक है?", "पानी की बर्बादी कैसे कम करें?"],
            "general": ["बारिश के बाद सिंचाई कब करें?", "कल्ले निकलने की अवस्था में यूरिया कैसे दें?", "ड्रिप और फ्लड सिंचाई में क्या अंतर है?"],
        },
        "mr": {
            "rain": ["पावसानंतर जमिनीतील ओलावा कसा तपासावा?", "सिंचन पुन्हा कधी सुरू करावे?", "अतिरिक्त पाण्याची लक्षणे कोणती?"],
            "fertilizer": ["खत सुरक्षितपणे कसे द्यावे?", "पोषक कमतरतेची लक्षणे कोणती?", "ठिबक सिंचनातून खत देता येते का?"],
            "irrigation": ["शेतातील ओलावा किती वेळा तपासावा?", "वालुकामय जमिनीसाठी कोणती पद्धत योग्य?", "पाण्याची नासाडी कशी कमी करावी?"],
            "general": ["पावसानंतर सिंचन कधी करावे?", "फुटवे अवस्थेत युरिया कसा द्यावा?", "ठिबक आणि पाट सिंचनात काय फरक आहे?"],
        },
        "gu": {
            "rain": ["વરસાદ પછી જમીનની ભેજ કેવી રીતે તપાસવી?", "સિંચાઈ ફરી ક્યારે શરૂ કરવી?", "વધુ પાણીના સંકેતો કયા છે?"],
            "fertilizer": ["ખાતર સુરક્ષિત રીતે કેવી રીતે આપવું?", "પોષક તત્વોની ઉણપના સંકેતો કયા છે?", "શું ડ્રિપથી ફર્ટિગેશન કરી શકાય?"],
            "irrigation": ["ખેતરની ભેજ કેટલી વાર તપાસવી?", "રેતાળ જમીન માટે કઈ પદ્ધતિ યોગ્ય છે?", "પાણીનો બગાડ કેવી રીતે ઘટાડવો?"],
            "general": ["વરસાદ પછી સિંચાઈ ક્યારે કરવી?", "ટિલરિંગ તબક્કે યુરિયા કેવી રીતે આપવું?", "ડ્રિપ અને ફ્લડ સિંચાઈમાં શું તફાવત છે?"],
        },
        "pa": {
            "rain": ["ਮੀਂਹ ਤੋਂ ਬਾਅਦ ਮਿੱਟੀ ਦੀ ਨਮੀ ਕਿਵੇਂ ਜਾਂਚੀਏ?", "ਸਿੰਚਾਈ ਦੁਬਾਰਾ ਕਦੋਂ ਸ਼ੁਰੂ ਕਰੀਏ?", "ਵੱਧ ਪਾਣੀ ਦੇ ਲੱਛਣ ਕੀ ਹਨ?"],
            "fertilizer": ["ਖਾਦ ਸੁਰੱਖਿਅਤ ਢੰਗ ਨਾਲ ਕਿਵੇਂ ਪਾਈਏ?", "ਪੋਸ਼ਕ ਤੱਤਾਂ ਦੀ ਘਾਟ ਦੇ ਲੱਛਣ ਕੀ ਹਨ?", "ਕੀ ਡ੍ਰਿਪ ਰਾਹੀਂ ਫਰਟੀਗੇਸ਼ਨ ਕਰ ਸਕਦੇ ਹਾਂ?"],
            "irrigation": ["ਖੇਤ ਦੀ ਨਮੀ ਕਿੰਨੀ ਵਾਰ ਜਾਂਚੀਏ?", "ਰੇਤੀਲੀ ਮਿੱਟੀ ਲਈ ਕਿਹੜਾ ਤਰੀਕਾ ਠੀਕ ਹੈ?", "ਪਾਣੀ ਦੀ ਬਰਬਾਦੀ ਕਿਵੇਂ ਘਟਾਈਏ?"],
            "general": ["ਮੀਂਹ ਤੋਂ ਬਾਅਦ ਸਿੰਚਾਈ ਕਦੋਂ ਕਰੀਏ?", "ਟਿਲਰਿੰਗ ਪੜਾਅ ਵਿੱਚ ਯੂਰੀਆ ਕਿਵੇਂ ਪਾਈਏ?", "ਡ੍ਰਿਪ ਅਤੇ ਹੜ੍ਹ ਸਿੰਚਾਈ ਵਿੱਚ ਕੀ ਫਰਕ ਹੈ?"],
        },
        "kn": {
            "rain": ["ಮಳೆಯ ನಂತರ ಮಣ್ಣಿನ ತೇವಾಂಶವನ್ನು ಹೇಗೆ ಪರಿಶೀಲಿಸುವುದು?", "ನೀರಾವರಿಯನ್ನು ಮತ್ತೆ ಯಾವಾಗ ಪ್ರಾರಂಭಿಸಬೇಕು?", "ಹೆಚ್ಚಿನ ನೀರಿನ ಲಕ್ಷಣಗಳು ಯಾವುವು?"],
            "fertilizer": ["ರಸಗೊಬ್ಬರವನ್ನು ಸುರಕ್ಷಿತವಾಗಿ ಹೇಗೆ ಹಾಕುವುದು?", "ಪೋಷಕಾಂಶಗಳ ಕೊರತೆಯ ಲಕ್ಷಣಗಳು ಯಾವುವು?", "ಡ್ರಿಪ್ ಮೂಲಕ ಫರ್ಟಿಗೇಶನ್ ಮಾಡಬಹುದೇ?"],
            "irrigation": ["ಹೊಲದ ತೇವಾಂಶವನ್ನು ಎಷ್ಟು ಬಾರಿ ಪರಿಶೀಲಿಸಬೇಕು?", "ಮರಳು ಮಣ್ಣಿಗೆ ಯಾವ ವಿಧಾನ ಸೂಕ್ತ?", "ನೀರಿನ ನಷ್ಟವನ್ನು ಹೇಗೆ ಕಡಿಮೆ ಮಾಡುವುದು?"],
            "general": ["ಮಳೆಯ ನಂತರ ನೀರಾವರಿ ಯಾವಾಗ ಮಾಡಬೇಕು?", "ಟಿಲ್ಲರಿಂಗ್ ಹಂತದಲ್ಲಿ ಯೂರಿಯಾವನ್ನು ಹೇಗೆ ಹಾಕಬೇಕು?", "ಡ್ರಿಪ್ ಮತ್ತು ಫ್ಲಡ್ ನೀರಾವರಿಯಲ್ಲಿ ಏನು ವ್ಯತ್ಯಾಸ?"],
        },
    }
    return suggestions.get(lang, suggestions["en"])[topic]


def mock_response(message: str, lang: str) -> dict:
    advisory_by_language = {
        "en": "Check field moisture and verify the irrigation decision with a local agronomist.",
        "hi": "यह डेमो सलाह है। खेत की नमी और स्थानीय कृषि विशेषज्ञ की सलाह देखकर सिंचाई का निर्णय लें।",
        "mr": "हा डेमो सल्ला आहे. शेतातील ओलावा तपासा आणि स्थानिक कृषी तज्ज्ञांच्या सल्ल्याने सिंचनाचा निर्णय घ्या.",
        "gu": "આ ડેમો સલાહ છે. જમીનની ભેજ તપાસો અને સ્થાનિક કૃષિ નિષ્ણાતની સલાહથી સિંચાઈનો નિર્ણય લો.",
        "pa": "ਇਹ ਡੈਮੋ ਸਲਾਹ ਹੈ। ਖੇਤ ਦੀ ਨਮੀ ਜਾਂਚੋ ਅਤੇ ਸਥਾਨਕ ਖੇਤੀ ਮਾਹਿਰ ਦੀ ਸਲਾਹ ਨਾਲ ਸਿੰਚਾਈ ਦਾ ਫੈਸਲਾ ਕਰੋ.",
        "kn": "ಇದು ಡೆಮೊ ಸಲಹೆಯಾಗಿದೆ. ಹೊಲದ ತೇವಾಂಶವನ್ನು ಪರಿಶೀಲಿಸಿ ಮತ್ತು ಸ್ಥಳೀಯ ಕೃಷಿ ತಜ್ಞರ ಸಲಹೆಯೊಂದಿಗೆ ನೀರಾವರಿ ನಿರ್ಧಾರ ತೆಗೆದುಕೊಳ್ಳಿ.",
    }
    advisory = advisory_by_language.get(lang, advisory_by_language["en"])
    intent = "General Query"
    return {
        "intent": intent,
        "confidence": 0.0,
        "slots": [],
        "advisory": advisory,
        "advisory_source": "template",
        "demo_data": True,
        "suggestions": next_suggestions(message, lang),
        "suggestions_label": SUGGESTION_LABELS.get(lang, SUGGESTION_LABELS["en"]),
    }


@app.exception_handler(RequestValidationError)
async def validation_error_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(status_code=422, content={"detail": "Please provide a valid message and language."})


@app.get("/api/health")
def health() -> dict:
    return {"status": "ok", "languages": SUPPORTED_LANGUAGES, "model_loaded": MODEL_LOADED}


@app.post("/api/chat")
def chat(payload: ChatRequest, request: Request) -> dict:
    check_rate_limit(request)
    message = clean_text(payload.message)
    lang = payload.lang.lower().strip()
    if not message:
        raise HTTPException(status_code=422, detail="Message cannot be empty.")
    if lang not in SUPPORTED_LANGUAGES:
        raise HTTPException(status_code=422, detail="Unsupported language selection.")

    result = mock_response(message, lang)
    if PIPELINE is not None:
        try:
            processed = PIPELINE.process(message, language=lang)
            advisory, advisory_source = generate_advisory(
                message,
                processed.get("structured_record", processed),
                lang,
                processed["advisory"],
                session_id=payload.session_id,
            )
            result = {
                "intent": processed["intent"],
                "confidence": round(float(processed["confidence"]), 4),
                "slots": slot_spans(message, processed.get("slots", {})),
                "advisory": advisory,
                "advisory_source": advisory_source,
                "demo_data": not MODEL_LOADED,
                "suggestions": next_suggestions(message, lang),
                "suggestions_label": SUGGESTION_LABELS.get(lang, SUGGESTION_LABELS["en"]),
            }
        except Exception as exc:
            print(f"[Pipeline] Error during processing: {exc}", file=sys.stderr)
            result = mock_response(message, lang)

    return {"request_id": str(uuid4()), **result, "lang": lang}



DATABASE_URL = os.environ["DATABASE_URL"]


def store_feedback(payload: FeedbackRequest) -> None:
    with psycopg.connect(DATABASE_URL) as connection:
        connection.execute(
            "INSERT INTO feedback (timestamp, request_id, action, override_text) VALUES (%s, %s, %s, %s)",
            (datetime.now(timezone.utc), payload.request_id, payload.action, clean_text(payload.override_text or "") or None),
        )


@app.post("/api/feedback")
def feedback(payload: FeedbackRequest) -> dict:
    if payload.action == "override" and not clean_text(payload.override_text or ""):
        raise HTTPException(status_code=422, detail="Override feedback needs corrected advice.")
    try:
        store_feedback(payload)
    except psycopg.Error as exc:
        raise HTTPException(status_code=503, detail="Feedback storage is unavailable.") from exc
    return {"ok": True}
