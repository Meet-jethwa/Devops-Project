# Phase 1 serving-safe pipeline; this copy never imports training frameworks.
"""Serving-safe Phase 1 pipeline; this copy never imports training frameworks.

End-to-End Pipeline for Multilingual Farmer Query Understanding and Advisory Generation.
Flow:
  Query -> Clean & Detect Lang -> Intent Classification -> Slot Extraction
  -> Rule-Based Recommendation (Stub: slots + dummy weather/soil dict)
  -> Advisory Generation
"""

from pathlib import Path
import hashlib
import re
import joblib
import numpy as np

try:
    from .gazetteer import pre_label_query, word2features
    from .templates import render_advisory
except ImportError:
    from gazetteer import pre_label_query, word2features
    from templates import render_advisory


# Dummy environmental sensor context stub (NOT a complex agronomic simulation)
DUMMY_AGRI_CONTEXT = {
    "soil_moisture_pct": 22.0,      # e.g., 22% indicates low/moderate moisture in sandy loam
    "rain_expected_24h": False,    # weather forecast API stub
    "temperature_c": 33.5,
    "district": "Belagavi"
}


def detect_language(text: str) -> str:
    """Detect supported Indic text without importing the training cleaner."""
    if not isinstance(text, str) or not text.strip():
        return "en"
    if any("\u0900" <= char <= "\u097f" for char in text):
        return "hi"
    return "en"


def normalize_text(text: str, lang: str = "en") -> str:
    """Apply the serving subset of the existing query normalization behavior."""
    normalized = re.sub(r"https?://\S+|www\.\S+", " ", str(text))
    normalized = re.sub(r"\+?\d[\d\s().-]{7,}\d", " ", normalized)
    normalized = re.sub(r"([!?.,])\1+", r"\1", normalized)
    normalized = re.sub(r"\s+", " ", normalized).strip().lower()
    if lang == "hi":
        normalized = re.sub(r"\s+([?,.!;:])", r"\1", normalized)
    return normalized


