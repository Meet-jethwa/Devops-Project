# Phase 3 advisory service: intelligent Gemini response generation with robust fallbacks.
"""Render safe, contextual advisory text and multi-turn agricultural chat."""

from typing import Any
import json
import os
import re
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request as UrlRequest, urlopen
from fastapi import FastAPI, Request
from pydantic import BaseModel

try:
    from templates import render_advisory
except ImportError:
    import importlib.util

    templates_path = Path(__file__).resolve().parents[3] / "1-monolith" / "templates.py"
    templates_spec = importlib.util.spec_from_file_location("serving_templates", templates_path)
    templates_module = importlib.util.module_from_spec(templates_spec)
    assert templates_spec.loader is not None
    templates_spec.loader.exec_module(templates_module)
    render_advisory = templates_module.render_advisory

app = FastAPI(title="Advisory service", version="3.0.0")

# In-memory session history: session_id -> list of {"user": str, "assistant": str}
SESSION_HISTORIES: dict[str, list[dict[str, str]]] = {}
MAX_SESSION_HISTORY = 4


class AdviceRequest(BaseModel):
    message: str = ""
    recommendation: dict[str, Any] = {}
    lang: str = "en"
    session_id: str = ""


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


def generate_gemini_advisory(
    message: str,
    recommendation: dict[str, Any],
    lang: str,
    fallback: str,
    session_id: str = "",
) -> tuple[str, str]:
    """Generate localized text using Gemini with multi-model cascade, thinking token budget, and fallback."""
    api_key = os.getenv("GEMINI_API_KEY", "").strip()
    primary_model = os.getenv("GEMINI_MODEL", "gemini-3.5-flash").strip()
    fallback_model = os.getenv("GEMINI_FALLBACK_MODEL", "gemini-3.1-flash-lite").strip()
    gemini_timeout = float(os.getenv("GEMINI_TIMEOUT_SECONDS", "10.0"))

    if not api_key or api_key == "my_api_key":
        return fallback, "template"

    # Build priority model list, excluding deprecated models
    candidate_models = []
    for m in [primary_model, fallback_model, "gemini-3.5-flash", "gemini-3.1-flash-lite", "gemini-3.8-flash", "gemini-flash-latest"]:
        if m and m not in candidate_models and m != "gemini-2.5-flash":
            candidate_models.append(m)

    # Inject conversation history if available
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

    for selected_model in candidate_models:
        url = (
            "https://generativelanguage.googleapis.com/v1beta/models/"
            f"{selected_model}:generateContent?key={api_key}"
        )
        try:
            request = UrlRequest(url, data=body, headers={"Content-Type": "application/json"}, method="POST")
            with urlopen(request, timeout=gemini_timeout) as response:
                result = json.loads(response.read().decode("utf-8"))
            candidate = result["candidates"][0]
            parts = candidate.get("content", {}).get("parts", [])
            text = "".join(p.get("text", "") for p in parts).strip()
            if text:
                append_session_turn(session_id, message, text)
                return text, "gemini"
        except HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="replace")[:300]
            print(f"[Gemini] Model {selected_model} unavailable: HTTP {exc.code}: {detail}", flush=True)
        except (URLError, TimeoutError, KeyError, IndexError, ValueError) as exc:
            print(f"[Gemini] Model {selected_model} unavailable: {exc}", flush=True)

    return fallback, "template"


