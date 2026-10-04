# Gemini advisory helper; it exists to generate localized text with Gemini.
# Analogy: this is a translator who turns a field note into a farmer-friendly answer.
import json
import os
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


def generate_advisory(recommendation: dict, lang: str, fallback: str) -> tuple[str, str]:
    """Ask Gemini for localized text and report whether Gemini or fallback won."""
    api_key = os.getenv("GEMINI_API_KEY", "").strip()
    model = os.getenv("GEMINI_MODEL", "gemini-2.5-flash").strip()
    if not api_key:
        return fallback, "template"

    prompt = (
        "You are a careful sugarcane irrigation adviser. Write one short, clear "
        f"advisory in language code '{lang}'. Use only this recommendation: "
        f"{json.dumps(recommendation, ensure_ascii=False)}. "
        "Sensor and weather values are simulated demo values. Do not invent "
        "measurements, doses, guarantees, or emergency claims. Mention that "
        "field moisture should be checked and a local agronomist should confirm "
        "the decision when appropriate. Return only the advisory text."
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
        request = Request(url, data=body, headers={"Content-Type": "application/json"}, method="POST")
        with urlopen(request, timeout=8) as response:
            result = json.loads(response.read().decode("utf-8"))
        text = result["candidates"][0]["content"]["parts"][0]["text"].strip()
        return (text, "gemini") if text else (fallback, "template")
    except (HTTPError, URLError, TimeoutError, KeyError, IndexError, ValueError) as exc:
        print(f"[Gemini] Advisory generation unavailable: {exc}", flush=True)
        return fallback, "template"