class AdvisoryPipeline:
    def __init__(self, config_path: str = "config.yaml"):
        self.project_root = Path(__file__).resolve().parent
        self.results_dir = self.project_root / "models"

        # 1. Load Intent Model (MaxEnt baseline or BiLSTM)
        self.intent_model = None
        maxent_path = self.results_dir / "baseline_maxent_model.joblib"
        if maxent_path.exists():
            try:
                self.intent_model = joblib.load(maxent_path)
                print(f"[Pipeline] Loaded MaxEnt intent model from {maxent_path}")
            except Exception as e:
                print(f"[Pipeline] Could not load intent model: {e}")

        # 2. Load Slot Tagger (CRF)
        self.crf_model = None
        crf_path = self.results_dir / "crf_slot_tagger.joblib"
        if crf_path.exists():
            try:
                self.crf_model = joblib.load(crf_path)
                print(f"[Pipeline] Loaded CRF slot model from {crf_path}")
            except Exception as e:
                print(f"[Pipeline] Could not load CRF model: {e}")

    def clean_query(self, raw_query: str, language: str = None) -> tuple:
        if language is not None:
            requested_lang = str(language).lower()
            lang = requested_lang if requested_lang in {"en", "hi", "mr", "gu", "pa", "kn"} else "en"
        else:
            lang = detect_language(raw_query)
        cleaned = normalize_text(raw_query, lang=lang)
        return cleaned, lang

    def predict_intent(self, cleaned_query: str) -> tuple:
        """Predict intent and confidence."""
        if self.intent_model is not None and cleaned_query:
            try:
                probs = self.intent_model.predict_proba([cleaned_query])[0]
                classes = self.intent_model.classes_
                best_idx = np.argmax(probs)
                return classes[best_idx], float(probs[best_idx])
            except Exception:
                pass

        # Robust heuristic fallback if model is not yet trained
        q_lower = cleaned_query.lower()
        if any(w in q_lower for w in ["water", "irrigation", "सिंचाई", "पानी", "drip", "ड्रिप"]):
            return "Water Management", 0.85
        elif any(w in q_lower for w in ["fertilizer", "fertiliser", "urea", "खाद", "उर्वरक", "यूरिया"]):
            return "Fertilizer Use", 0.82
        elif any(w in q_lower for w in ["disease", "pest", "रोग", "कीट", "दीमक", "borer"]):
            return "Plant Protection", 0.80
        elif any(w in q_lower for w in ["price", "rate", "भाव", "दाम", "mandir"]):
            return "Market Information", 0.75
        return "General Query", 0.60

    def extract_slots(self, raw_query: str) -> dict:
        """Extract domain slots using CRF or gazetteer."""
        tokens, gazetteer_tags = pre_label_query(raw_query)
        tags = gazetteer_tags

        if self.crf_model is not None and tokens:
            try:
                features = [word2features(tokens, i) for i in range(len(tokens))]
                tags = self.crf_model.predict([features])[0]
            except Exception as e:
                tags = gazetteer_tags

        # Group BIO tags into structured dictionary
        slots = {}
        curr_slot = None
        curr_tokens = []

        for tok, tag in zip(tokens, tags):
            if tag.startswith("B-"):
                if curr_slot:
                    slots[curr_slot] = " ".join(curr_tokens)
                curr_slot = tag[2:]
                curr_tokens = [tok]
            elif tag.startswith("I-") and curr_slot == tag[2:]:
                curr_tokens.append(tok)
            else:
                if curr_slot:
                    slots[curr_slot] = " ".join(curr_tokens)
                    curr_slot = None
                    curr_tokens = []

        if curr_slot:
            slots[curr_slot] = " ".join(curr_tokens)

        return slots

    def rule_based_recommendation(self, intent: str, slots: dict, context: dict = None, query_text: str = "") -> dict:
        """
        Rule-based decision stub combining extracted slots and environmental context.
        NOT a complex crop simulator; structured heuristic stub per project specifications.
        """
        if context is None:
            context = DUMMY_AGRI_CONTEXT

        query_lower = query_text.lower()
        rain_terms = ["rain", "rainfall", "after rain", "बारिश", "वर्षा"]
        fertilizer_terms = ["fertilizer", "fertiliser", "urea", "dap", "npk", "खाद", "उर्वरक", "यूरिया"]
        rain = context.get("rain_expected_24h", False) or any(term in query_lower for term in rain_terms)
        soil_m = context.get("soil_moisture_pct", 25.0)

        # Parse duration if provided in slots (e.g. '3 hours' -> 3)
        duration = 3
        if "DURATION" in slots:
            m = re.search(r"\d+", slots["DURATION"])
            if m:
                duration = min(max(int(m.group()), 1), 6)

        # Determine when
        when = "morning"
        if "TIME" in slots:
            t = slots["TIME"].lower()
            if "कल" in t or "tomorrow" in t:
                when = "tomorrow"
            elif "शाम" in t or "evening" in t:
                when = "evening"

        # Action decision rules
        if rain:
            action = "skip_irrigation"
        elif soil_m < 20.0:
            action = "irrigate"
            duration = max(duration, 4)
        elif soil_m > 35.0:
            action = "skip_irrigation"
        else:
            action = "irrigate"

        # Check fertigation requirement
        fertigation = (
            intent.lower() in ["fertilizer use", "fertigation", "nutrient management"]
            or "QUANTITY" in slots
            or any(term in query_lower for term in fertilizer_terms)
        )

        return {
            "action": action,
            "when": when,
            "duration_hours": duration,
            "rain_expected": rain,
            "fertigation": fertigation
        }

    def query_specific_advisory(self, query_text: str, lang: str) -> str | None:
        """Answer common comparison/timing questions that need query context."""
        query_lower = query_text.lower()

        if any(term in query_lower for term in ["what is sugarcane", "what's sugarcane", "sugarcane meaning"]):
            localized = {
                "en": "Sugarcane is a tall tropical grass grown mainly for its sweet juice, which is processed into sugar and other products. It needs warm weather, sunlight, and carefully managed water. Ask me about its crop stages or irrigation needs.",
                "hi": "गन्ना एक लंबी उष्णकटिबंधीय घास है जिसे मुख्य रूप से मीठे रस के लिए उगाया जाता है। इसी रस से चीनी और अन्य उत्पाद बनाए जाते हैं। इसे गर्म मौसम, धूप और सही जल प्रबंधन की आवश्यकता होती है।",
                "mr": "ऊस ही एक उंच उष्णकटिबंधीय गवताची जात आहे. तिच्या गोड रसापासून साखर आणि इतर उत्पादने तयार केली जातात. या पिकाला उबदार हवामान, सूर्यप्रकाश आणि योग्य पाणी व्यवस्थापन आवश्यक असते.",
                "gu": "શેરડી એક ઊંચું ઉષ્ણકટિબંધીય ઘાસ છે, જે મુખ્યત્વે તેના મીઠા રસ માટે ઉગાડવામાં આવે છે. આ રસમાંથી ખાંડ અને અન્ય ઉત્પાદનો બનાવવામાં આવે છે. તેને ગરમ હવામાન, સૂર્યપ્રકાશ અને યોગ્ય પાણી વ્યવસ્થાપનની જરૂર પડે છે.",
                "pa": "ਗੰਨਾ ਇੱਕ ਲੰਮਾ ਗਰਮ ਇਲਾਕਿਆਂ ਵਿੱਚ ਉੱਗਣ ਵਾਲਾ ਘਾਹ ਹੈ। ਇਸ ਦੇ ਮਿੱਠੇ ਰਸ ਤੋਂ ਚੀਨੀ ਅਤੇ ਹੋਰ ਉਤਪਾਦ ਬਣਾਏ ਜਾਂਦੇ ਹਨ। ਇਸ ਨੂੰ ਗਰਮ ਮੌਸਮ, ਧੁੱਪ ਅਤੇ ਠੀਕ ਪਾਣੀ ਪ੍ਰਬੰਧਨ ਦੀ ਲੋੜ ਹੁੰਦੀ ਹੈ।",
                "kn": "ಕಬ್ಬು ಮುಖ್ಯವಾಗಿ ಸಿಹಿಯಾದ ರಸಕ್ಕಾಗಿ ಬೆಳೆಸುವ ಎತ್ತರದ ಉಷ್ಣವಲಯದ ಹುಲ್ಲಾಗಿದೆ. ಈ ರಸದಿಂದ ಸಕ್ಕರೆ ಮತ್ತು ಇತರ ಉತ್ಪನ್ನಗಳನ್ನು ತಯಾರಿಸಲಾಗುತ್ತದೆ. ಇದಕ್ಕೆ ಬೆಚ್ಚಗಿನ ವಾತಾವರಣ, ಸೂರ್ಯಪ್ರಕಾಶ ಮತ್ತು ಸರಿಯಾದ ನೀರಿನ ನಿರ್ವಹಣೆ ಅಗತ್ಯವಿದೆ.",
            }
            return localized.get(lang, localized["en"])

        if any(term in query_lower for term in ["drip vs flood", "drip or flood", "drip and flood"]):
            localized = {
                "en": "Drip irrigation delivers water more directly near the roots, while flood irrigation spreads water across the field. Choose based on field layout, soil, and water availability with local agronomist guidance.",
                "hi": "ड्रिप सिंचाई पानी को जड़ों के पास अधिक लक्षित तरीके से देती है, जबकि फ्लड सिंचाई पूरे क्षेत्र में पानी फैलाती है। खेत की बनावट, मिट्टी और उपलब्ध पानी के अनुसार स्थानीय कृषि विशेषज्ञ से विधि चुनें।",
                "mr": "ठिबक सिंचनामुळे पाणी मुळांजवळ अधिक लक्षित पद्धतीने मिळते, तर पाट सिंचनात पाणी संपूर्ण क्षेत्रात पसरते. शेताची रचना, माती आणि उपलब्ध पाण्यानुसार स्थानिक कृषी तज्ज्ञांच्या सल्ल्याने पद्धत निवडा.",
                "gu": "ડ્રિપ સિંચાઈ પાણી મૂળની નજીક વધુ લક્ષિત રીતે પહોંચાડે છે, જ્યારે ફ્લડ સિંચાઈ સમગ્ર ખેતરમાં પાણી ફેલાવે છે. ખેતરની રચના, જમીન અને ઉપલબ્ધ પાણીના આધારે સ્થાનિક કૃષિ નિષ્ણાતની સલાહ લો.",
                "pa": "ਡ੍ਰਿਪ ਸਿੰਚਾਈ ਪਾਣੀ ਨੂੰ ਜੜ੍ਹਾਂ ਦੇ ਨੇੜੇ ਵਧੇਰੇ ਨਿਸ਼ਾਨੇ ਨਾਲ ਪਹੁੰਚਾਉਂਦੀ ਹੈ, ਜਦਕਿ ਹੜ੍ਹ ਸਿੰਚਾਈ ਪਾਣੀ ਨੂੰ ਪੂਰੇ ਖੇਤ ਵਿੱਚ ਫੈਲਾਉਂਦੀ ਹੈ। ਖੇਤ ਦੀ ਬਣਤਰ, ਮਿੱਟੀ ਅਤੇ ਉਪਲਬਧ ਪਾਣੀ ਅਨੁਸਾਰ ਸਥਾਨਕ ਖੇਤੀ ਮਾਹਿਰ ਦੀ ਸਲਾਹ ਲਓ.",
                "kn": "ಡ್ರಿಪ್ ನೀರಾವರಿ ನೀರನ್ನು ಬೇರುಗಳ ಬಳಿ ಹೆಚ್ಚು ನೇರವಾಗಿ ನೀಡುತ್ತದೆ, ಆದರೆ ಫ್ಲಡ್ ನೀರಾವರಿ ಹೊಲದಾದ್ಯಂತ ನೀರನ್ನು ಹರಡುತ್ತದೆ. ಹೊಲದ ವಿನ್ಯಾಸ, ಮಣ್ಣು ಮತ್ತು ಲಭ್ಯವಿರುವ ನೀರಿನ ಆಧಾರದ ಮೇಲೆ ಸ್ಥಳೀಯ ಕೃಷಿ ತಜ್ಞರ ಸಲಹೆ ಪಡೆಯಿರಿ.",
            }
            return localized.get(lang, localized["en"])

        if any(term in query_lower for term in ["urea", "fertilizer", "fertiliser", "dap", "npk", "खाद", "उर्वरक", "यूरिया"]):
            localized = {
                "en": "The right urea or fertilizer amount depends on a soil test, crop stage, and local recommendation. This demo does not prescribe a fixed dose; confirm the amount with a local agronomist and avoid application before heavy rain.",
                "hi": "यूरिया की सही मात्रा मिट्टी की जांच, फसल की अवस्था और स्थानीय सिफारिश पर निर्भर करती है। इस डेमो से निश्चित मात्रा न लें; भारी बारिश से पहले खाद देने से बचें और स्थानीय कृषि विशेषज्ञ से मात्रा की पुष्टि करें।",
                "mr": "युरिया किंवा खताची योग्य मात्रा मातीची तपासणी, पिकाची अवस्था आणि स्थानिक शिफारशीवर अवलंबून असते. या डेमोमधून ठराविक मात्रा घेऊ नका; स्थानिक कृषी तज्ज्ञांकडून खात्री करा आणि मुसळधार पावसापूर्वी खत देणे टाळा.",
                "gu": "યુરિયા અથવા ખાતરની યોગ્ય માત્રા જમીનની તપાસ, પાકની અવસ્થા અને સ્થાનિક ભલામણ પર આધારિત છે. આ ડેમોમાંથી નિશ્ચિત માત્રા ન લો; સ્થાનિક કૃષિ નિષ્ણાતની સલાહ લો અને ભારે વરસાદ પહેલાં ખાતર આપવાનું ટાળો.",
                "pa": "ਯੂਰੀਆ ਜਾਂ ਖਾਦ ਦੀ ਸਹੀ ਮਾਤਰਾ ਮਿੱਟੀ ਦੀ ਜਾਂਚ, ਫਸਲ ਦੇ ਪੜਾਅ ਅਤੇ ਸਥਾਨਕ ਸਿਫਾਰਸ਼ 'ਤੇ ਨਿਰਭਰ ਕਰਦੀ ਹੈ। ਇਸ ਡੈਮੋ ਤੋਂ ਨਿਸ਼ਚਿਤ ਮਾਤਰਾ ਨਾ ਲਓ; ਸਥਾਨਕ ਖੇਤੀ ਮਾਹਿਰ ਨਾਲ ਪੁਸ਼ਟੀ ਕਰੋ ਅਤੇ ਤੇਜ਼ ਮੀਂਹ ਤੋਂ ਪਹਿਲਾਂ ਖਾਦ ਨਾ ਪਾਓ.",
                "kn": "ಯೂರಿಯಾ ಅಥವಾ ಗೊಬ್ಬರದ ಸರಿಯಾದ ಪ್ರಮಾಣವು ಮಣ್ಣಿನ ಪರೀಕ್ಷೆ, ಬೆಳೆಯ ಹಂತ ಮತ್ತು ಸ್ಥಳೀಯ ಶಿಫಾರಸಿನ ಮೇಲೆ ಅವಲಂಬಿತವಾಗಿದೆ. ಈ ಡೆಮೊನಿಂದ ನಿಗದಿತ ಪ್ರಮಾಣವನ್ನು ತೆಗೆದುಕೊಳ್ಳಬೇಡಿ; ಸ್ಥಳೀಯ ಕೃಷಿ ತಜ್ಞರನ್ನು ಸಂಪರ್ಕಿಸಿ ಮತ್ತು ಭಾರಿ ಮಳೆಯ ಮೊದಲು ಗೊಬ್ಬರ ಹಾಕುವುದನ್ನು ತಪ್ಪಿಸಿ.",
            }
            return localized.get(lang, localized["en"])

        if any(term in query_lower for term in ["rain", "rainfall", "after rain", "बारिश", "वर्षा"]):
            localized = {
                "en": "After rain, check moisture in the root zone before irrigating. If the soil is still moist, postpone watering and reassess when the field begins to dry.",
                "hi": "बारिश के बाद जड़ क्षेत्र की मिट्टी में नमी जांचें। मिट्टी अभी नम हो तो सिंचाई टालें और सूखापन दिखने पर ही अगली सिंचाई पर विचार करें।",
                "mr": "पावसानंतर मुळांच्या भागातील मातीचा ओलावा तपासा. माती अजून ओलसर असल्यास सिंचन पुढे ढकला आणि शेत सुकू लागल्यावर पुन्हा तपासा.",
                "gu": "વરસાદ પછી સિંચાઈ કરતા પહેલાં મૂળ વિસ્તારની ભેજ તપાસો. જમીન હજુ ભીની હોય તો સિંચાઈ મુલતવી રાખો અને ખેતર સુકાવા લાગે ત્યારે ફરી તપાસો.",
                "pa": "ਮੀਂਹ ਤੋਂ ਬਾਅਦ ਸਿੰਚਾਈ ਕਰਨ ਤੋਂ ਪਹਿਲਾਂ ਜੜ੍ਹਾਂ ਵਾਲੇ ਖੇਤਰ ਦੀ ਨਮੀ ਜਾਂਚੋ। ਜੇ ਮਿੱਟੀ ਅਜੇ ਵੀ ਗਿੱਲੀ ਹੈ ਤਾਂ ਸਿੰਚਾਈ ਮੁਲਤਵੀ ਕਰੋ ਅਤੇ ਖੇਤ ਸੁੱਕਣਾ ਸ਼ੁਰੂ ਹੋਣ 'ਤੇ ਦੁਬਾਰਾ ਜਾਂਚੋ.",
                "kn": "ಮಳೆಯ ನಂತರ ನೀರಾವರಿ ಮಾಡುವ ಮೊದಲು ಬೇರುಗಳ ಪ್ರದೇಶದ ತೇವಾಂಶವನ್ನು ಪರಿಶೀಲಿಸಿ. ಮಣ್ಣು ಇನ್ನೂ ತೇವವಾಗಿದ್ದರೆ ನೀರಾವರಿಯನ್ನು ಮುಂದೂಡಿ ಮತ್ತು ಹೊಲ ಒಣಗಲು ಪ್ರಾರಂಭಿಸಿದಾಗ ಮತ್ತೆ ಪರಿಶೀಲಿಸಿ.",
            }
            return localized.get(lang, localized["en"])

        if any(term in query_lower for term in [
            "irrigat", "water", "watering", "सिंचाई", "पानी", "सिंचन", "पाणी",
            "સિંચાઈ", "પાણી", "ਸਿੰਚਾਈ", "ਪਾਣੀ", "ನೀರಾವರಿ", "ನೀರು"
        ]):
            localized = {
                "en": "Check moisture in the root zone before irrigating. Water when the soil begins to dry, then run the system only long enough to wet the root zone without runoff. The correct runtime depends on your soil, field area, and pump or emitter flow, so do not use a fixed three-hour schedule.",
                "hi": "सिंचाई से पहले जड़ क्षेत्र की मिट्टी की नमी जांचें। मिट्टी सूखने लगे तभी पानी दें और बहाव हुए बिना जड़ क्षेत्र को गीला करने जितनी देर ही सिंचाई करें। सही अवधि मिट्टी, खेत के क्षेत्रफल और पंप या ड्रिप प्रवाह पर निर्भर करती है; तीन घंटे का निश्चित समय न अपनाएं।",
                "mr": "सिंचनापूर्वी मुळांच्या भागातील मातीचा ओलावा तपासा. माती सुकू लागल्यावरच पाणी द्या आणि पाणी वाहून जाणार नाही इतपतच मुळांचा भाग ओला करा. योग्य वेळ माती, शेताचे क्षेत्रफळ आणि पंप किंवा ठिबक प्रवाहावर अवलंबून असतो; तीन तासांचा ठराविक वेळ वापरू नका.",
                "gu": "સિંચાઈ કરતા પહેલાં મૂળ વિસ્તારની જમીનની ભેજ તપાસો. જમીન સુકાવા લાગે ત્યારે જ પાણી આપો અને પાણી વહી ન જાય તે રીતે મૂળ વિસ્તાર ભીનો થાય એટલો જ સમય સિંચાઈ કરો. યોગ્ય સમય જમીન, ખેતરનું ક્ષેત્રફળ અને પંપ અથવા ડ્રિપના પ્રવાહ પર આધારિત છે; ત્રણ કલાકનો નિશ્ચિત સમય ન રાખો.",
                "pa": "ਸਿੰਚਾਈ ਤੋਂ ਪਹਿਲਾਂ ਜੜ੍ਹਾਂ ਵਾਲੇ ਖੇਤਰ ਦੀ ਮਿੱਟੀ ਦੀ ਨਮੀ ਜਾਂਚੋ। ਮਿੱਟੀ ਸੁੱਕਣ ਲੱਗੇ ਤਾਂ ਹੀ ਪਾਣੀ ਦਿਓ ਅਤੇ ਪਾਣੀ ਵਗਣ ਤੋਂ ਬਿਨਾਂ ਜੜ੍ਹਾਂ ਵਾਲਾ ਖੇਤਰ ਗਿੱਲਾ ਹੋਣ ਤੱਕ ਹੀ ਸਿੰਚਾਈ ਕਰੋ। ਸਹੀ ਸਮਾਂ ਮਿੱਟੀ, ਖੇਤ ਦੇ ਰਕਬੇ ਅਤੇ ਪੰਪ ਜਾਂ ਡ੍ਰਿਪ ਦੇ ਵਹਾਅ ਉੱਤੇ ਨਿਰਭਰ ਕਰਦਾ ਹੈ; ਤਿੰਨ ਘੰਟਿਆਂ ਦਾ ਨਿਸ਼ਚਿਤ ਸਮਾਂ ਨਾ ਰੱਖੋ।",
                "kn": "ನೀರಾವರಿ ಮಾಡುವ ಮೊದಲು ಬೇರುಗಳ ಪ್ರದೇಶದ ಮಣ್ಣಿನ ತೇವಾಂಶವನ್ನು ಪರಿಶೀಲಿಸಿ. ಮಣ್ಣು ಒಣಗಲು ಪ್ರಾರಂಭಿಸಿದಾಗ ಮಾತ್ರ ನೀರು ನೀಡಿ ಮತ್ತು ನೀರು ಹರಿದುಹೋಗದಂತೆ ಬೇರುಗಳ ಪ್ರದೇಶ ತೇವವಾಗುವಷ್ಟು ಮಾತ್ರ ನೀರಾವರಿ ಮಾಡಿ. ಸರಿಯಾದ ಅವಧಿಯು ಮಣ್ಣು, ಹೊಲದ ವಿಸ್ತೀರ್ಣ ಮತ್ತು ಪಂಪ್ ಅಥವಾ ಡ್ರಿಪ್ ಹರಿವಿನ ಮೇಲೆ ಅವಲಂಬಿತವಾಗಿದೆ; ಮೂರು ಗಂಟೆಗಳ ನಿಗದಿತ ಅವಧಿಯನ್ನು ಬಳಸಬೇಡಿ.",
            }
            return localized.get(lang, localized["en"])

        return None

    def process(self, query: str, context: dict = None, language: str = None) -> dict:
        """Execute full end-to-end processing pipeline."""
        cleaned_q, lang = self.clean_query(query, language=language)
        intent, conf = self.predict_intent(cleaned_q)
        slots = self.extract_slots(query)
        record = self.rule_based_recommendation(intent, slots, context, query_text=cleaned_q)
        paraphrase_idx = int(hashlib.sha256(cleaned_q.encode("utf-8")).hexdigest(), 16)
        advisory = self.query_specific_advisory(cleaned_q, lang) or render_advisory(
            record, lang=lang, paraphrase_idx=paraphrase_idx
        )

        return {
            "raw_query": query,
            "cleaned_query": cleaned_q,
            "language": lang,
            "intent": intent,
            "confidence": conf,
            "slots": slots,
            "structured_record": record,
            "advisory": advisory
        }
