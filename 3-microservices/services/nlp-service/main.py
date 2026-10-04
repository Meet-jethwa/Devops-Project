# Phase 3 NLP service: reuse the saved MaxEnt, CRF and gazetteer artifacts.
"""Torch-free intent and slot extraction service."""

import os
import re
import importlib.util
from pathlib import Path
from typing import Any

import joblib
from fastapi import FastAPI, Request
from pydantic import BaseModel, Field

ROOT = Path(os.getenv("PROJECT_ROOT", "/project"))
MODEL_PATH = Path(os.getenv("MODEL_PATH", ROOT / "results" / "baseline_maxent_model.joblib"))
CRF_MODEL_PATH = Path(os.getenv("CRF_MODEL_PATH", ROOT / "results" / "crf_slot_tagger.joblib"))
app = FastAPI(title="NLP service", version="3.0.0")
try:
    MODEL = joblib.load(MODEL_PATH)
except Exception:
    MODEL = None
try:
    CRF_MODEL = joblib.load(CRF_MODEL_PATH)
except Exception:
    CRF_MODEL = None

gazetteer_path = Path(__file__).with_name("gazetteer.py")
if not gazetteer_path.exists():
    gazetteer_path = Path(__file__).resolve().parents[3] / "1-monolith" / "gazetteer.py"
gazetteer_spec = importlib.util.spec_from_file_location("serving_gazetteer", gazetteer_path)
gazetteer_module = importlib.util.module_from_spec(gazetteer_spec)
assert gazetteer_spec.loader is not None
gazetteer_spec.loader.exec_module(gazetteer_module)


@app.middleware("http")
async def request_log(request: Request, call_next):
    response = await call_next(request)
    print(
        f"request_id={request.headers.get('X-Request-ID', '-')} "
        f"path={request.url.path} status={response.status_code}",
        flush=True,
    )
    return response

GAZETTEER = {
    "CROP": ["sugarcane", "cane", "गन्ना", "गन्ने", "ईख"],
    "STAGE": ["germination", "tillering", "maturity", "planting", "कल्ले", "परिपक्वता"],
    "TIME": ["morning", "evening", "today", "tomorrow", "सुबह", "शाम", "आज", "कल"],
    "SOIL_ISSUE": ["waterlogging", "salinity", "drought", "dry soil", "जलभराव", "सूखा"],
}
PATTERNS = {
    "DURATION": r"\b\d+(?:\.\d+)?\s*(?:hours?|hrs?|days?|दिन|घंटे)\b",
    "QUANTITY": r"\b\d+(?:\.\d+)?\s*(?:kg|kgs|liters?|bags?|किलो|लीटर|बोरी)\b",
    "PLOT_AREA": r"\b\d+(?:\.\d+)?\s*(?:acres?|hectares?|एकड़|हेक्टेयर)\b",
}


class Query(BaseModel):
    message: str = Field(min_length=1, max_length=500)
    lang: str = "en"


def slots(text: str) -> dict[str, str]:
    tokens, gazetteer_tags = gazetteer_module.pre_label_query(text)
    tags = gazetteer_tags
    if CRF_MODEL is not None and tokens:
        try:
            features = [gazetteer_module.word2features(tokens, i) for i in range(len(tokens))]
            crf_tags = CRF_MODEL.predict([features])[0]
            if any(tag != "O" for tag in crf_tags):
                tags = crf_tags
        except Exception:
            pass
    found: dict[str, str] = {}
    current_label = None
    current_tokens: list[str] = []
    for token, tag in zip(tokens, tags):
        if tag.startswith("B-"):
            if current_label:
                found[current_label] = " ".join(current_tokens)
            current_label = tag[2:]
            current_tokens = [token]
        elif tag.startswith("I-") and current_label == tag[2:]:
            current_tokens.append(token)
        elif current_label:
            found[current_label] = " ".join(current_tokens)
            current_label = None
            current_tokens = []
    if current_label:
        found[current_label] = " ".join(current_tokens)
    return found


@app.get("/health")
def health() -> dict[str, Any]:
    return {"status": "ok", "service": "nlp-service", "model_loaded": MODEL is not None, "torch": False}


@app.post("/analyze")
def analyze(query: Query) -> dict[str, Any]:
    extracted = slots(query.message)
    if MODEL is not None:
        try:
            intent = str(MODEL.predict([query.message])[0])
            confidence = float(max(MODEL.predict_proba([query.message])[0]))
        except Exception:
            intent, confidence = "General Query", 0.0
    else:
        intent = "Irrigation" if any(x in query.message.lower() for x in ("water", "irrigat", "सिंच")) else "General Query"
        confidence = 0.2
    return {"intent": intent, "confidence": confidence, "slots": extracted, "model": "saved-maxent-or-rule",
            "crf_available": Path(os.getenv("CRF_MODEL_PATH", ROOT / "results" / "crf_slot_tagger.joblib")).exists()}
