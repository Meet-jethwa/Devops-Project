# Gemini advisory helper; it exists to generate localized text with Gemini.
# Analogy: this is a translator who turns a field note into a farmer-friendly answer.
import json
import os
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


# In-memory session history: session_id -> list of {"user": str, "assistant": str}
SESSION_HISTORIES: dict[str, list[dict[str, str]]] = {}
MAX_SESSION_HISTORY = 4


def get_session_history(session_id: str) -> list[dict[str, str]]:
    if not session_id:
        return []
    return SESSION_HISTORIES.get(session_id, [])


def append_session_turn(session_id: str, user_msg: str, assistant_msg: str):
    if not session_id or not user_msg or not assistant_msg:
        return
    history = SESSION_HISTORIES.setdefault(session_id, [])
    history.append({"user": user_msg.strip(), "assistant": assistant_msg.strip()})
    if len(history) > MAX_SESSION_HISTORY:
        SESSION_HISTORIES[session_id] = history[-MAX_SESSION_HISTORY:]


def generate_advisory(
    message: str, recommendation: dict, lang: str, fallback: str, session_id: str = ""
) -> tuple[str, str]:
    """Ask Gemini for localized text and report whether Gemini or fallback won."""
    api_key = os.getenv("GEMINI_API_KEY", "").strip()
    model = os.getenv("GEMINI_MODEL", "gemini-3.5-flash").strip()
    fallback_model = os.getenv("GEMINI_FALLBACK_MODEL", "gemini-3.1-flash-lite").strip()
    gemini_timeout = float(os.getenv("GEMINI_TIMEOUT_SECONDS", "10.0"))
    if not api_key or api_key == "my_api_key":
        append_session_turn(session_id, message, fallback)
        return fallback, "template"

    history = get_session_history(session_id)
    history_section = ""
    if history:
        history_section = "Recent conversation context:\n" + "\n".join(
            f"User: {h['user']}\nAssistant: {h['assistant']}" for h in history
        ) + "\n\n"

    prompt = (
        "Answer the user's question directly, concisely, and accurately as FLoraAI, an expert sugarcane farming assistant. "
        "Return only the answer without greetings, labels, or sign-offs. "
        f"Write in the requested language code '{lang}' (do not translate it to another language). "
        "If the user is asking a follow-up question (e.g., 'what is the issue?', 'why?'), use the previous conversation context to address it specifically. "
        "Use the recommendation context only when it is relevant to the question; never answer an unrelated question with an irrigation or soil-moisture message. "
        "If the question asks about harvesting or cutting sugarcane, provide clear maturity signs (months, leaf drying, brix/sweetness) and cutting instructions. "
        "If the question asks for a definition, explain the term plainly. "
        "If it asks for a farming recommendation, include a practical answer and a safety caveat where appropriate. "
        "Sensor and weather values are simulated demo values. Do not invent measurements, fertilizer doses, or guarantees.\n\n"
        f"{history_section}"
        f"User question: {message}\n"
        f"Recommendation context: {json.dumps(recommendation, ensure_ascii=False)}"
    )
    body = json.dumps({
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {
            "temperature": 0.2,
            "maxOutputTokens": 800,
            "thinkingConfig": {"thinkingBudget": 0},
        },
    }).encode("utf-8")
    candidate_models = []
    for m in [model, fallback_model, "gemini-3.5-flash", "gemini-3.1-flash-lite", "gemini-3.8-flash"]:
        if m and m not in candidate_models and m != "gemini-2.5-flash":
            candidate_models.append(m)

    for selected_model in candidate_models:
        url = (
            "https://generativelanguage.googleapis.com/v1beta/models/"
            f"{selected_model}:generateContent?key={api_key}"
        )
        try:
            request = Request(url, data=body, headers={"Content-Type": "application/json"}, method="POST")
            with urlopen(request, timeout=gemini_timeout) as response:
                result = json.loads(response.read().decode("utf-8"))
            candidate = result["candidates"][0]
            parts = candidate.get("content", {}).get("parts", [])
            text = "".join(p.get("text", "") for p in parts).strip()
            if text:
                append_session_turn(session_id, message, text)
                return text, "gemini"
        except (HTTPError, URLError, TimeoutError, KeyError, IndexError, ValueError) as exc:
            print(f"[Gemini] Model {selected_model} unavailable: {exc}", flush=True)

    append_session_turn(session_id, message, fallback)
    return fallback, "template"