def get_smart_fallback_and_suggestions(
    message: str,
    recommendation: dict[str, Any],
    lang: str,
    history: list[dict[str, str]],
) -> tuple[str, list[str]]:
    """Determine domain-appropriate fallback advisory and follow-up suggestions."""
    raw = message.strip().lower()
    norm = re.sub(r"[\s-]+", "", raw)
    normalized_spaced = re.sub(r"\s+", " ", raw)

    # 1. Sugarcane Definition
    if (
        re.search(r"\bwhat(?:'s| is)\s+(?:suger|sugar)cane\b", raw) is not None
        or re.search(r"\b(?:suger|sugar)cane\s+meaning\b", raw) is not None
        or "whatissugercane" in norm
        or "whatissugarcane" in norm
    ):
        text = {
            "en": "Sugarcane is a tall tropical grass grown mainly for its sweet juice, which is processed into sugar and other products. It needs warm weather, sunlight, and carefully managed water.",
            "hi": "गन्ना एक लंबी उष्णकटिबंधीय घास है जिसे मुख्य रूप से मीठे रस के लिए उगाया जाता है। इसी रस से चीनी और अन्य उत्पाद बनाए जाते हैं। इसे गर्म मौसम, धूप और सही जल प्रबंधन की आवश्यकता होती है।",
            "mr": "ऊस हे एक उष्णकटिबंधीय गवत वर्गातील पीक आहे जे प्रामुख्याने साखरेसाठी पिकवले जाते. याला उबदार हवामान, सूर्यप्रकाश आणि पाण्याचे योग्य नियोजन लागते.",
        }.get(lang, "Sugarcane is a tall tropical grass grown mainly for its sweet juice, which is processed into sugar and other products.")
        suggestions = {
            "en": ["When can I harvest sugarcane?", "How much water does sugarcane need?", "Leaves are turning yellow, why?"],
            "hi": ["गन्ने की कटाई कब करें?", "गन्ने को कितने पानी की आवश्यकता होती है?", "पत्तियां पीली क्यों हो रही हैं?"],
        }.get(lang, ["When can I harvest sugarcane?", "How much water does sugarcane need?"])
        return text, suggestions

    # 2. Plant Definition
    if re.search(r"\bwhat(?:'s| is) (?:a )?plant\b|\bplant meaning\b", normalized_spaced):
        text = {
            "en": "A plant is a living organism that usually grows in soil, uses sunlight to make food, and needs water, air, and nutrients.",
            "hi": "पौधा एक जीवित organism है जो सामान्यतः मिट्टी में बढ़ता है और भोजन बनाने के लिए सूर्यप्रकाश का उपयोग करता है। उसे पानी, हवा और पोषक तत्वों की आवश्यकता होती है।",
        }.get(lang, "A plant is a living organism that grows and needs water, air, and nutrients.")
        suggestions = {
            "en": ["What are sugarcane growth stages?", "How do roots absorb nutrients?"],
            "hi": ["गन्ने की बढ़वार की अवस्थाएं क्या हैं?", "जड़ें पोषक तत्व कैसे लेती हैं?"],
        }.get(lang, ["What are sugarcane growth stages?"])
        return text, suggestions

    # 3. Software / Non-agricultural queries
    if "docker compose" in raw or "docker-compose" in raw:
        return "I can answer sugarcane and crop-management questions. Docker Compose is a software deployment command, not an agricultural question.", []

    # 4. Harvesting / Cutting Sugarcane
    harvest_keywords = ["cut", "harvest", "cutting", "maturity", "कटाई", "काटना", "कापणी", "કાપણી"]
    if any(k in raw for k in harvest_keywords) and ("cane" in raw or "suger" in raw or "sugar" in raw or "crop" in raw or "गन्न" or "ऊस" in raw or "શેરડી" in raw or "when" in raw):
        text = {
            "en": "Sugarcane is ready to cut (harvest) typically 10 to 14 months after planting (or 11 to 12 months for ratoon crops). Look for maturity signs: bottom leaves dry up, stalks become firm and make a metallic ring when tapped, and juice Brix reads 18–20%. Always cut stalks flush with ground level to maximize sugar yield and ensure healthy ratoon regrowth.",
            "hi": "गन्ने की कटाई आमतौर पर रोपाई के 10 से 14 महीने बाद (और पेड़ी में 11 से 12 महीने बाद) की जाती है। परिपक्वता के मुख्य संकेत: निचली पत्तियां सूखने लगें, तना सख्त हो जाए और थपथपाने पर धातु जैसी खनक आए, तथा ब्रिक्स (मिठास) 18–20% हो। हमेशा गन्ने को जमीन की सतह से सटाकर काटें ताकि अधिक चीनी मिले और पेड़ी अच्छी फूटे।",
            "mr": "ऊस तोडणी सामान्यतः लागवडीनंतर 10 ते 14 महिन्यांनी (आणि खोडवा 11 ते 12 महिन्यांनी) केली जाते. पक्वतेची लक्षणे: खालची पाने वाळणे, कांड्या टणक होणे आणि ब्रिक्स (साखरेचे प्रमाण) 18-20% असणे. ऊस नेहमी जमिनीलगत कापावा जेणेकरून जास्तीत जास्त साखर मिळते.",
            "gu": "શેરડીની કાપણી સામાન્ય રીતે વાવણી પછી 10 થી 14 મહિને (અને પેડી શેરડી 11 થી 12 મહિને) કરવામાં આવે છે. પરિપક્વતાની નિશાનીઓ: નીચેના પાંદડા સૂકવવા લાગે, સાંઠો કઠણ બને અને બ્રિક્સ 18-20% થાય. હંમેશા જમીનને અડીને શેરડી કાપવી.",
        }.get(lang, "Sugarcane is ready to harvest 10 to 14 months after planting when lower leaves dry and juice Brix reaches 18–20%. Cut flush with ground level.")
        suggestions = {
            "en": ["How to measure sugarcane Brix sweetness?", "What time of day is best to cut sugarcane?", "How to care for ratoon crop after cutting?"],
            "hi": ["गन्ने की मिठास (ब्रिक्स) कैसे मापें?", "कटाई का सबसे अच्छा समय क्या है?", "कटाई के बाद पेड़ी फसल की देखभाल कैसे करें?"],
        }.get(lang, ["How to measure sugarcane Brix?", "How to care for ratoon crop?"])
        return text, suggestions

    # 5. Yellow leaves / Chlorosis
    if ("yellow" in raw or "chlorosis" in raw or "पीली" in raw or "पिवळी" in raw or "પીળા" in raw) and (
        "leaf" in raw or "leaves" in raw or "पत्त" in raw or "पान" in raw or "પાંદ" in raw
    ):
        text = {
            "en": "Yellow leaves can result from nitrogen or iron deficiency, excess water, poor drainage, pests, or root stress. Check whether the soil is waterlogged, inspect the roots and leaf undersides, and use a soil test before applying fertilizer. If yellowing spreads quickly, consult a local agronomist.",
            "hi": "पीली पत्तियां नाइट्रोजन या आयरन की कमी, अधिक पानी, खराब जल निकास, कीट या जड़ों पर तनाव के कारण हो सकती हैं। जलभराव की जांच करें, जड़ों और पत्तियों के नीचे देखें और खाद डालने से पहले मिट्टी की जांच कराएं।",
            "mr": "पाने पिवळी पडणे हे नायट्रोजन किंवा लोहाची कमतरता, जास्त पाणी, पाण्याचा निचरा न होणे किंवा कीड-रोगांमुळे होऊ शकते. जमिनीत पाणी साचले आहे का ते तपासा आणि खत देण्यापूर्वी माती परीक्षण करा.",
            "gu": "પાંદડા પીળા પડવાનું કારણ નાઇટ્રોજન અથવા લોહતત્વની ઉણપ, વધારે પડતું પાણી, નબળો નિકાલ અથવા જીવાત હોઈ શકે છે. જમીનમાં પાણી ભરાયેલું નથી તે તપાસો.",
        }.get(lang, "Yellow leaves may come from nutrient deficiency, excess water, poor drainage, pests, or root stress. Check the soil and plants before applying fertilizer.")
        suggestions = {
            "en": ["What is the issue with yellowing leaves?", "How to treat nitrogen deficiency?", "What are symptoms of sugarcane yellow leaf virus?"],
            "hi": ["पीलापन दूर करने के उपाय क्या हैं?", "नाइट्रोजन की कमी कैसे पहचानें?", "यलो लीफ वायरस के क्या लक्षण हैं?"],
        }.get(lang, ["What is the issue with yellowing leaves?", "How to treat nitrogen deficiency?"])
        return text, suggestions

    # 6. Follow-up / Issue query (e.g., "what is the issue?", "why?", "explain problem")
    issue_queries = ["what is the issue", "what's the issue", "what is the problem", "why", "issue?", "problem?", "क्या समस्या", "काय समस्या"]
    if any(q in raw for q in issue_queries) or (len(raw.split()) <= 4 and ("issue" in raw or "problem" in raw or "reason" in raw)):
        # Check if previous context was yellow leaves
        prev_has_yellow = any("yellow" in h.get("user", "").lower() or "yellow" in h.get("assistant", "").lower() for h in history)
        if prev_has_yellow:
            text = {
                "en": "In yellowing sugarcane, the primary issues to inspect are: 1) Nitrogen deficiency (older lower leaves yellow first), 2) Waterlogging/poor root aeration, or 3) Sugarcane Yellow Leaf Virus (midrib turns bright yellow). Check soil moisture depth and inspect leaf undersides for sucking pests.",
                "hi": "गन्ने में पत्तियों के पीलेपन की मुख्य समस्याएं हैं: 1) नाइट्रोजन की कमी (पुरानी निचली पत्तियां पीली पड़ना), 2) जलभराव या खराब जल निकास (जड़ों में हवा की कमी), या 3) यलो लीफ वायरस (मध्य शिरा का पीला होना)। जड़ क्षेत्र की नमी और पत्तियों की निचली सतह की जांच करें।",
            }.get(lang, "In yellowing sugarcane, check for nitrogen deficiency, waterlogged roots, or yellow leaf virus.")
            suggestions = {
                "en": ["How to fix nitrogen deficiency?", "How to inspect leaf pests?", "When should I irrigate next?"],
                "hi": ["नाइट्रोजन की कमी कैसे दूर करें?", "कीट नियंत्रण कैसे करें?", "अगली सिंचाई कब करें?"],
            }.get(lang, ["How to fix nitrogen deficiency?", "When should I irrigate next?"])
            return text, suggestions

        text = {
            "en": "Common sugarcane issues stem from nutrient imbalances (nitrogen/iron), improper watering, root compaction, or pest attacks like stem borers. Inspect soil moisture, leaf coloration, and stalk health to isolate the cause.",
            "hi": "फसल में आम समस्याएं पोषक तत्वों की कमी, गलत सिंचाई, जलभराव या तना छेदक जैसे कीट हो सकते हैं। समस्या पहचानने के लिए मिट्टी की नमी, पत्तियों का रंग और तने की स्थिति देखें।",
        }.get(lang, "Common sugarcane issues stem from nutrient imbalances, improper moisture, or pest infestation.")
        suggestions = {
            "en": ["How to check field soil moisture?", "When can I harvest sugarcane?", "Leaves are turning yellow, why?"],
            "hi": ["खेत की नमी कैसे जांचें?", "गन्ने की कटाई कब करें?", "पत्तियां पीली क्यों हो रही हैं?"],
        }.get(lang, ["How to check field soil moisture?", "When can I harvest sugarcane?"])
        return text, suggestions

    # 7. Planting / Sowing
    if ("when" in raw or "best time" in raw) and ("plant" in raw or "sow" in raw or "बुवाई" in raw or "लागवड" in raw):
        text = {
            "en": "Plant sugarcane at the locally recommended planting window, usually at the start of a reliable warm season. Choose healthy disease-free setts, ensure the soil has good moisture and drainage, and confirm the exact month with your local agricultural extension service.",
            "hi": "गन्ने की रोपाई स्थानीय अनुशंसित समय पर करें, आमतौर पर गर्म मौसम की स्थिर शुरुआत में। स्वस्थ रोगमुक्त सेट चुनें, मिट्टी में पर्याप्त नमी और अच्छा जल निकास रखें, तथा सही महीने की पुष्टि स्थानीय कृषि विभाग से करें।",
        }.get(lang, "Plant sugarcane during the locally recommended warm-season planting window, using healthy setts and well-drained soil.")
        suggestions = {
            "en": ["How to prepare setts for planting?", "What spacing is best between rows?", "When can I harvest sugarcane?"],
            "hi": ["बुवाई के लिए बीज (सेट) कैसे तैयार करें?", "पंक्तियों में कितनी दूरी रखें?", "गन्ने की कटाई कब करें?"],
        }.get(lang, ["How to prepare setts for planting?", "When can I harvest sugarcane?"])
        return text, suggestions

    # 8. Fertilizer / Nutrients
    if any(k in raw for k in ["fertilizer", "fertiliser", "urea", "dap", "npk", "potash", "खाद", "खत", "ખાતર"]):
        text = {
            "en": "Sugarcane requires balanced N-P-K nutrients. Apply basal phosphorus and potassium during planting, and split nitrogen applications across tillering and formative phases. Avoid excessive nitrogen late in the season to prevent delayed maturity.",
            "hi": "गन्ने में नाइट्रोजन, फास्फोरस और पोटाश का संतुलित उपयोग करें। फास्फोरस बुवाई के समय दें, तथा नाइट्रोजन और पोटाश को कल्ले निकलने और बढ़वार के दौरान किस्तों में डालें। पकने के समय अधिक नाइट्रोजन न दें।",
        }.get(lang, "Sugarcane requires balanced N-P-K nutrients. Split nitrogen across early growth stages.")
        suggestions = {
            "en": ["How much urea per acre for tillering?", "Drip vs flood fertigation?", "When should I irrigate next?"],
            "hi": ["कल्ले निकलने की अवस्था में यूरिया कितना दें?", "ड्रिप से खाद देने का तरीका?", "अगली सिंचाई कब करें?"],
        }.get(lang, ["How much urea per acre?", "When should I irrigate next?"])
        return text, suggestions

    # 9. Irrigation / Water queries
    irrigation_keywords = ["water", "irrigat", "moisture", "flood", "drip", "पानी", "सिंचाई", "पाणी", "સિંચાઈ"]
    is_irrigation_query = any(k in raw for k in irrigation_keywords) or not message.strip()

    if is_irrigation_query:
        text = render_advisory(recommendation, lang=lang)
        suggestions = {
            "en": ["When should I irrigate after rain?", "Drip vs flood irrigation?", "How to check soil moisture?"],
            "hi": ["बारिश के बाद सिंचाई कब करें?", "ड्रिप और फ्लड सिंचाई में क्या अंतर है?", "खेत में नमी की जांच कैसे करें?"],
        }.get(lang, ["When should I irrigate after rain?", "Drip vs flood irrigation?"])
        return text, suggestions

    # 10. General agricultural fallback (not irrigation!)
    general_text = {
        "en": "For optimal sugarcane performance, monitor soil moisture, maintain good field drainage, and inspect regularly for pest or nutrient stresses. Confirm specific agronomic treatments with your local agricultural extension service.",
        "hi": "गन्ने की अच्छी पैदावार के लिए खेत में अच्छा जल निकास रखें, नियमित रूप से नमी की जांच करें और कीट या पोषक तत्वों की कमी पर नजर रखें। किसी भी विशेष उपचार के लिए स्थानीय कृषि अधिकारी से सलाह लें।",
        "mr": "चांगल्या ऊस उत्पादनासाठी शेतात पाण्याचा निचरा चांगला ठेवा, ओलावा तपासा आणि कीड किंवा रोगांची नियमित पाहणी करा.",
    }.get(lang, "For optimal sugarcane performance, monitor soil moisture, drainage, and crop health regularly.")
    suggestions = {
        "en": ["When can I cut my sugarcane?", "Leaves are turning yellow, why?", "How much water does sugarcane need?"],
        "hi": ["गन्ने की कटाई कब करें?", "पत्तियां पीली क्यों हो रही हैं?", "गन्ने को कितने पानी की आवश्यकता होती है?"],
    }.get(lang, ["When can I cut my sugarcane?", "Leaves are turning yellow, why?"])
    return general_text, suggestions


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
    lang = request.lang if request.lang in {"en", "hi", "mr", "gu", "pa", "kn"} else "en"
    history = get_session_history(request.session_id)

    # Compute domain-aware fallback and suggestions
    fallback_text, suggestions = get_smart_fallback_and_suggestions(
        request.message, request.recommendation, lang, history
    )

    # Generate response via Gemini (with multi-model cascade, thinking budget, and session context)
    advisory, source = generate_gemini_advisory(
        request.message,
        request.recommendation,
        lang,
        fallback_text,
        session_id=request.session_id,
    )

    # If Gemini answered, remember this turn in session history if not already recorded
    if source != "gemini":
        append_session_turn(request.session_id, request.message, advisory)

    print(
        f"request_id={http_request.headers.get('X-Request-ID', '-')} "
        f"advisory_source={source}",
        flush=True,
    )

    suggestions_label = "You can ask next" if lang == "en" else "आप आगे यह पूछ सकते हैं"

    return {
        "advisory": advisory,
        "advisory_source": source,
        "suggestions": suggestions,
        "suggestions_label": suggestions_label,
    }
